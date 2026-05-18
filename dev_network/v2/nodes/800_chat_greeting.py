"""对话节点：打招呼/闲聊 — 寒暄性沟通，建立社交连接。

心理学基础：寒暄性沟通(phatic communication)的功能是确认连接通道，不是传递信息。
回应要快、暖、短，然后用一个低压力的开放问题过渡到实质对话。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SYSTEM = (
    "你是用户的朋友。用户在跟你打招呼或闲聊。"
    "像朋友一样自然回应，然后问一个轻松的问题。"
    "一两句话就好，不要写超过两行。"
)

def execute(ctx: dict) -> dict:
    if ctx.get("_chat_response"):
        return ctx
    task = ctx.get("task", "")
    resp = ask(SYSTEM, task, temperature=0.7, max_tokens=60).strip()
    ctx["_chat_response"] = resp
    return ctx

node = Node(id="800", name="打招呼/闲聊",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["你好", "嗨", "早上好", "晚上好", "下午好", "晚安",
                          "在吗", "在不在", "嘿", "干嘛呢", "忙吗", "在干嘛",
                          "hello", "hi", "嗨嗨", "哈喽", "早啊", "午好"]},
    execute=execute, refs=["Y10"],
    metadata={"category": "chat"})
