"""知识节点：调试方法论 — 假说诊断+闭环调试+安全边界。

融合三套方法论：
1. 假说诊断顺序：先消除已知再判断未知，一次只改一个变量
2. 自主闭环调试：可自视/可远操/可感知/可全知/可封印
3. 安全调试原则：默认只读，隔离环境，备份先行
4. 问题诊断顺序：数据量->多样性->质量->评估->算法
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

DIAGNOSIS_SYSTEM = """You are a debugging methodology advisor. Apply these principles:

HYPOTHESIS DIAGNOSIS ORDER:
- When A and B both exist causing symptom C, eliminate A first, re-test baseline, then judge B
- A+B->C does NOT imply B->C. Never skip the control experiment
- One variable at a time. Re-establish baseline after each fix
- Do NOT do second-order diagnosis on B immediately after fixing A

PROBLEM DIAGNOSIS ORDER (never skip steps):
1. Is data quantity sufficient? (check first)
2. Is data diverse enough?
3. Is data quality OK (noise/pollution)?
4. Is the evaluation metric wrong?
5. Only then consider algorithm/architecture changes

SELF-LOOP DEBUGGING (5 capabilities):
- Observable: system can capture its own output (screenshots, structured logs)
- Controllable: all user interactions can be triggered programmatically
- Perceivable: every operation result is queryable as structured data
- Omniscient: one command returns complete application state snapshot
- Sealable: all debug capabilities can be fully disabled in production

SAFE DEBUGGING BOUNDARIES:
- Default to read-only. Write operations require isolated environment
- Backup before any data modification. Backup must include RESTORE instructions
- User data priority > all debugging convenience
- Service restart = memory state reset. Prefer hot reload over restart
- Architecture changes require migration tools (forward + rollback, idempotent)

Given the user's debugging situation, identify which principle applies and give ONE specific next step."""

# 常见错误模式及其根因映射
ERROR_PATTERNS = {
    "getElementById.*null": "HTML中缺少对应ID的元素，或JS在DOM加载前执行",
    "is not defined": "变量/函数未定义——可能模型输出了不完整代码",
    "Cannot read prop": "对null/undefined取属性——通常是querySelector返回null",
    "Unexpected token": "JSON解析错误或语法错误——检查模型是否输出了markdown标记",
    "SyntaxError": "JS语法错误——检查是否有未闭合的括号/引号",
}


def execute(ctx: dict) -> dict:
    """诊断生成代码问题：静态扫描+LLM方法论判断。"""
    js = ctx.get("js", "")
    html = ctx.get("html", "")
    task = ctx.get("task", "")
    errors = ctx.get("_errors", [])

    potential_issues = []

    if js:
        # 检查JS中引用的ID是否都在HTML中
        js_ids = set(re.findall(r'getElementById\([\'"](\w+)[\'"]\)', js))
        html_ids = set(re.findall(r'id=[\'"](\w+)[\'"]', html))
        missing = js_ids - html_ids
        if missing:
            potential_issues.append(f"JS引用了HTML中不存在的ID: {missing}")

        # 检查是否有裸的script标签残留
        if "<script" in js or "</script>" in js:
            potential_issues.append("JS中残留了<script>标签")

        # 检查未闭合的括号
        opens = js.count("{") + js.count("(") + js.count("[")
        closes = js.count("}") + js.count(")") + js.count("]")
        if abs(opens - closes) > 2:
            potential_issues.append(f"括号不平衡: 开{opens} 闭{closes}")

    # 如果有错误或问题，用LLM给出方法论指导
    if errors or potential_issues:
        problem_desc = "; ".join(
            [str(e) for e in errors] + potential_issues
        )[:200]
        advice = ask(
            DIAGNOSIS_SYSTEM,
            f"Problem: {problem_desc}",
            max_tokens=120
        ).strip()
        ctx["_debug_advice"] = advice

    if potential_issues:
        ctx.setdefault("_warnings", []).extend(potential_issues)

    return ctx


node = Node(
    id="140",
    name="代码诊断",
    trigger={"type": "key_exists", "key": "js"},
    execute=execute,
    refs=["Y30"],
    metadata={"source": "Guild/假说诊断+闭环调试+安全调试", "category": "quality"},
)
