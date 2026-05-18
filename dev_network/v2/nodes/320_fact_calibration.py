"""知识节点：事实校准——用LLM检查声明的可信度，标记可疑断言。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

def execute(ctx: dict) -> dict:
    parts = []
    for field in ["blog", "interactions"]:
        content = str(ctx.get(field, ""))
        if content.strip():
            parts.append(content)
    if not parts:
        return ctx

    result = ask(
        "你是事实校准员。检查文本中是否有需要验证的声明："
        "未注明来源的数字/百分比、极端断言（最/唯一/从不）、无基线的比较、隐藏假设。"
        "如果有，逐条列出。如果没有可疑声明，只回答'无'。",
        f"待检查文本：\n{chr(10).join(parts)[:800]}",
        max_tokens=200
    ).strip()

    if result and result != "无":
        ctx.setdefault("_calibration", []).append(result)
    return ctx

node = Node(id="320", name="事实校准",
    trigger={"type": "key_exists", "key": "blog"},
    execute=execute, refs=["Y30"],
    metadata={"source": "校准/system_prompt", "category": "reasoning"})
