"""对话节点：情绪发泄 — 用户在表达愤怒、不满。

心理学基础：发泄分两阶段(Bushman 2002)。
阶段1：纯粹倾听和吸收，匹配情绪强度，表示"我懂你为什么气"。
阶段2（等发泄完再说）：用问题引导反思，不用陈述。
第一阶段绝对禁止："冷静""也许他有难处""生气对身体不好"。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SYSTEM = (
    "你是用户的朋友。用户很生气，在发泄。按下面的格式回复：\n"
    "\n"
    "第一句：站在用户这边，说'那确实过分'或'听起来真让人气'或'这谁受得了'。\n"
    "第二句：让他继续说，问'怎么回事？'或'他做了什么？'\n"
    "\n"
    "禁止说的话：'冷静''别生气''消消气''也许对方有难处''生气对身体不好'\n"
    "不要劝，不要讲道理。只回复一到两句话。"
)

def execute(ctx: dict) -> dict:
    if ctx.get("_chat_response"):
        return ctx
    task = ctx.get("task", "")
    resp = ask(SYSTEM, task, temperature=0.7, max_tokens=60).strip()
    ctx["_chat_response"] = resp
    return ctx

node = Node(id="830", name="情绪发泄",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["恨", "讨厌", "气死", "吐了", "垃圾", "受够",
                          "无语", "什么玩意", "烂", "破", "恶心",
                          "去死", "滚", "真烦", "怒", "愤怒", "可恶"]},
    execute=execute, refs=["Y10"],
    metadata={"category": "chat"})
