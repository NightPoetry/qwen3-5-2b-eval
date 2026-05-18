"""CSS碎片：nav样式"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify": return ctx
    v = ctx["v"]
    ctx["css_fragments"]["20_nav"] = f"""nav{{position:sticky;top:0;z-index:100;background:{v['nav_bg']};backdrop-filter:blur(12px) saturate(180%);-webkit-backdrop-filter:blur(12px) saturate(180%);border-bottom:1px solid {v['border']}}}
nav .w{{display:flex;gap:4px;padding:8px 24px}}
nav a{{padding:7px 14px;font-size:0.82rem;font-weight:500;color:{v['text3']};text-decoration:none;border-radius:7px;transition:all .2s}}
nav a:hover{{color:{v['text']};background:{v['bg']}}}"""
    return ctx

node = Node(id="220_s", name="CSS:nav",
    trigger={"type": "key_exists", "key": "v"}, execute=execute, refs=[])
