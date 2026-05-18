"""知识节点：间距节奏 — 确保间距遵循8px倍数网格。"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

# 8px网格：有效值
VALID_SPACINGS = {0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64}


def execute(ctx: dict) -> dict:
    css = ctx.get("css", "")
    if not css:
        return ctx

    fixes = []
    # 找所有间距声明
    pattern = r'((?:padding|margin|gap)\s*:\s*)(\d+)(px)'

    def fix_spacing(match):
        prop = match.group(1)
        val = int(match.group(2))
        unit = match.group(3)

        if val in VALID_SPACINGS or val > 64:
            return match.group(0)

        # 找最近的合法值
        closest = min(VALID_SPACINGS, key=lambda x: abs(x - val))
        fixes.append(f"{val}px→{closest}px")
        return f"{prop}{closest}{unit}"

    new_css = re.sub(pattern, fix_spacing, css)

    if fixes:
        ctx["css"] = new_css
        ctx.setdefault("_style_fixes", []).append(f"间距对齐8px网格: {', '.join(fixes[:5])}")

    return ctx


node = Node(
    id="121",
    name="间距8px网格",
    trigger={"type": "key_exists", "key": "css"},
    execute=execute,
    refs=["122"],
    metadata={"source": "UI设计/呼吸留白", "category": "visual"},
)
