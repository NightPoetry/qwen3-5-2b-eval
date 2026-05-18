"""知识节点：风格一致性 — 生成代码的命名/缩进/格式统一。"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def execute(ctx: dict) -> dict:
    """检查并修复代码风格不一致。"""
    js = ctx.get("js", "")
    if not js:
        return ctx

    fixes = []

    # 检查缩进一致性：混合tab和space
    has_tabs = "\t" in js
    has_spaces = re.search(r'^  \S', js, re.MULTILINE) is not None
    if has_tabs and has_spaces:
        js = js.replace("\t", "  ")
        fixes.append("统一缩进为2空格")

    # 检查引号一致性：单引号 vs 双引号（JS优先单引号）
    single_count = js.count("'") - js.count("\\'")
    double_count = js.count('"') - js.count('\\"')
    # 如果双引号明显多于单引号且不在HTML字符串中
    # 不自动修复引号，只标记
    if double_count > single_count * 2:
        fixes.append("建议统一使用单引号(JS惯例)")

    # 检查分号一致性
    lines_with_semi = len(re.findall(r';\s*$', js, re.MULTILINE))
    lines_without = len(re.findall(r'[^;{}\s/]\s*$', js, re.MULTILINE))
    if lines_with_semi > 0 and lines_without > lines_with_semi:
        fixes.append("分号使用不一致（部分有部分无）")

    if fixes:
        ctx["js"] = js
        ctx.setdefault("_style_fixes", []).extend(fixes)

    return ctx


node = Node(
    id="210",
    name="风格一致性",
    trigger={"type": "key_exists", "key": "js"},
    execute=execute,
    refs=[],
    metadata={"source": "编程规范/代码风格一致性", "category": "code_quality"},
)
