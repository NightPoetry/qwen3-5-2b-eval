"""知识节点：前端精致感 — 消除廉价感的六维自查。

融合：精致感设计原则 + UI自查清单 + 禁止浏览器原生样式透出 + Flex防溢出。

廉价感六来源：
1. 全局monospace字体（应只用于数值/代码）
2. 10px全大写+超宽字距（2018模板标配，现已过时）
3. 零圆角+硬边框（像电子表格）
4. 荧光色+深黑底（视觉疲劳/游戏HUD感）
5. 拥挤（元素间无呼吸空间）
6. 缺少过渡和状态反馈（界面僵硬）

防御性布局：
- 固定区域flex-shrink-0，可变区域flex-1 min-h-0
- flex-1和minHeight不要同时使用
- 必须始终可见的元素放flex-shrink-0容器
- 固定宽度浮层用min(Npx, 100vw)

原生样式隔离：
- type=number的spinner隐藏或改type=text+inputMode=numeric
- select的原生箭头appearance:none
- 焦点不能outline:none了事，必须有替代指示
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

POLISH_SYSTEM = """You are a frontend polish reviewer. Check for these quality issues:

CHEAPNESS SOURCES (check all 6):
1. Global monospace font (should only be for numbers/code/filenames)
2. 10px uppercase + wide letter-spacing (dated "dark dashboard" template look)
3. Zero border-radius + hard borders (spreadsheet feel)
4. Neon colors + pure black background (visual fatigue, game HUD)
5. Crowding (no breathing space between elements, padding < 8px)
6. No transitions/hover feedback (stiff interface)

COLOR SYSTEM (4 layers + 3 text levels + 1 accent):
- Surface layers: #161618 -> #1c1c1e -> #2c2c2e -> #3a3a3c (~16 brightness steps)
- Text: primary 88%, secondary 55%, tertiary 30%
- Borders: normal 8%, strong 14% white opacity
- Accent: one saturated color, desaturated 10-15%

DEFENSIVE LAYOUT:
- Fixed areas: flex-shrink-0. Flexible areas: flex-1 min-h-0
- Never combine flex-1 with minHeight (conflict, minHeight wins, container breaks)
- Must-visible elements (buttons, status, warnings) in flex-shrink-0 regions
- Fixed width overlays: width: min(Npx, 100vw)
- Horizontal tabs: overflow-x-auto instead of overflow/clipping

NATIVE STYLE ISOLATION:
- type="number" spinner: use type="text" + inputMode="numeric" or CSS hide spinner
- select: appearance: none + custom arrow
- textarea: resize: none
- focus: never bare outline:none, must have box-shadow/border replacement
- button: reset appearance/background/border/font

Given CSS/HTML code, identify which cheapness sources and layout issues exist."""


def execute(ctx: dict) -> dict:
    css = ctx.get("css", "")
    html = ctx.get("html", "")
    if not css and not html:
        return ctx

    snippet = (css[:300] if css else "") + "\n" + (html[:300] if html else "")
    review = ask(
        POLISH_SYSTEM,
        f"Review this frontend code:\n{snippet}",
        max_tokens=150
    ).strip()
    ctx["_polish_review"] = review
    return ctx

node = Node(id="993", name="前端精致感审查",
    trigger={"type": "key_exists", "key": "css"},
    execute=execute, refs=["Y20"],
    metadata={"source": "Guild/精致感+UI自查+原生样式+Flex防溢出", "category": "code_quality"})
