"""HTML碎片：about section"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify": return ctx
    intro = ctx.get("blog", {}).get("intro", "")
    ctx["html_fragments"]["about"] = f"""<section id="about">
  <div class="sh"><span>关于</span></div>
  <div class="about">
    <p>{intro}</p>
    <p>核心发现：模型做不到100%的事交给程序。模型只负责语义理解，其余一切由代码完成。</p>
    <h4 class="sub-h">技术栈</h4>
    <div class="tags">
      <span class="tg">Qwen3.5-2B</span><span class="tg">Python</span>
      <span class="tg">System Orchestration</span><span class="tg">Knowledge Network</span>
      <span class="tg">LM Studio</span>
    </div>
    <h4 class="sub-h">设计哲学</h4>
    <blockquote>2B模型是单线程处理器。给它一件简单的事，它做得完美。给它两件事，它就崩。系统的工作是把复杂任务拆成一串简单问题。</blockquote>
  </div>
</section>"""
    return ctx

node = Node(id="140_h", name="HTML:about",
    trigger={"type": "key_exists", "key": "v"}, execute=execute, refs=[])
