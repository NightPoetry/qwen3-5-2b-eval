"""CSS碎片：card + post样式"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify": return ctx
    v = ctx["v"]
    ctx["css_fragments"]["30_cards"] = f"""section{{padding:40px 0}}
section+section{{border-top:1px solid {v['border']}}}
.sh{{font-size:1.1rem;font-weight:600;color:{v['text']};margin-bottom:20px;padding-bottom:10px;border-bottom:1px solid {v['border']};display:flex;justify-content:space-between;align-items:baseline}}
.badge{{font-size:0.7rem;font-weight:600;color:{v['accent']};background:{v['accent_bg']};padding:2px 10px;border-radius:99px}}
.card{{background:{v['bg2']};border:1px solid {v['border']};border-radius:12px;padding:20px 24px;margin-bottom:12px;transition:all .2s}}
.card:hover{{border-color:{v['accent']};box-shadow:{v['shadow']};transform:translateY(-1px)}}
.meta{{display:flex;gap:8px;align-items:center;margin-bottom:8px}}
.date{{font-size:0.74rem;color:{v['text4']}}}
.tag{{font-size:0.66rem;font-weight:600;color:{v['accent']};background:{v['accent_bg']};padding:2px 8px;border-radius:4px}}
.card h3{{font-size:1.02rem;font-weight:600;color:{v['text']};margin-bottom:4px;transition:color .2s}}
.card:hover h3{{color:{v['accent']}}}
.desc{{font-size:0.84rem;color:{v['text3']}}}
.body{{max-height:0;overflow:hidden;transition:max-height .4s ease,padding .3s}}
.body p{{font-size:0.88rem;color:{v['text2']};line-height:1.8;margin-bottom:10px}}
.card.open .body{{max-height:600px;padding:14px 0 4px;border-top:1px solid {v['border']};margin-top:12px}}
.toggle{{display:block;margin-top:10px;background:none;border:none;font-size:0.8rem;font-weight:500;color:{v['accent']};cursor:pointer;padding:0;transition:opacity .2s}}
.toggle:hover{{opacity:.7}}
.t-close{{display:none}}.card.open .t-open{{display:none}}.card.open .t-close{{display:inline}}"""
    return ctx

node = Node(id="230_s", name="CSS:cards",
    trigger={"type": "key_exists", "key": "v"}, execute=execute, refs=[])
