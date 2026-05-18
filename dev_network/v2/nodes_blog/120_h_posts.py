"""HTML碎片：posts section"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify": return ctx
    posts = ctx.get("blog", {}).get("posts", [])
    cards = ""
    for i, p in enumerate(posts):
        body_html = "".join(f"<p>{b}</p>" for b in p.get("body", []))
        cards += f"""
    <article class="card" id="post-{i}">
      <div class="meta"><span class="date">2026-05-{17-i:02d}</span><span class="tag">Research</span></div>
      <h3>{p['title']}</h3>
      <p class="desc">{p['summary']}</p>
      <div class="body">{body_html}</div>
      <button class="toggle" onclick="this.parentElement.classList.toggle('open')">
        <span class="t-open">展开全文</span><span class="t-close">收起</span>
      </button>
    </article>"""

    ctx["html_fragments"]["posts"] = f"""<section id="posts">
  <div class="sh"><span>最近文章</span><span class="badge">{len(posts)} 篇</span></div>
  {cards}
</section>"""
    return ctx

node = Node(id="120_h", name="HTML:posts",
    trigger={"type": "key_exists", "key": "v"}, execute=execute, refs=[])
