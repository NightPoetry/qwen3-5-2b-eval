"""HTML碎片：nav"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify": return ctx
    ctx["html_fragments"]["nav"] = """<nav><div class="w">
  <a href="#posts">博文</a>
  <a href="#projects">项目</a>
  <a href="#about">关于</a>
</div></nav>"""
    return ctx

node = Node(id="110_h", name="HTML:nav",
    trigger={"type": "key_exists", "key": "v"}, execute=execute, refs=[])
