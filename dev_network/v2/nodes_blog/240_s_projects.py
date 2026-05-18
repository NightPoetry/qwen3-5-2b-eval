"""CSS碎片：projects grid样式"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify": return ctx
    v = ctx["v"]
    ctx["css_fragments"]["40_projects"] = f""".pg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}}
.pc{{background:{v['bg2']};border:1px solid {v['border']};border-radius:12px;padding:18px;transition:all .2s}}
.pc:hover{{border-color:{v['purple']};box-shadow:0 4px 14px -3px rgba(124,58,237,.2);transform:translateY(-1px)}}
.pc h3{{font-size:.92rem;font-weight:600;color:{v['text']};margin-bottom:6px}}
.pc p{{font-size:.8rem;color:{v['text3']};line-height:1.5;margin-bottom:10px}}
.ps{{font-size:.7rem;color:{v['text4']};font-weight:500}}"""
    return ctx

node = Node(id="240_s", name="CSS:projects",
    trigger={"type": "key_exists", "key": "v"}, execute=execute, refs=[])
