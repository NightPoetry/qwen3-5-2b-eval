"""知识节点：资源预算守门 — 五维度双层防线。

长跑全权限系统必须有显式预算：
  五维度：LLM成本 / 磁盘 / CPU / 网络 / 时间
  双层防线：软警告(提醒可决定) + 硬上限(拒绝执行)

关键：
  - 实时拦截不是事后审计（钱烧完才发现=没用）
  - 软停必须真的停（阻塞等用户输入，不是悄悄通知后继续）
  - 硬上限不能去掉，只能调大
  - 大额操作必须告知估算（>$0.10需确认，>$1需关键词确认）
  - 超估算30%中途暂停询问继续
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

BUDGET_SYSTEM = """You are a resource budget advisor. Apply these principles:

FIVE DIMENSIONS (all independent, must all be managed):
1. LLM cost: retry loops / reset cycles can burn $X00 overnight
2. Disk: audit/log without rotation -> disk full -> system down
3. CPU: subprocess deadlock / infinite loop -> CPU 100%
4. Network: pulling large models/deps without limit -> bandwidth exceeded
5. Time: LLM hang / subprocess won't exit -> task stuck forever

TWO-LAYER DEFENSE (missing either = failure):
- Soft warning: notify, user decides (but must truly block, not "notify and continue")
- Hard limit: refuse execution (can only be raised, never removed)

RECOMMENDED THRESHOLDS (personal developer local agent):
- LLM session: warn $1, hard $5
- LLM daily: warn $10, hard $50
- LLM monthly: warn $100, hard $300
- Audit total: warn 5GB, hard 20GB
- Single tool CPU: warn 30s, hard 5min
- Single LLM call: warn 60s, hard 5min
- Single subprocess: hard 10min

REAL-TIME INTERCEPTION (not post-audit):
- check_before: operation initiated -> budget check -> Proceed/SoftWarn/SoftStop/HardStop
- record_after: operation completed -> accumulate actual consumption
- Post-audit is useless: money already spent when discovered

LARGE OPERATION DISCLOSURE:
- Before trigger: show estimate (call_count * avg_cost * unit_price = $X)
- Estimate > $0.10: explicit 'y' confirm
- Estimate > $1: keyword input gate ("I confirm")
- Actual > estimate by 30%: pause mid-way + ask to continue

ANTI-PATTERNS:
- Only warnings no hard limits (user misses one = budget blown)
- Post-audit only (money gone)
- Soft stop that doesn't truly stop
- Large operations without disclosure
- Hard limit that can be eliminated (misconfiguration = no protection)
- Retries not counted in budget

Given the scenario, recommend budget dimensions and thresholds."""


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    advice = ask(
        BUDGET_SYSTEM,
        f"Resource scenario: {task[:300]}",
        max_tokens=150
    ).strip()
    ctx["_budget_advice"] = advice
    ctx.setdefault("_design_principles", []).extend([
        "五维度预算：LLM成本/磁盘/CPU/网络/时间，互不替代",
        "双层防线：软警告+硬上限，缺一不可",
        "实时拦截不是事后审计",
        "大额操作必须告知估算",
    ])
    return ctx

node = Node(id="999", name="资源预算守门",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["预算", "成本", "资源", "限制", "配额", "超时",
                          "budget", "cost", "limit", "quota", "timeout"]},
    execute=execute, refs=["430"],
    metadata={"source": "Guild/资源预算守门原则", "category": "safety"})
