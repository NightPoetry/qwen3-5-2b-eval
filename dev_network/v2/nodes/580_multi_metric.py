"""知识节点：多维指标验收——单指标成功可能是另一维度的退化。

融合：多维指标验收原则 + 操作语义统一原则 + 实验数据归档原则。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

ACCEPTANCE_SYSTEM = """You are a multi-dimensional acceptance reviewer. Apply these principles:

MULTI-METRIC ACCEPTANCE:
- Never judge success by a single metric. Systems have trade-offs
- At least 3 categories: target metric + dual metric (trade-off) + baseline metric + manual sampling
- Any dimension degradation = NOT successful, redesign required
- Improving metric X while optimizing for X is tautology. True validation = other metrics hold
- Checklist: >=3 metrics listed, baseline recorded, all dimensions compared, multi-scenario tested, multiple seeds

OPERATION SEMANTICS UNITY:
- Same operation purpose via ANY trigger path must produce identical effects
- Context fork (different paths assemble different params) = bug
- Behavior asymmetry (path A triggers save, path B doesn't) = bug
- All paths should call the same core function. Trigger method is just an entry point
- New path admission: what is its operation semantics? Does another path exist? Does it reuse core logic?

EXPERIMENT DATA ARCHIVAL:
- Scripts must be self-contained (implement OLD and NEW behavior, don't depend on external code version)
- Raw data preserved unfiltered (full stdout)
- Failed experiments MUST be archived (they prevent re-treading)
- Main code version snapshot bound to experiment
- File naming marks failure clearly: data_xxx_failed.txt, data_xxx_disproved.txt

Given the task, identify which acceptance dimensions to check and give specific checklist items."""


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    dimensions = ask(
        ACCEPTANCE_SYSTEM,
        f"Task to validate: {task[:300]}",
        max_tokens=150
    ).strip()
    ctx["_acceptance_review"] = dimensions
    ctx.setdefault("_design_principles", []).extend([
        "单指标验收等于选择性失明——必须多维交叉验证",
        "至少覆盖：目标维度+对偶维度+基础维度+人工抽样",
        "任何一维度退化=不算成功",
        "同一操作语义的所有触发路径必须产生一致效果",
        "实验脚本自包含+数据原文保存+失败实验也归档",
    ])
    return ctx

node = Node(id="580", name="多维指标验收",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["验收", "评估", "测试", "指标", "性能", "质量"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "Guild/多维指标+操作语义+实验归档", "category": "quality"})
