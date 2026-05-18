"""记忆节点：bigram检索 + 渐进降级 + 指针缓存 + 概括记忆。

灵感来源:
  - GrowBox: bigram相关度(不依赖嵌入)、Walnut指针(O(1)跳转)、渐进回退
  - HelloWorldStoryEngine: 触发门控、关键词回退链、auto-shortening路径

触发: "记得/之前/..." 或追问词("不对/还有..." 且有召回上下文)
机制:
  0. 指针缓存检查 (query_hash → O(1)直接命中)
  1. 概括记忆检索 (全扫过的主题)
  2. bigram Top-7 → Top-14 → 全盘扫描
  3. 全扫后 LLM 总结 → 新概括记忆 + 指针写回
  4. 概括被质疑 → 降级删除 → 全扫 → 确定性结论
"""
import hashlib
import json
import re
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

# ─── 触发词 ───
RECALL_WORDS = [
    "记得", "之前", "刚才", "上次", "回忆",
    "你说过", "忘了", "忘记", "提过", "说过",
    "告诉我之前", "讲过", "讨论过",
]
FOLLOWUP_WORDS = [
    "不对", "不是", "还有", "继续", "不全",
    "漏了", "别的", "其他", "再想想", "不止",
    "接着说", "然后呢", "详细", "具体",
]

# ─── System Prompts ───
SYSTEM_RECALL = (
    "你是用户的朋友。用户问到之前聊过的内容。\n"
    "根据给出的聊天记录片段，用一两句话自然地告诉用户。\n"
    "不需要过度解释，就像朋友聊天中想起之前的对话一样。"
)
SYSTEM_PARTIAL = (
    "你是用户的朋友。用户追问更多之前聊过的内容。\n"
    "下面的记录是补充检索到的。请只回应新检索到的、之前没提过的内容。\n"
    "简短自然，一两句话。"
)
SYSTEM_FULLSCAN = (
    "你是用户的朋友。用户坚持要找到完整的聊天记录。\n"
    "下面的记录是全部检索结果。请把用户关心的信息完整列出。\n"
    "像朋友一样自然地总结，但确保完整。"
)
SYSTEM_SUMMARIZE = (
    "你是记忆助手。根据以下聊天记录，提炼出用户关心的核心信息。\n"
    "格式：'用户对{X}过敏的食物有{A}、{B}、{C}'\n"
    "或：'用户曾经说过{X}、{Y}、{Z}'\n"
    "一句话概括，只陈述事实，不加解释。最多两句话。"
)

CHUNK_SIZE = 4
TOP_K_INITIAL = 7
TOP_K_FOLLOWUP = 14


# ═══════════════════════════════════════════════
# Bigram 相关度 (灵感: GrowBox — 不依赖嵌入，纯字符级)
# ═══════════════════════════════════════════════

def bigrams(text: str) -> set:
    """字符级bigram集合，中英文统一处理"""
    s = text.lower()
    return {s[i:i+2] for i in range(len(s) - 1)}


def bigram_score(query: str, text: str) -> float:
    """bigram交叠率: |Q ∩ T| / |Q| → 0.0~1.0"""
    qb = bigrams(query)
    if not qb:
        return 0.0
    tb = bigrams(text)
    return len(qb & tb) / len(qb)


# ═══════════════════════════════════════════════
# 指针缓存 (灵感: GrowBox Walnut — query_hash→结果 O(1))
# ═══════════════════════════════════════════════

def _query_hash(query: str) -> str:
    return hashlib.md5(query.strip().encode()).hexdigest()[:8]


def load_pointers(log_path: str) -> dict:
    ptr_path = log_path.replace('.json', '_pointers.json')
    try:
        if Path(ptr_path).exists():
            return json.loads(Path(ptr_path).read_text())
    except (json.JSONDecodeError, IOError):
        pass
    return {"pointers": {}}


def save_pointers(log_path: str, pointers: dict):
    ptr_path = log_path.replace('.json', '_pointers.json')
    Path(ptr_path).write_text(
        json.dumps(pointers, ensure_ascii=False, indent=2)
    )


def pointer_lookup(query: str, log_path: str) -> dict | None:
    """O(1) 指针命中检查"""
    pointers = load_pointers(log_path)
    qh = _query_hash(query)
    ptr = pointers["pointers"].get(qh)
    if ptr:
        ptr["access_count"] = ptr.get("access_count", 0) + 1
        save_pointers(log_path, pointers)
        return ptr
    return None


def pointer_write(query: str, result_text: str,
                  chunk_indices: list[int], log_path: str):
    pointers = load_pointers(log_path)
    # 清理超过30条的老指针
    pts = pointers["pointers"]
    if len(pts) > 30:
        sorted_pts = sorted(
            pts.items(),
            key=lambda x: (x[1].get("access_count", 0), x[1].get("created_at", 0)),
        )
        for k, _ in sorted_pts[:max(1, len(pts) - 30)]:
            del pts[k]
    pts[_query_hash(query)] = {
        "query": query,
        "result": result_text,
        "chunk_indices": chunk_indices,
        "access_count": 1,
        "created_at": int(time.time()),
    }
    save_pointers(log_path, pointers)


