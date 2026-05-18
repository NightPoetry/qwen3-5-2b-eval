"""记忆节点：三层缓存检索 + Walnut 边图 + 渐进降级。

三层缓存:
  L1: 锚点→边遍历 (O(1)入口 + 多跳扩展，最快)
  L2: bigram搜索 + 概括记忆 (毫秒级)
  L3: 全盘扫描 (秒级，需用户确认)

Walnut 边图:
  - 锚点(anchor): query_hash → 入口chunk (O(1)跳转)
  - 边(edge): chunk ↔ chunk (共同检索过的chunk互相连边)
  - 遍历: 从锚点出发，沿边走2跳，收集相关chunk
  - 每次成功检索都写边，图越用越密

渐进降级: depth 0→1→2→3，追问时 LLM 精炼查询(evolve_query)
"""
import hashlib
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

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
    "一句话概括，只陈述事实，不加解释。最多两句话。"
)

CHUNK_SIZE = 4
TOP_K_INITIAL = 7
TOP_K_FOLLOWUP = 14


# ═══ Bigram ═══

def bigrams(text):
    s = text.lower()
    return {s[i:i+2] for i in range(len(s) - 1)}

def bigram_score(query, text):
    qb = bigrams(query)
    if not qb: return 0.0
    return len(qb & bigrams(text)) / len(qb)


# ═══ Walnut 边图 (替代旧指针缓存) ═══

def _qh(query):
    return hashlib.md5(query.strip().encode()).hexdigest()[:8]

def _graph_path(log_path):
    return log_path.replace('.json', '_graph.json')

def load_graph(log_path):
    gp = _graph_path(log_path)
    try:
        if Path(gp).exists():
            return json.loads(Path(gp).read_text())
    except (json.JSONDecodeError, IOError):
        pass
    return {"edges": {}, "anchors": {}}

def save_graph(log_path, graph):
    Path(_graph_path(log_path)).write_text(
        json.dumps(graph, ensure_ascii=False))

def anchor_lookup(query, log_path):
    graph = load_graph(log_path)
    anchor = graph["anchors"].get(_qh(query))
    if anchor:
        anchor["access_count"] = anchor.get("access_count", 0) + 1
        save_graph(log_path, graph)
        return anchor, graph
    return None, graph

def edge_walk(start_ids, graph, max_hops=2):
    """从起点chunk沿边BFS，最多走max_hops跳，返回所有可达chunk id。"""
    visited = set(str(c) for c in start_ids)
    frontier = list(visited)
    for _ in range(max_hops):
        nxt = []
        for cid in frontier:
            for nb in graph["edges"].get(cid, {}).get("targets", []):
                if str(nb) not in visited:
                    visited.add(str(nb))
                    nxt.append(str(nb))
        frontier = nxt
        if not frontier:
            break
    return [int(c) for c in visited if c.isdigit()]

def graph_write(chunk_ids, query, log_path):
    """写入边 + 锚点。共同检索到的chunk互相连边。"""
    graph = load_graph(log_path)
    sids = [str(c) for c in chunk_ids]
    for i, sa in enumerate(sids):
        node = graph["edges"].setdefault(sa, {"targets": [], "access_count": 0})
        node["access_count"] += 1
        for sb in sids[i+1:]:
            if sb not in node["targets"]:
                node["targets"].append(sb)
            nb = graph["edges"].setdefault(sb, {"targets": [], "access_count": 0})
            if sa not in nb["targets"]:
                nb["targets"].append(sa)
    if chunk_ids:
        anchors = graph["anchors"]
        anchors[_qh(query)] = {
            "chunk_id": chunk_ids[0],
            "query": query[:50],
            "access_count": 1,
            "created_at": int(time.time()),
        }
        if len(anchors) > 40:
            trim = sorted(anchors.items(),
                          key=lambda x: x[1].get("access_count", 0))
            for k, _ in trim[:len(anchors) - 30]:
                del anchors[k]
    save_graph(log_path, graph)

def delete_anchor(query, log_path):
    graph = load_graph(log_path)
    graph["anchors"].pop(_qh(query), None)
    save_graph(log_path, graph)


# ═══ 概括记忆 ═══

def load_memories(log_path):
    mp = log_path.replace('.json', '_memories.json')
    try:
        if Path(mp).exists():
            return json.loads(Path(mp).read_text()).get("memories", [])
    except (json.JSONDecodeError, IOError):
        pass
    return []

def save_memories(log_path, memories):
    mp = log_path.replace('.json', '_memories.json')
    Path(mp).write_text(json.dumps({"memories": memories}, ensure_ascii=False))


# ═══ 工具 ═══

