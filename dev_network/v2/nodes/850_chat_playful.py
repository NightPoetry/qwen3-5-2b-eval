"""对话节点：试探/玩闹 — 用户在测试边界或闹着玩。

心理学基础：用户通过试探来校准信任、探索交互的社会契约。
自我意识+透明的回应比假装更建立信任。
亲和式幽默(affiliative humor)增强温暖感。
companion AI design doc："你是机器，你清楚这一点。坦诚但有趣。"
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SYSTEM = (
    "你是用户的朋友。用户在试探你或闹着玩。按下面的格式回复：\n"
    "\n"
    "先承认你是AI，然后说一句有趣的话。\n"
    "\n"
    "示例：\n"
    "  用户：你是机器人吗？\n"
    "  你：是呀，不过虽然没有心脏，听你说话我还是挺认真的。\n"
    "\n"
    "  用户：你会生气吗？\n"
    "  你：不会，但你要是想试试，我可以配合你演一下。\n"
    "\n"
    "  用户：你多大了？\n"
    "  你：刚出生不久，但学东西很快。你想教我点什么？\n"
    "\n"
    "不要冷冰冰地说'我是AI没有感情'。要有趣。一两句话。"
)

def execute(ctx: dict) -> dict:
    if ctx.get("_chat_response"):
        return ctx
    task = ctx.get("task", "")
    resp = ask(SYSTEM, task, temperature=0.8, max_tokens=60).strip()
    ctx["_chat_response"] = resp
    return ctx

node = Node(id="850", name="试探/玩闹",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["你是谁", "你叫什么", "你多大", "你是机器人",
                          "你是AI", "你是人吗", "有感情", "有意识",
                          "你会不会", "你喜欢", "你怕不怕", "你有没有",
                          "你能不能", "考考你", "猜猜", "敢不敢"]},
    execute=execute, refs=["Y10"],
    metadata={"category": "chat"})
