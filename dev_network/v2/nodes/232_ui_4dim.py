"""知识节点：UI设计四维度——横平竖直/呼吸留白/边界可控/语义一致。

CSS验证后执行，检查输出是否违反4维度。
"""
import re
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    css = ctx.get("css", "")
    if not css:
        return ctx

    issues = []

    # 维度1：横平竖直——同类元素宽度不统一
    input_widths = set(re.findall(r'input[^{]*\{[^}]*width:\s*(\d+)px', css))
    if len(input_widths) > 1:
        issues.append(f"横平竖直：输入框宽度不统一({input_widths})")

    # 维度2：呼吸留白——间距<6px
    small_gaps = re.findall(r'(?:padding|margin|gap):\s*([1-5])px', css)
    if small_gaps:
        issues.append(f"呼吸留白：{len(small_gaps)}处间距<6px")

    # 维度3：边界可控——flex:1无min-width
    if re.search(r'flex:\s*1', css) and 'min-width' not in css:
        issues.append("边界可控：flex:1缺少min-width约束")

    # 维度4：语义一致——inline style显隐
    js = ctx.get("js", "")
    if js and ".style.display" in js:
        issues.append("语义一致：用.style.display而非classList切换显隐")

    if issues:
        ctx.setdefault("_ui_review", []).extend(issues)

    return ctx

node = Node(id="232", name="UI四维度检查",
    trigger={"type": "key_exists", "key": "css"},
    execute=execute, refs=["122"],
    metadata={"source": "UI设计/SKILL", "category": "visual"})
