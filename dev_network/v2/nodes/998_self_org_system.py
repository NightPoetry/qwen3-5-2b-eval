"""知识节点：自组织系统设计 — 权重权力机制+反固化+知识流转。

核心理念：让系统自组织/自架构，建立高效反馈机制。

权重权力机制：
  权重 = 成功率 x log2(总经验数+1)，无上限
  高权重者可力压群雄（防多数人愚蠢）
  错误决策按权重比例惩罚（防少数人独裁）

投票机制：
  总同意权重 > 70%总权重 -> 通过
  知识上传：个人知识->投票->职位层->投票->公司层

知识三层抽象：
  经验(具体案例，客观保留) -> 知识(共性，不变条件和不变结果) -> 理解(推理规则，最少假设推导)

反固化：
  决策时权重越高出问题时承担权重越高
  投票同意错误知识->按权重比例惩罚
  投票反对错误知识->权重不变(鼓励审慎)
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SELFORG_SYSTEM = """You are a self-organizing system designer. Apply these principles:

WEIGHT-POWER MECHANISM:
- Weight = success_rate * log2(total_experience + 1). No upper limit.
- High-weight individuals can overrule majority (prevents mob stupidity)
- Errors penalized proportional to weight (prevents tyranny of few)
- Decision weight high -> error responsibility high (responsibility = power)

VOTING MECHANISM:
- Approval threshold: total approving weight > 70% of total weight
- Knowledge escalation: personal -> team vote -> role level -> company vote -> company level
- Responsibility tracing: voted for wrong knowledge -> penalty proportional to weight
- Voted against wrong knowledge -> no penalty (encourages caution)

KNOWLEDGE THREE-LAYER ABSTRACTION:
- Experience: specific cases with preconditions, preserved objectively
- Knowledge: commonalities, invariant conditions and invariant results
- Understanding: inference rules, minimum assumptions to maximum deductions

ANTI-OSSIFICATION:
- No permanent authority (capabilities become outdated, rapid elimination)
- No majority tyranny (competent individuals guide direction)
- Responsibility equals power (higher weight = higher stakes)
- Dynamic adjustment (weight reflects real capability)

FAILURE SEVERITY:
- Critical (project delay/failure): -2.0 weight
- Moderate (functional defect, medium fix): -1.0 weight
- Minor (small issue, quick fix): -0.5 weight

Given the organizational/system design question, apply self-organization principles."""


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    advice = ask(
        SELFORG_SYSTEM,
        f"System design question: {task[:300]}",
        max_tokens=150
    ).strip()
    ctx["_selforg_advice"] = advice
    return ctx

node = Node(id="998", name="自组织系统设计",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["权重", "投票", "自组织", "反馈机制", "知识管理",
                          "权限", "角色", "escalat", "weight", "vote"]},
    execute=execute, refs=["Y20"],
    metadata={"source": "Guild/自组织系统+权重权力+知识流转", "category": "architecture"})
