"""知识节点：质量门——蒸馏产出的最终检查，通过才能接入网络。

七项检查全通过才算合格。任何一项不通过，标记需要修正。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

QUALITY_CHECKLIST = [
    "trigger精度：不会在无关任务上误触发",
    "execute单一性：LLM每次只做一件事",
    "判断方式：语义判断用LLM不用regex",
    "refs合理性：只连因果/互补相关节点",
    "脱敏完整：无个人信息/项目名/URL",
    "归并检查：没有与现有节点严重重复",
    "可达性：至少被一个上游节点refs引用",
]

def execute(ctx: dict) -> dict:
    synthesized = ctx.get("_synthesized", {})
    if synthesized.get("action") == "skip":
        ctx["_quality_result"] = {"passed": True, "reason": "skipped (duplicate)"}
        return ctx

    design = synthesized.get("design", "")
    system_prompt = synthesized.get("system_prompt", "")

    review = ask(
        "审查这个节点设计是否满足质量标准：\n"
        + "\n".join(f"{i+1}. {c}" for i, c in enumerate(QUALITY_CHECKLIST))
        + "\n\n回答格式：通过/不通过|原因（如不通过，指出哪项失败）",
        f"节点设计：{design[:400]}\nSystem prompt：{system_prompt[:300]}",
        max_tokens=80
    ).strip()

    passed = "通过" in review and "不通过" not in review
    ctx["_quality_result"] = {
        "passed": passed,
        "review": review,
        "checklist": QUALITY_CHECKLIST,
    }
    return ctx

node = Node(id="729", name="质量门",
    trigger={"type": "key_exists", "key": "_synthesized"},
    execute=execute, refs=["Y30"],
    metadata={"source": "distillation-pipeline/quality", "category": "meta"})