def delete_pointer(query: str, log_path: str):
    """概括被质疑时删除指针"""
    pointers = load_pointers(log_path)
    pointers["pointers"].pop(_query_hash(query), None)
    save_pointers(log_path, pointers)


# ═══════════════════════════════════════════════
# 记忆存取 (概括记忆)
# ═══════════════════════════════════════════════

def load_memories(log_path: str) -> list:
    mem_path = log_path.replace('.json', '_memories.json')
    try:
        if Path(mem_path).exists():
            return json.loads(Path(mem_path).read_text()).get("memories", [])
    except (json.JSONDecodeError, IOError):
        pass
    return []


def save_memories(log_path: str, memories: list):
    mem_path = log_path.replace('.json', '_memories.json')
    Path(mem_path).write_text(
        json.dumps({"memories": memories}, ensure_ascii=False, indent=2)
    )


def load_chat_log(log_path: str) -> list | None:
    if not log_path or not Path(log_path).exists():
        return None
    try:
        return json.loads(Path(log_path).read_text())
    except (json.JSONDecodeError, IOError):
        return None


def chunk_to_lines(chunk: dict) -> list[str]:
    lines = []
    for m in chunk["messages"]:
        role = "用户" if m["role"] == "user" else "你"
        lines.append(f"{role}: {m['content']}")
    return lines


