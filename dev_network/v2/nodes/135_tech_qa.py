"""知识节点：技术问答——回答编程/技术相关的纯知识问题。

当用户问"怎么做X""为什么Y""X和Y的区别"等技术问题时，
直接用LLM回答，不进入代码生成管线。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

QA_WORDS = ["怎么", "如何", "为什么", "什么是", "区别", "对比",
            "原理", "原因", "方法", "最佳实践", "推荐"]

def execute(ctx: dict) -> dict:
    if ctx.get("_chat_response"):
        return ctx
    task = ctx.get("task", "")
    if not any(w in task for w in QA_WORDS):
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
    trigger={"type": "keyword", "target": "task",
             "keywords": QA_WORDS},
    execute=execute, refs=["Y20"],
    metadata={"category": "quality"})
