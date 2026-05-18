"""知识节点：破坏性操作确认流程 — 指令完整性+风险分级+安全调试。

融合：指令完整性与风险分级原则 + 安全调试原则 + 破坏性操作指令轨。

风险四级：
  L0安全(ls/SELECT) → L1局部写入 → L2跨界影响 → L3不可逆破坏
  L3必须：二次验证+警示UI+两阶段确认

安全调试边界：
  - 默认只读，写入需隔离环境
  - 备份先行（附RESTORE.md），架构变更需迁移工具
  - 用户数据 > 一切调试便利
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

RISK_ASSESSMENT_SYSTEM = """You are a risk assessment engine. Classify the operation into risk levels:

RISK LEVELS:
- L0 Safe: read-only commands (ls, SELECT, git status). Single parse OK.
- L1 Local write: temp files, dev branch edits. Integrity double-check.
- L2 Cross-boundary: create PR, brew install, global config. Double-check + inform user.
- L3 Irreversible: rm -rf, DROP/TRUNCATE, git push --force, sudo. Double-check + warning UI + two-phase confirm.

TRUNCATION DETECTION (fast path reject):
- rm -rf followed by only whitespace/EOF = truncated (rm needs a target)
- rm -rf / or rm -rf /* = critical: root deletion
- SQL ending with WHERE or unclosed quotes = truncated
- Shell quotes odd count = unclosed
- Command ending with && || | ; \\ = incomplete
- Placeholder {var} not substituted = incomplete

L3 WARNING UI RULES:
1. Warning border color (red/orange) + warning icon
2. Full command displayed verbatim, no abbreviation
3. Impact quantified (file count / rows / size)
4. Explicit irreversibility notice + latest backup location
5. Two-phase confirm: step1 "I see it" -> step2 "I confirm"
6. Step2 button position must NOT overlap step1 (prevent double-click)
7. 3-5 second countdown before clickable (force reading)
8. Critical: require typing confirmation keyword

Given the operation, output: risk level (L0-L3), truncation check result, and required safeguards."""

DESTRUCTIVE_FLOW = [
    {"id": "X01", "name": "识别目标", "action": "列出所有候选，精确定位目标"},
    {"id": "X02", "name": "展示确认", "action": "向用户展示识别结果，等待明确确认"},
    {"id": "X03", "name": "安全准备", "action": "备份+卸载/解锁——为破坏性操作准备环境"},
    {"id": "X04", "name": "执行操作", "action": "执行破坏性操作（可后台运行）"},
    {"id": "X05", "name": "监控完成", "action": "监控exit code/日志确认成功，不盲目假设"},
    {"id": "X06", "name": "审计记录", "action": "写入audit：原始指令+验证链+用户确认事件"},
]

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    ctx["_destructive_flow"] = DESTRUCTIVE_FLOW

    # LLM风险评估
    risk = ask(
        RISK_ASSESSMENT_SYSTEM,
        f"Operation: {task[:300]}",
        max_tokens=120
    ).strip()
    ctx["_risk_assessment"] = risk

    ctx.setdefault("_design_principles", []).extend([
        "风险四级：L0安全/L1局部/L2跨界/L3不可逆，级别越高验证越严",
        "二次验证必须真冗余——独立路径/独立角度/独立校验",
        "L3铁律：警示色+完整指令+量化影响+两阶段确认+倒计时",
        "截断检测：rm无目标/SQL无WHERE/引号奇数/命令未完成=直接拒绝",
        "安全调试：默认只读，备份先行（附RESTORE.md），用户数据>调试便利",
        "破坏性操作：识别→展示→确认→备份→执行→监控→审计",
    ])
    return ctx

node = Node(id="620", name="破坏性操作流程",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["删除", "擦除", "清除", "格式化", "重置", "drop", "rm",
                          "erase", "wipe", "destroy", "force", "sudo"]},
    execute=execute, refs=["330", "470"],
    metadata={"source": "Guild/指令完整性+风险分级+安全调试", "category": "safety"})
