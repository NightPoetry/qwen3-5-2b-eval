"""知识节点：UI设计规范——横平竖直/呼吸留白/边界可控/语义一致/跨系统视觉一致。

检查CSS和HTML输出的视觉规范：对齐、间距、溢出防护、控件统一、禁止emoji字符。
第五维度：UI禁用emoji字符（渲染差异巨大），一律内联SVG。
状态指示放statusbar，由圆点+文字标签+separator组成。
"""
import re
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

UI_ANTI_PATTERNS = [
    "同面板input和toggle裸排不齐→toggle包统一宽度容器",
    "图标菜单用flex不固定图标列→用grid固定列宽",
    "等分按钮用flex被内容撑大→用grid repeat(N,1fr)",
    "inline style='display:none'在WKWebView可能失效→用CSS class切换",
    "可滚动区域无max-height→加max-height+overflow:auto",
    "数字字体不等宽导致宽度抖动→font-variant-numeric: tabular-nums",
    "UI文本用emoji字符→内联SVG（emoji跨系统渲染差异巨大）",
    "状态指示只有圆点无文字→放statusbar，圆点+文字+separator",
    "Tab切换按钮尺寸风格不同→共用class体系+固定height+box-sizing",
]

SPACING_MIN = {
    "section_padding": 12,
    "row_gap": 8,
    "control_gap": 8,
    "panel_margin": 14,
}

def execute(ctx: dict) -> dict:
    css = ctx.get("css", "")
    html = ctx.get("html", "")
    if not css and not html:
        return ctx

    issues = []

    if css:
        # 检查间距<6px
        small_gaps = re.findall(r'(?:padding|margin|gap):\s*([1-5])px', css)
        if small_gaps:
            issues.append(f"呼吸留白：{len(small_gaps)}处间距<6px，最小建议8px")

        # flex:1无min-width
        if re.search(r'flex:\s*1', css) and 'min-width' not in css:
            issues.append("边界可控：flex:1缺少min-width约束，可能被内容撑破")

        # inline style显隐
        js = ctx.get("js", "")
        if js and ".style.display" in js:
            issues.append("语义一致：用.style.display切换显隐→改用classList.toggle")

    if html:
        # 检查emoji字符（Unicode范围）
        emoji_pattern = re.compile(
            '[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F6FF]'
        )
        if emoji_pattern.search(html):
            issues.append("跨系统一致：HTML中包含emoji字符→改用内联SVG")

    if issues:
        ctx.setdefault("_ui_review", []).extend(issues)

    ctx.setdefault("_ui_anti_patterns", []).extend(UI_ANTI_PATTERNS)
    return ctx

node = Node(id="710", name="UI设计规范",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["UI", "界面", "布局", "对齐", "间距", "溢出", "样式",
                          "面板", "控件", "statusbar"]},
    execute=execute, refs=["232", "122"],
    metadata={"source": "Skills/UI设计", "category": "visual"})
