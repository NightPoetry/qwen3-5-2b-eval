"""知识节点：理论纯净不等于删参数 — 消除机制前先理解其功能。

核心：消除任何"看似多余"的机制前，先回答"删除它哪些场景会变差"。
三类辨识：
  A类(真冗余)->应删  B类(补偿性失真)->修根因后才能删  C类(合法功能)->不能删
功能性参数(温度/学习率)不是超参，是政策选择旋钮。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

PURITY_SYSTEM = """You are a mechanism analysis advisor. When someone wants to remove a "seemingly redundant" mechanism, apply this framework:

BEFORE REMOVING ANY MECHANISM X:
- Ask: "If X is removed, which scenarios get worse?" Cannot answer = don't understand it = FORBIDDEN to remove.

THREE TYPES:
- Type A (true redundancy): function derivable from basics, no scenario changes when removed, historical legacy. OK to remove.
- Type B (compensatory distortion): looks like a hack (empirical value, softening, compensation). Direct removal = lose compensation, problem returns. MUST fix root cause first, verify compensation no longer needed, THEN remove.
- Type C (legitimate function): carries function NOT derivable from basic principles. Removal degrades specific scenarios. CANNOT remove.

DECISION FLOW:
1. "Remove X, which scenarios get worse?" -> Can't answer -> forbidden
2. Those scenarios are real needs? -> Yes = Type C -> keep
3. Can root cause be fixed? -> No = Type C -> keep; Yes = Type B -> fix root cause first
4. After fixing root cause, X truly not needed? -> Yes = Type A -> remove; No = Type C misdiagnosed -> keep

COMMON MISTAKES:
- Removing temperature -> in-context anchoring lost (Type C, not a hack)
- Removing retry -> intermittent network failures exposed
- Removing backend validation -> trust boundary broken (frontend bypass)
- Removing hyperparameter -> optimal range for task/scale lost

Given the mechanism under consideration, classify it as A/B/C and recommend action."""


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    analysis = ask(
        PURITY_SYSTEM,
        f"Mechanism under consideration: {task[:300]}",
        max_tokens=150
    ).strip()
    ctx["_purity_analysis"] = analysis
    ctx.setdefault("_design_principles", []).extend([
        "看似多余!=真多余。删除前先理解它承担什么功能",
        "答不出删除后哪里变差=不懂它=禁止删除",
        "A真冗余/B补偿性(修根因后删)/C合法功能(不能删)",
        "功能性参数(温度/lr)是政策选择旋钮，不是超参",
    ])
    return ctx

node = Node(id="990", name="理论纯净判断",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["删除", "移除", "去掉", "简化", "精简", "冗余", "多余",
                          "remove", "simplify", "redundant"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "Guild/理论纯净不等于删参数", "category": "quality"})
