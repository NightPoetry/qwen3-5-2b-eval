"""HTML碎片：projects section"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify": return ctx
    ctx["html_fragments"]["projects"] = """<section id="projects">
  <div class="sh"><span>开源项目</span></div>
  <div class="pg">
    <div class="pc"><h3>dev-network</h3><p>可执行知识网络引擎 — 31节点图驱动的代码生成框架</p><span class="ps">Python · 31 nodes</span></div>
    <div class="pc"><h3>cognitive-expansion</h3><p>认知展开器 — 将复合判断拆解为原子微问题序列</p><span class="ps">Python · 100% accuracy</span></div>
    <div class="pc"><h3>system-orchestrated</h3><p>系统编排框架 — 2B模型达成6/6=100%提取准确率</p><span class="ps">Python · F1 = 1.00</span></div>
  </div>
</section>"""
    return ctx

node = Node(id="130_h", name="HTML:projects",
    trigger={"type": "key_exists", "key": "v"}, execute=execute, refs=[])