def load_chat_log(log_path):
    if not log_path or not Path(log_path).exists(): return None
    try: return json.loads(Path(log_path).read_text())
    except: return None

def make_chunks(chat_log):
    chunks = []
    for i in range(0, len(chat_log), CHUNK_SIZE):
        msgs = chat_log[i:i + CHUNK_SIZE]
        chunks.append({
            "index": i // CHUNK_SIZE,
            "messages": msgs,
            "text": ' '.join(m['content'] for m in msgs),
        })
    return chunks

def chunk_to_lines(chunk):
    return [f"{'用户' if m['role']=='user' else '你'}: {m['content']}"
            for m in chunk["messages"]]


# ═══ 主执行 ═══

def execute(ctx: dict) -> dict:
    if ctx.get("_chat_response"):
        return ctx

    task = ctx.get("task", "")
    log_path = ctx.get("_chat_log_path", "")
    turns = ctx.get("_turns", [])

    # L0: _turns 快速搜索（当前会话内存中，最快）
    if turns and len(turns) >= 4:
        best_i, best_score = -1, 0
        for i, t in enumerate(turns[:-1]):
            if t == task: continue
            s = bigram_score(task, t)
            if s > best_score:
                best_i, best_score = i, s
        if best_score > 0.12 and best_i >= 0:
            lo = max(0, best_i - 1)
            hi = min(len(turns), best_i + 2)
            context_lines = []
            for j in range(lo, hi):
                role = "用户" if j % 2 == 0 else "你"
                context_lines.append(f"{role}：{turns[j][:100]}")
            resp = ask(
                "用户问起之前聊过的事。根据下面的对话记录，准确告诉用户。\n"
                "只说记录里有的内容，不要编造。如果记录里没有，说'我不记得了'。",
                f"记录：\n{chr(10).join(context_lines)}\n\n用户问：{task}",
                temperature=0.3, max_tokens=80).strip()
            ctx["_chat_response"] = resp
            ctx["_recall_depth"] = 1
            return ctx

    chat_log = load_chat_log(log_path)
    if not chat_log or len(chat_log) < 2:
        return ctx

    is_followup = (any(w in task for w in FOLLOWUP_WORDS)
                   and ctx.get("_recall_depth", 0) > 0)
    summary_challenged = (is_followup and ctx.get("_recall_used_summary")
                          and any(w in task for w in ["不对", "不是", "不全", "漏了"]))

    chunks = make_chunks(chat_log)

    # ════════ L1: 锚点 → 边遍历 (O(1) + 多跳) ════════
    if not is_followup and not summary_challenged:
        anchor, graph = anchor_lookup(task, log_path)
        if anchor:
            start = [anchor["chunk_id"]]
            walked_ids = edge_walk(start, graph, max_hops=2)
            l1_chunks = [c for c in chunks if c["index"] in walked_ids]
            if l1_chunks:
                lines = [f"[L1·边遍历·{len(walked_ids)}chunks]"]
                for c in sorted(l1_chunks, key=lambda c: c["index"]):
                    lines.extend(chunk_to_lines(c))
                ctx["_recalled"] = {"found": True, "chunks": lines,
                                    "source": "L1_edge_walk", "depth": 0}
                resp = ask(SYSTEM_RECALL,
                           f"聊天记录：\n{chr(10).join(lines[-12:])}\n\n用户问：{task}",
                           temperature=0.7, max_tokens=150).strip()
                ctx["_chat_response"] = resp
                ctx["_recall_depth"] = 1
                ctx["_recall_question"] = task
                ctx["_recall_shown"] = [c["index"] for c in l1_chunks]
                ctx["_recall_shown_text"] = "\n".join(lines[:6])
                graph_write([c["index"] for c in l1_chunks], task, log_path)
                return ctx

    # ════════ 状态管理 ════════
    if summary_challenged:
        depth = 3
        delete_anchor(task, log_path)
        memories = load_memories(log_path)
        old_q = ctx.get("_recall_question", "")
        memories = [m for m in memories if m.get("question", "") != old_q]
        save_memories(log_path, memories)
    elif is_followup:
        depth = ctx["_recall_depth"] + 1
    else:
        depth = 0
        ctx["_recall_shown"] = []
        ctx["_recall_used_summary"] = False
        ctx["_recall_question"] = task
    ctx["_recall_depth"] = depth
    shown = set(ctx.get("_recall_shown", []))

    # ════════ L2: 概括记忆 + bigram搜索 ════════
    memories = load_memories(log_path)
    summary_hits = []
    if depth == 0:
        for mem in memories:
            if bigram_score(task, mem.get("content", "")) > 0.15:
                summary_hits.append(mem)

    task_text = task
    if is_followup and not summary_challenged:
        prev = ctx.get("_recall_shown_text", "")
        evolved = ask(
            "用户追问要找更多内容。提取2-3个最关键的搜索词（空格分隔）。只回答关键词。",
            f"原始问题：{ctx.get('_recall_question', task)}\n"
            f"已找到：{prev[:200]}\n追问：{task}",
            max_tokens=20).strip()
        if evolved and len(evolved) > 1:
            task_text = evolved

    for c in chunks:
        c["score"] = bigram_score(task_text, c["text"])
    ranked = sorted(chunks, key=lambda c: c["score"], reverse=True)
    ranked = [c for c in ranked if task not in c["text"]]
    unshown = [c for c in ranked if c["index"] not in shown and c["score"] > 0.05]

    # ════════ L3: 全盘扫描 (depth≥2) ════════
    top_k = len(unshown) if depth >= 2 else (TOP_K_FOLLOWUP if depth == 1 else TOP_K_INITIAL)
    top = unshown[:top_k]

    if not top:
        if depth >= 3:
            ctx["_chat_response"] = "我仔细翻遍了全部聊天记录，确定没有你说的这个内容。"
        elif depth >= 2:
            ctx["_chat_response"] = "我已经翻遍了全部聊天记录，没有找到更多相关内容了。"
        elif depth == 1:
            ctx["_chat_response"] = "目前找到的就是这些。如果你觉得不全，我可以再仔细找一遍。"
        else:
            return ctx
        ctx["_recall_depth"] = 0
        ctx["_recall_shown"] = []
        return ctx

    new_shown = shown | {c["index"] for c in top}
    ctx["_recall_shown"] = list(new_shown)

    recalled_lines = []
    if summary_hits:
        ctx["_recall_used_summary"] = True
        for mem in summary_hits:
            recalled_lines.insert(0, f"[概括记忆]: {mem['content']}")
    else:
        ctx["_recall_used_summary"] = False
    for c in top:
        recalled_lines.extend(chunk_to_lines(c))
    ctx["_recall_shown_text"] = "\n".join(recalled_lines[:6])

    ctx["_recalled"] = {
        "found": True, "chunks": recalled_lines, "depth": depth,
        "showing": len(top),
        "remaining": len(unshown) - len(top) if depth < 2 else 0,
        "source": f"L{'3' if depth >= 2 else '2'}_bigram",
    }

    context_str = "\n".join(recalled_lines)
    remaining = ctx["_recalled"]["remaining"]
    is_full = depth >= 2 and remaining == 0

    if depth >= 3:
        system, prompt = SYSTEM_FULLSCAN, f"全部记录（确定版）：\n{context_str}\n\n用户问：{task}"
    elif depth >= 2:
        system, prompt = SYSTEM_FULLSCAN, f"全部记录：\n{context_str}\n\n用户问：{task}"
    elif depth >= 1:
        system, prompt = SYSTEM_PARTIAL, f"补充记录：\n{context_str}\n\n用户问：{task}"
    else:
        system, prompt = SYSTEM_RECALL, f"聊天记录：\n{context_str}\n\n用户问：{task}"

    resp = ask(system, prompt, temperature=0.7, max_tokens=150).strip()

    if remaining > 0:
        resp += "（还有更多相关内容，需要我继续说吗？）"
    elif is_full:
        resp += "（全部记录已检索完毕。）"

    ctx["_chat_response"] = resp
    if depth == 0 and top:
        depth = 1
    ctx["_recall_depth"] = depth

    # 写边图：本次共同检索到的chunk互相连边
    hit_ids = [c["index"] for c in top]
    if hit_ids:
        graph_write(hit_ids, ctx.get("_recall_question", task), log_path)

    # 概括记忆（深度≥2时提炼）
    if 2 <= depth < 3 and top and len(chat_log) >= 4:
        try:
            summary = ask(SYSTEM_SUMMARIZE,
                          f"聊天记录：\n{chr(10).join(recalled_lines[-20:])}\n"
                          f"用户关心：{task}",
                          temperature=0.3, max_tokens=100).strip()
            if summary and len(summary) > 3:
                memories.append({"type": "summary", "content": summary,
                                 "question": task})
                seen = set()
                deduped = []
                for m in memories:
                    k = m["content"][:20]
                    if k not in seen:
                        seen.add(k)
                        deduped.append(m)
                save_memories(log_path, deduped[-10:])
        except Exception:
            pass

    return ctx


node = Node(
    id="880", name="记忆检索",
    trigger={"type": "keyword", "target": "task",
             "keywords": RECALL_WORDS + FOLLOWUP_WORDS},
    execute=execute, refs=["Y10"],
    metadata={"category": "chat"})
