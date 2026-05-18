"""知识节点：结构主义推理 — 最少前提推出最多结论。

非代码生成节点。用于Phase0交互设计时，帮助系统判断：
  - 用户需求中哪些是真需求，哪些是可从已有推出的
  - 功能列表中哪些可以合并为同一机制
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask


def execute(ctx: dict) -> dict:
    """对交互列表做结构化精简：合并同类、消除冗余。"""
    interactions = ctx.get("interactions", "")
    if not interactions:
        return ctx

    lines = [l.strip() for l in interactions.strip().split("\n") if l.strip()]
    if len(lines) <= 3:
        return ctx  # 已经够精简

    # 让模型做一件简单的事：标记哪些行描述的是同一个操作
    merged = ask(
        "你是分析师。找出下面交互列表中描述相同功能的行，合并它们。",
        (f"交互列表：\n{interactions}\n\n"
         "规则：如果两行描述的是同一个用户动作（比如'点击添加'和'按Enter添加'），"
         "合并成一行。输出合并后的列表，每行一个动作。"),
        temperature=0.0,
        max_tokens=200
    )

    if merged and len(merged.strip().split("\n")) < len(lines):
        ctx["interactions_merged"] = merged
        ctx.setdefault("_reasoning", []).append(
            f"交互精简: {len(lines)}条 → {len(merged.strip().split(chr(10)))}条"
        )

    return ctx


node = Node(
    id="130",
    name="结构化精简",
    trigger={"type": "key_exists", "key": "interactions"},
    execute=execute,
    refs=["Y30"],
    metadata={"source": "理解/最少前提", "category": "reasoning"},
)
