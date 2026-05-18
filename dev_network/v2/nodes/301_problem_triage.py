"""知识节点：问题三分——真问题/伪问题/工程问题。

当分析/推理完成后，对剩余问题做分类。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

def execute(ctx: dict) -> dict:
    reasoning = ctx.get("_reasoning")
    if not reasoning:
        return ctx

    restated = reasoning.get("restated", "")
    if not restated:
        return ctx

    classification = ask(
        "将这个问题分类为以下之一。只回答分类名：真问题 / 伪问题 / 工程问题",
        (f"问题：{restated}\n\n"
         "真问题=需要新理论/新方法才能解决\n"
         "伪问题=换个角度看就消解了\n"
         "工程问题=理论已有，缺实现/数据/实验"),
        max_tokens=20
    ).strip()

    reasoning["classification"] = classification
    ctx["_reasoning"] = reasoning
    return ctx

node = Node(id="301", name="问题三分",
    trigger={"type": "key_exists", "key": "_reasoning"},
    execute=execute, refs=["Y30"],
    metadata={"source": "理解/六步法", "category": "reasoning"})
