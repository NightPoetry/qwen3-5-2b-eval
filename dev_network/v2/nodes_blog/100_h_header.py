"""HTML碎片：header"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify": return ctx
    v = ctx["v"]; blog = ctx.get("blog", {})
    title = blog.get("title", "Blog"); intro = blog.get("intro", "")
    ctx["html_fragments"]["header"] = f"""<header><div class="w">
  <div class="av"><div class="av-in">AI</div></div>
  <h1>{title}</h1>
  <p class="sub">{intro}</p>
</div></header>"""
    return ctx

node = Node(id="100_h", name="HTML:header",
    trigger={"type": "key_exists", "key": "v"}, execute=execute,
    refs=["110_h", "120_h", "130_h", "140_h", "150_h"])
