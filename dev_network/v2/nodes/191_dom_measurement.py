"""知识节点：DOM测量断言 — 验证CSS变量/尺寸/色值正确性。"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def execute(ctx: dict) -> dict:
    """检查CSS中是否有不一致的值（同面板控件尺寸不同等）。"""
    css = ctx.get("css", "")
    if not css:
        return ctx

    # 提取所有width声明，检查同类元素是否统一
    width_declarations = re.findall(r'([\w#.:-]+)\s*\{[^}]*width:\s*(\d+)px', css)

    # 按相似选择器分组检查一致性
    input_widths = set()
    button_widths = set()
    for selector, width in width_declarations:
        if "input" in selector.lower():
            input_widths.add(int(width))
        if "btn" in selector.lower() or "button" in selector.lower():
            button_widths.add(int(width))

    warnings = []
    if len(input_widths) > 1:
        warnings.append(f"输入框宽度不统一: {input_widths}")
    if len(button_widths) > 1:
        warnings.append(f"按钮宽度不统一: {button_widths}")

    if warnings:
        ctx.setdefault("_warnings", []).extend(warnings)

    return ctx


node = Node(
    id="191",
    name="DOM尺寸一致性",
    trigger={"type": "key_exists", "key": "css"},
    execute=execute,
    refs=["Y20"],
    metadata={"source": "GUI前端集成验证工程师/DOM测量", "category": "verification"},
)
