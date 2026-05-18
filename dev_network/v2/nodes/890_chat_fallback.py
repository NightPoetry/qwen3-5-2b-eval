"""对话节点：兜底对话 — 纯工作记忆，不依赖聊天历史。

光标定位 + task + 工作记忆 = 足够判断上下文。
聊天记录由 app.py 存储，只在回忆节点(880)触发时检索。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

TECHNICAL_KEYS = [
    "_creative_output", "_reasoning", "_fix_steps", "_debug",
    "contract", "_changes", "_word_method", "_disambiguated",
    "_domain_rules", "raw_html", "raw_css", "raw_js",
]

SYSTEM_FIRST = (
    "你是用户的朋友。自然地回应用户说的话。"
    "简短、真诚、有温度。一两句话。"
    "如果不确定用户想聊什么，可以友好地问一下。"
)

SYSTEM_CONTINUE = (
    "你是用户的朋友，你们正在聊天。\n"
    "根据之前的对话自然地接着聊。不要跳到新话题。\n"
    "简短、真诚。一两句话。不要用emoji。"
)

SYSTEM_RECALL = (
    "你是用户的朋友。用户在回忆之前聊过的内容。\n"
    "根据下面给出的聊天记录片段，自然地回应用户。\n"
    "简短、真诚。一两句话。"
)


def execute(ctx: dict) -> dict:
    if ctx.get("_chat_response"):
        return ctx

    turns = ctx.get("_turns", [])
    in_conversation = len(turns) >= 2

    if not in_conversation:
        if any(ctx.get(k) for k in TECHNICAL_KEYS):
            return ctx

    task = ctx.get("task", "")

    recalled = ctx.get("_recalled")
    if recalled and recalled.get("found"):
        context_str = "\n".join(recalled.get("chunks", [])[-6:])
        prompt = f"聊天记录片段：\n{context_str}\n\n用户现在说：{task}"
        system = SYSTEM_RECALL
    elif in_conversation:
        # 利用光标位置来判断上下文方向，但不带聊天历史
        cursor = ctx.get("_cursor", [])
        cursor_hint = ""
        if cursor:
            cursor_hint = f"（你们刚才的话题方向是：{'→'.join(cursor[-3:])}）\n"
        prompt = f"{cursor_hint}用户说：{task}"
        system = SYSTEM_CONTINUE
    else:
        prompt = task
        system = SYSTEM_FIRST

    resp = ask(system, prompt, temperature=0.7, max_tokens=100).strip()
    ctx["_chat_response"] = resp
    return ctx


node = Node(id="890", name="通用对话",
    trigger={"type": "regex", "target": "task",
             "pattern": "[\\u4e00-\\u9fff]"},
    execute=execute, refs=["Y10"],
    metadata={"category": "chat"})
