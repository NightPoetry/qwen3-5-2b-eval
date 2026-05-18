"""知识节点：失效模式与恢复 — 故障树+fail-safe/fail-stop+post-mortem。

核心：复杂系统必有失败。事前列出故障树+决策模式+post-mortem模板。
默认偏好：保护用户数据+保证可溯源 -> 多数偏fail-stop。

五位置故障树：
  A.外部依赖(API故障/限流/下线)
  B.本地存储(DB损坏/磁盘满/文件锁)
  C.子进程(超时/内存爆/死锁)
  D.自身组件(task死锁/递归/panic)
  E.用户输入(红线/截断/Ctrl-C)

fail-stop后：不自动崩溃，停止当前任务->持久化关键状态->flush审计->写post-mortem->等用户。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

FAILURE_SYSTEM = """You are a failure mode analyst. Apply these principles:

FAIL-SAFE vs FAIL-STOP:
- fail-safe: degrade to safe state, continue. Use when: impact limited + has degradation + doesn't break user flow
- fail-stop: stop immediately. Use when: failure may spread / data integrity at risk / needs human intervention
- Default preference: protect user data + ensure traceability -> most cases lean fail-stop

FIVE-POSITION FAULT TREE (every system must have):
A. External dependencies: API failure, rate limit, content rejection, service decommission
B. Local storage: DB corruption, disk full, file lock, NAS disconnect
C. Sub-processes: timeout, OOM, deadlock
D. Own components: task deadlock, recursion, panic
E. User input: red line, truncation, Ctrl-C

For each: Detection -> Blocking -> Recovery -> Mode (fail-safe/fail-stop)

KEY RULES:
- External API: temp unavailable = retry with backoff (fail-safe); content rejection = no retry (fail-stop)
- DB corruption = refuse to continue (fail-stop); audit corruption = refuse to work (fail-stop)
- Sub-process timeout = SIGTERM -> SIGKILL (fail-stop)
- fail-stop behavior: stop tasks -> persist critical state -> flush audit -> write post-mortem -> wait for user
- Unrecoverable last resort: don't write new audit, write CRITICAL.md, dump memory, next start = read-only mode

ANTI-PATTERNS:
- Default panic (loses work)
- Unlimited retry (temp failure -> permanent block)
- Content rejection hard retry (wastes cost)
- Continue after audit corruption (breaks integrity)
- Post-mortem in memory only (lost on crash)

Given the scenario, identify failure position (A-E), recommend fail-safe or fail-stop, and specify recovery path."""


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    analysis = ask(
        FAILURE_SYSTEM,
        f"System scenario: {task[:300]}",
        max_tokens=150
    ).strip()
    ctx["_failure_analysis"] = analysis
    ctx.setdefault("_design_principles", []).extend([
        "故障树覆盖五位置：外部/存储/子进程/自身/用户输入",
        "默认偏fail-stop：保护数据+可溯源",
        "fail-stop后不崩溃：持久化->审计->post-mortem->等用户",
        "审计损坏时拒绝继续工作",
        "不可恢复兜底：CRITICAL.md+dump+下次只读模式",
    ])
    return ctx

node = Node(id="992", name="失效模式分析",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["故障", "失败", "恢复", "异常", "错误处理", "容错",
                          "fallback", "recover", "fail", "crash", "timeout"]},
    execute=execute, refs=["620", "430"],
    metadata={"source": "Guild/失效模式与恢复原则", "category": "safety"})
