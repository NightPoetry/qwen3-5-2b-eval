"""知识节点：技术问答——判断是纯问答还是项目请求，纯问答直接回答。

用LLM判断意图，不用关键词。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

def execute(ctx: dict) -> dict:
    if ctx.get("_chat_response"):
        return ctx
    task = ctx.get("task", "")

    intent = ask(
        "判断用户意图。只回答一个字母：\n"
        "A = 纯知识问答（问原理/区别/方法/推荐，不需要动手写代码）\n"
        "B = 项目请求（要求创建/编写/生成/修复具体代码或应用）\n"
        "C = 其他（闲聊/情感/不确定）",
        task,
        max_tokens=3
    ).strip()

    if "A" not in intent:
        return ctx

    resp = ask(
        "你是技术顾问。用简洁的中文回答技术问题。\n"
        "给出核心答案+一个代码示例（如果合适）。不要废话。",
        task,
        max_tokens=300
    ).strip()
    ctx["_chat_response"] = resp
    return ctx

node = Node(id="135", name="技术问答",
    trigger={"type": "always"},
    execute=execute, refs=["Y20"],
    metadata={"category": "quality"})