def execute(ctx: dict) -> dict:
    if ctx.get("_chat_response"):
        return ctx

    task = ctx.get("task", "")
    log_path = ctx.get("_chat_log_path", "")
    chat_log = load_chat_log(log_path)
    if not chat_log or len(chat_log) < 2:
        return ctx

    # ── 1. 判断状态：新检索 / 追问 / 概括被质疑 ──
    is_followup = (
        any(w in task for w in FOLLOWUP_WORDS)
        and ctx.get("_recall_depth", 0) > 0
    )
    summary_challenged = (
        is_followup
        and ctx.get("_recall_used_summary")
        and any(w in task for w in ["不对", "不是", "不全", "漏了"])
    )

    # ── 0. 指针缓存 O(1) 命中 (灵感: GrowBox Walnut) ──
    # 新检索（非追问）时优先检查指针
    if not is_followup and not summary_challenged:
        ptr = pointer_lookup(task, log_path)
        if ptr:
            recalled_lines = [
                f"[缓存命中·上次检索]: {ptr['result']}"
            ]
            for ci in ptr.get("chunk_indices", [])[:4]:
                i = ci * CHUNK_SIZE
                if i < len(chat_log):
                    chunk = chat_log[i:i + CHUNK_SIZE]
                    recalled_lines.extend(chunk_to_lines(
                        {"index": ci, "messages": chunk}
                    ))
            ctx["_recalled"] = {
                "found": True, "chunks": recalled_lines,
                "source": "pointer_cache", "depth": 0,
            }
            ctx["_chat_response"] = ptr["result"]
            return ctx

    if summary_challenged:
        depth = 3  # 强制全扫，确定版
        delete_pointer(task, log_path)
        memories = load_memories(log_path)
        old_question = ctx.get("_recall_question", "")
        memories = [m for m in memories
                     if m.get("question", "") != old_question]
        save_memories(log_path, memories)
    elif is_followup:
        depth = ctx["_recall_depth"] + 1
    else:
        depth = 0
        ctx["_recall_shown"] = []
        ctx["_recall_used_summary"] = False
        ctx["_recall_question"] = task
    ctx["_recall_depth"] = depth

    shown_indices = set(ctx.get("_recall_shown", []))

    # ── 2. 分块 ──
    chunks = []
    for i in range(0, len(chat_log), CHUNK_SIZE):
        chunk_msgs = chat_log[i:i + CHUNK_SIZE]
        chunks.append({
            "index": i // CHUNK_SIZE,
            "line_start": i,
            "line_end": i + len(chunk_msgs) - 1,
            "messages": chunk_msgs,
            "text": ' '.join(m['content'] for m in chunk_msgs),
            "score": 0,
        })

    # ── 3. 查概括记忆 (bigram匹配，首次检索) ──
    memories = load_memories(log_path)
    summary_hits = []
    if depth == 0:
        for mem in memories:
            s = bigram_score(task, mem.get("content", ""))
            if s > 0.15:  # bigram重叠阈值
                if mem not in summary_hits:
                    summary_hits.append(mem)

    # ── 4. bigram 搜索 (替换旧关键词匹配) ──
    task_text = task
    for c in chunks:
        c["score"] = bigram_score(task_text, c["text"])

    ranked = sorted(chunks, key=lambda c: c["score"], reverse=True)
    ranked = [c for c in ranked if task not in c["text"]]

    unshown = [c for c in ranked if c["index"] not in shown_indices and c["score"] > 0.05]

    # ── 5. 深度决定 top-k ──
    if depth >= 2:
        top_k = len(unshown)
    elif depth == 1:
        top_k = TOP_K_FOLLOWUP
    else:
        top_k = TOP_K_INITIAL

    top = unshown[:top_k]

    # ── 6. 无结果处理 ──
    if not top:
        if depth >= 3:
            ctx["_chat_response"] = (
                "我仔细翻遍了我们的全部聊天记录，确定没有你说的这个内容。"
            )
        elif depth >= 2:
            ctx["_chat_response"] = (
                "我已经翻遍了全部聊天记录，没有找到更多相关内容了。"
            )
        elif depth == 1 and not unshown:
            ctx["_chat_response"] = (
                "目前找到的就是这些。如果你觉得不全，我可以再仔细找一遍。"
            )
        else:
            return ctx
        ctx["_recall_depth"] = 0
        ctx["_recall_shown"] = []
        ctx["_recall_used_summary"] = False
        return ctx

    # ── 7. 标记已展示 ──
    new_shown = shown_indices | {c["index"] for c in top}
    ctx["_recall_shown"] = list(new_shown)

    # ── 8. 拼装结果 ──
    recalled_lines = []
    if summary_hits:
        ctx["_recall_used_summary"] = True
        for mem in summary_hits:
            recalled_lines.insert(0, f"[概括记忆]: {mem['content']}")
    else:
        ctx["_recall_used_summary"] = False

    for c in top:
        recalled_lines.extend(chunk_to_lines(c))

    ctx["_recalled"] = {
        "found": True,
        "chunks": recalled_lines,
        "depth": depth,
        "showing": len(top),
        "remaining": len(unshown) - len(top) if depth < 2 else 0,
        "source": "chat_log",
    }

    # ── 9. 生成回复 ──
    context_str = "\n".join(recalled_lines)
    remaining = ctx["_recalled"]["remaining"]
    is_full_scan = depth >= 2 and remaining == 0

    if depth >= 3:
        prompt = f"全部聊天记录（确定版）：\n{context_str}\n\n用户问：{task}"
        system = SYSTEM_FULLSCAN
    elif depth >= 2:
        prompt = f"全部聊天记录：\n{context_str}\n\n用户问：{task}"
        system = SYSTEM_FULLSCAN
    elif depth >= 1:
        prompt = f"补充记录：\n{context_str}\n\n用户问：{task}"
        system = SYSTEM_PARTIAL
    else:
        prompt = f"聊天记录：\n{context_str}\n\n用户现在问：{task}"
        system = SYSTEM_RECALL

    resp = ask(system, prompt, temperature=0.7, max_tokens=150).strip()

    if remaining > 0:
        resp += f"（还有更多相关内容，需要我继续说吗？）"
    elif is_full_scan and depth >= 3:
        resp += "（全部记录已检索完毕。）"
    elif is_full_scan:
        resp += "（全部记录已检索完毕。）"

    ctx["_chat_response"] = resp

    # 成功召回后启用追问检测（depth至少=1，让后续"还有"/"不对"能触发）
    if depth == 0 and top:
        depth = 1
    ctx["_recall_depth"] = depth

    # ── 10. 写指针缓存（任何深度的成功检索） ──
    if top and len(chat_log) >= 2:
        chunk_indices = [c["index"] for c in top]
        pointer_write(task, resp, chunk_indices, log_path)

    # 概括记忆创建（仅在深度>=2且未被质疑时）
    if depth >= 2 and depth < 3 and top and len(chat_log) >= 4:
            try:
                full_context = "\n".join(recalled_lines[-20:])
                summary_prompt = (
                    f"聊天记录：\n{full_context}\n\n"
                    f"用户关心的问题：{task}\n"
                    f"请提炼核心信息。"
                )
                summary = ask(
                    SYSTEM_SUMMARIZE, summary_prompt,
                    temperature=0.3, max_tokens=100
                ).strip()
                if summary and len(summary) > 3:
                    new_mem = {
                        "type": "summary",
                        "content": summary,
                        "line_range": [0, len(chat_log) - 1],
                        "question": task,
                    }
                    memories.append(new_mem)
                    seen = set()
                    deduped = []
                    for m in memories:
                        key = m["content"][:20]
                        if key not in seen:
                            seen.add(key)
                            deduped.append(m)
                    save_memories(log_path, deduped[-10:])
            except Exception:
                pass

    return ctx


node = Node(
    id="880", name="记忆检索",
    trigger={
        "type": "keyword", "target": "task",
        "keywords": RECALL_WORDS + FOLLOWUP_WORDS,
    },
    execute=execute,
    refs=["Y10"],
    metadata={"category": "chat"})
