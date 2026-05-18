"""CSS碎片：header样式"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify": return ctx
    v = ctx["v"]
    ctx["css_fragments"]["10_header"] = f"""header{{background:{v['bg2']};border-bottom:1px solid {v['border']};padding:56px 0 44px;text-align:center}}
.av{{width:64px;height:64px;margin:0 auto 18px;border-radius:50%;padding:2px;background:linear-gradient(135deg,{v['accent']},{v['purple']})}}
.av-in{{width:100%;height:100%;border-radius:50%;background:{v['bg2']};display:flex;align-items:center;justify-content:center;font-size:1.3rem;font-weight:700;color:{v['accent']}}}
h1{{font-size:1.7rem;font-weight:700;color:{v['text']};letter-spacing:-0.02em;margin-bottom:8px}}
.sub{{font-size:0.9rem;color:{v['text3']};max-width:440px;margin:0 auto;line-height:1.6}}
.sub-h{{font-size:.9rem;color:{v['text']};margin:20px 0 8px}}"""
    return ctx

node = Node(id="210_s", name="CSS:header",
    trigger={"type": "key_exists", "key": "v"}, execute=execute, refs=[])
