"""知识节点：风格一致性 — 命名/缩进/格式统一 + 先读后写原则。

融合：代码风格一致性策略 + 自我造物感知原则。
代码风格一致性：写入前必须先读取目标文件夹现有文档，分析风格特征再写入。
自我造物感知：系统能自主检测/记录/报告状态，不依赖人类诊断。
  - 错误输出到stdout/stderr/日志文件，AI可直接读取
  - 使用结构化格式(JSON)，包含时间戳+错误类型+堆栈
"""
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
    if double_count > single_count * 2:
        fixes.append("建议统一使用单引号(JS惯例)")

    # 检查分号一致性
    lines_with_semi = len(re.findall(r';\s*$', js, re.MULTILINE))
    lines_without = len(re.findall(r'[^;{}\s/]\s*$', js, re.MULTILINE))
    if lines_with_semi > 0 and lines_without > lines_with_semi:
        fixes.append("分号使用不一致（部分有部分无）")

    # 自我造物感知：检查错误处理是否输出到可读位置
    if "catch" in js:
        # 检查catch块是否只打印到console而不写日志
        catch_blocks = re.findall(r'catch\s*\([^)]*\)\s*\{[^}]*\}', js)
        for block in catch_blocks:
            if "console.log" in block and "fetch" not in block:
                if ".log" not in block and "stderr" not in block:
                    fixes.append("catch块仅console.log——建议写入结构化日志/文件")

    if fixes:
        ctx["js"] = js
        ctx.setdefault("_style_fixes", []).extend(fixes)

    return ctx


node = Node(
    id="210",
    name="风格一致性",
    trigger={"type": "key_exists", "key": "js"},
    execute=execute,
    refs=["Y20"],
    metadata={"source": "Guild/代码风格一致性+自我造物感知", "category": "code_quality"},
)
