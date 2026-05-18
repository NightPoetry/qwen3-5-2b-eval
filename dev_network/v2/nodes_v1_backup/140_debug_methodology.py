"""知识节点：调试方法论 — 当生成的代码有问题时的诊断策略。

用于迭代修复阶段：验证失败后，系统按此方法论诊断根因。
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


# 常见错误模式及其根因映射
ERROR_PATTERNS = {
    "getElementById.*null": "HTML中缺少对应ID的元素，或JS在DOM加载前执行",
    "is not defined": "变量/函数未定义——可能模型输出了不完整代码",
    "Cannot read prop": "对null/undefined取属性——通常是querySelector返回null",
    "Unexpected token": "JSON解析错误或语法错误——检查模型是否输出了markdown标记",
    "SyntaxError": "JS语法错误——检查是否有未闭合的括号/引号",
}


def execute(ctx: dict) -> dict:
    """扫描生成代码中的潜在运行时错误模式。"""
    js = ctx.get("js", "")
    html = ctx.get("html", "")
    if not js:
        return ctx

    potential_issues = []

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

    if potential_issues:
        ctx.setdefault("_warnings", []).extend(potential_issues)

    return ctx


node = Node(
    id="140",
    name="代码诊断",
    trigger={"type": "key_exists", "key": "js"},
    execute=execute,
    refs=[],
    metadata={"source": "knowledge/debugging-methodology", "category": "quality"},
)
