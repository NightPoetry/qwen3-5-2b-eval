"""CSS碎片：about + tags + blockquote样式"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify": return ctx
    v = ctx["v"]
    ctx["css_fragments"]["50_about"] = f""".about p{{font-size:.88rem;color:{v['text3']};margin-bottom:10px}}
.tags{{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}}
.tg{{font-size:.74rem;font-weight:500;color:{v['text2']};background:{v['bg']};border:1px solid {v['border']};padding:4px 11px;border-radius:6px;transition:all .2s}}
.tg:hover{{border-color:{v['accent']};color:{v['accent']}}}
blockquote{{border-left:3px solid {v['accent']};padding:12px 16px;margin-top:12px;background:{v['bg']};border-radius:0 8px 8px 0;font-size:.86rem;color:{v['text3']};font-style:italic}}"""
    return ctx

node = Node(id="250_s", name="CSS:about",
    trigger={"type": "key_exists", "key": "v"}, execute=execute, refs=[])
