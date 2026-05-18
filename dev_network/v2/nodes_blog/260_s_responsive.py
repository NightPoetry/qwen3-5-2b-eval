"""CSS碎片：footer + responsive"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify": return ctx
    v = ctx["v"]
    ctx["css_fragments"]["60_responsive"] = f"""footer{{border-top:1px solid {v['border']};padding:24px 0;text-align:center;font-size:.74rem;color:{v['text4']}}}
@media(max-width:640px){{header{{padding:36px 0 28px}}h1{{font-size:1.4rem}}.pg{{grid-template-columns:1fr}}}}"""
    return ctx

node = Node(id="260_s", name="CSS:responsive",
    trigger={"type": "key_exists", "key": "v"}, execute=execute,
    refs=["300_a"])
