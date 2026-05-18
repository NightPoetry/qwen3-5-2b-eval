"""节点：CSS验证修复 + 知识卡001(flex防溢出)。"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Node


def execute(ctx: dict) -> dict:
    raw = ctx.get("raw_css", "")
    issues = []

    # 去 markdown
    if "```" in raw:
        blocks = re.findall(r'```(?:\w+)?\n(.*?)```', raw, re.DOTALL)
        if blocks:
            raw = blocks[0]

    # 去文件名
    lines = raw.split("\n")
    if lines and lines[0].strip().endswith(".css"):
        raw = "\n".join(lines[1:])
        issues.append("移除开头文件名")

    # HTML混入检测
    if "<html" in raw or "<body" in raw:
        issues.append("CSS混入HTML(无法自动修复)")

    # [知识卡001] flex防溢出
    blocks = re.findall(r'([^{}]+)\{([^}]*)\}', raw)
    for selector, body in blocks:
        if re.search(r'flex:\s*1', body) and 'min-width' not in body:
            old = f"{selector}{{{body}}}"
            new_body = body.rstrip() + "\n  min-width: 0;\n  overflow: hidden;\n"
            raw = raw.replace(old, f"{selector}{{{new_body}}}", 1)
            issues.append(f"flex防溢出({selector.strip()})")

    ctx["css"] = raw
    ctx["css_issues"] = issues
    return ctx


node = Node(
    id="071",
    name="CSS验证+知识卡",
    trigger={"type": "key_exists", "key": "raw_css"},
    execute=execute,
    refs=["080", "120", "121", "122"],
)
