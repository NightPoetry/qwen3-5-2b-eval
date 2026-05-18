"""
最终版博客 — 全展开滚动式，内容真实可交互。

裸2B教训：漂亮但不能用 = 没有价值。
所以：全部内容在一页上可见+文章可展开+导航用锚点跳转。
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from llm import ask


def gen_article_body(title, desc):
    """模型为每篇文章生成3段正文。"""
    body = ask(
        "你是技术博客作者。输出3段正文（每段40-60字）。纯文本，不要markdown标记。段落之间用空行分隔。",
        f"为文章《{title}》写正文。主题：{desc}",
        temperature=0.7, max_tokens=300
    )
    paragraphs = [p.strip() for p in body.strip().split("\n") if p.strip()]
    return paragraphs[:3] if len(paragraphs) >= 3 else paragraphs + [""] * (3 - len(paragraphs))


def main():
    theme = "dark" if "--dark" in sys.argv else "light"
    print(f"=== 最终版博客 ({theme}) ===\n")

    # 模型生成内容
    print("Step 1: 模型生成内容")

    print("  [model] 个人介绍...")
    intro = ask(
        "只输出纯文本，不要markdown。",
        "写50字技术博客简介：你研究让小型AI模型通过系统编排完成复杂任务。",
        temperature=0.7, max_tokens=100
    ).strip()

    articles = [
        ("系统编排让2B模型写代码", "小模型如何通过管线分解完成复杂代码生成"),
        ("可执行知识网络", "从被动数据到主动程序的知识组织范式转变"),
        ("认知极限实验报告", "2B参数模型的能力边界和绕过策略"),
        ("事件层模板化", "用确定性代码取代模型生成达成100%正确率"),
        ("网状知识路由", "邻接可见和触发门控让知识按需激活"),
    ]

    posts = []
    for title, desc in articles:
        print(f"  [model] 《{title}》...")
        summary = ask(
            "只输出一句话（20字以内），纯文本。",
            f"一句话概括：{desc}",
            temperature=0.7, max_tokens=50
        ).strip().strip('"\'')

        body = gen_article_body(title, desc)
        posts.append({"title": title, "summary": summary, "body": body})

    # 构建HTML
    print("\nStep 2: 系统生成页面")

    posts_html = ""
    for i, post in enumerate(posts):
        body_html = "".join(f"<p>{p}</p>" for p in post["body"])
        posts_html += f"""
            <article class="post-card" id="post-{i}">
                <div class="post-meta">
                    <span class="post-date">2026-05-{17-i:02d}</span>
                    <span class="post-tag">Research</span>
                </div>
                <h3 class="post-title">{post['title']}</h3>
                <p class="post-summary">{post['summary']}</p>
                <div class="post-body">{body_html}</div>
                <button class="read-toggle" onclick="this.parentElement.classList.toggle('expanded')">
                    <span class="expand-text">展开全文</span>
                    <span class="collapse-text">收起</span>
                </button>
            </article>"""

    is_dark = theme == "dark"
    bg = "#0d1117" if is_dark else "#f8fafc"
    bg2 = "#161b22" if is_dark else "#ffffff"
    border = "#21262d" if is_dark else "#e2e8f0"
    text = "#f0f6fc" if is_dark else "#0f172a"
    text2 = "#c9d1d9" if is_dark else "#334155"
    text3 = "#8b949e" if is_dark else "#64748b"
    text4 = "#484f58" if is_dark else "#94a3b8"
    accent = "#388bfd" if is_dark else "#2563eb"
    accent_bg = "rgba(56,139,253,0.15)" if is_dark else "#dbeafe"
    nav_bg = "rgba(13,17,23,0.85)" if is_dark else "rgba(255,255,255,0.85)"
    shadow = "rgba(56,139,253,0.2)" if is_dark else "rgba(37,99,235,0.18)"
    purple = "#a855f7" if is_dark else "#7c3aed"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Systems Research</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; }}

body {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: {bg};
  color: {text2};
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}}

.wrap {{ max-width: 720px; margin: 0 auto; padding: 0 24px; }}

/* HEADER */
header {{
  background: {bg2};
  border-bottom: 1px solid {border};
  padding: 56px 0 44px;
  text-align: center;
}}

.avatar {{
  width: 64px; height: 64px;
  margin: 0 auto 18px;
  border-radius: 50%;
  padding: 2px;
  background: linear-gradient(135deg, {accent}, {purple});
}}

.avatar-inner {{
  width: 100%; height: 100%;
  border-radius: 50%;
  background: {bg2};
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; font-weight: 700; color: {accent};
}}

h1 {{
  font-size: 1.7rem; font-weight: 700; color: {text};
  letter-spacing: -0.02em; margin-bottom: 8px;
}}

.subtitle {{
  font-size: 0.9rem; color: {text3};
  max-width: 440px; margin: 0 auto; line-height: 1.6;
}}

/* NAV */
nav {{
  position: sticky; top: 0; z-index: 100;
  background: {nav_bg};
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-bottom: 1px solid {border};
}}

nav .wrap {{
  display: flex; gap: 4px; padding: 8px 24px;
}}

nav a {{
  padding: 7px 14px;
  font-size: 0.82rem; font-weight: 500;
  color: {text3}; text-decoration: none;
  border-radius: 7px;
  transition: all 0.2s;
}}

nav a:hover {{ color: {text}; background: {bg}; }}

/* SECTION */
section {{ padding: 40px 0; }}
section + section {{ border-top: 1px solid {border}; }}

.sec-title {{
  font-size: 1.1rem; font-weight: 600; color: {text};
  margin-bottom: 20px; padding-bottom: 10px;
  border-bottom: 1px solid {border};
  display: flex; justify-content: space-between; align-items: baseline;
}}

.badge {{
  font-size: 0.7rem; font-weight: 600;
  color: {accent}; background: {accent_bg};
  padding: 2px 10px; border-radius: 99px;
}}

/* POSTS */
.post-card {{
  background: {bg2};
  border: 1px solid {border};
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 12px;
  transition: all 0.2s;
}}

.post-card:hover {{
  border-color: {accent};
  box-shadow: 0 4px 14px -3px {shadow};
  transform: translateY(-1px);
}}

.post-meta {{
  display: flex; gap: 8px; align-items: center;
  margin-bottom: 8px;
}}

.post-date {{ font-size: 0.74rem; color: {text4}; }}

.post-tag {{
  font-size: 0.66rem; font-weight: 600;
  color: {accent}; background: {accent_bg};
  padding: 2px 8px; border-radius: 4px;
}}

.post-title {{
  font-size: 1.02rem; font-weight: 600; color: {text};
  margin-bottom: 4px; transition: color 0.2s;
}}

.post-card:hover .post-title {{ color: {accent}; }}

.post-summary {{
  font-size: 0.84rem; color: {text3}; margin-bottom: 0;
}}

/* 文章正文（默认折叠） */
.post-body {{
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.4s ease, padding 0.3s ease;
  padding: 0;
}}

.post-body p {{
  font-size: 0.88rem; color: {text2}; line-height: 1.8;
  margin-bottom: 10px;
}}

.post-card.expanded .post-body {{
  max-height: 500px;
  padding: 14px 0 4px;
  border-top: 1px solid {border};
  margin-top: 12px;
}}

.read-toggle {{
  display: block;
  margin-top: 10px;
  background: none; border: none;
  font-size: 0.8rem; font-weight: 500;
  color: {accent}; cursor: pointer;
  padding: 0;
  transition: opacity 0.2s;
}}

.read-toggle:hover {{ opacity: 0.7; }}

.collapse-text {{ display: none; }}
.post-card.expanded .expand-text {{ display: none; }}
.post-card.expanded .collapse-text {{ display: inline; }}

/* PROJECTS */
.proj-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}}

.proj-card {{
  background: {bg2};
  border: 1px solid {border};
  border-radius: 12px;
  padding: 18px;
  transition: all 0.2s;
}}

.proj-card:hover {{
  border-color: {purple};
  box-shadow: 0 4px 14px -3px rgba(124,58,237,0.2);
  transform: translateY(-1px);
}}

.proj-card h3 {{ font-size: 0.92rem; font-weight: 600; color: {text}; margin-bottom: 6px; }}
.proj-card p {{ font-size: 0.8rem; color: {text3}; line-height: 1.5; margin-bottom: 10px; }}
.proj-stat {{ font-size: 0.7rem; color: {text4}; font-weight: 500; }}

/* ABOUT */
.about p {{ font-size: 0.88rem; color: {text3}; margin-bottom: 10px; }}
.tags {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }}

.tag {{
  font-size: 0.74rem; font-weight: 500;
  color: {text2}; background: {bg};
  border: 1px solid {border};
  padding: 4px 11px; border-radius: 6px;
  transition: all 0.2s;
}}

.tag:hover {{ border-color: {accent}; color: {accent}; }}

blockquote {{
  border-left: 3px solid {accent};
  padding: 12px 16px; margin-top: 12px;
  background: {bg};
  border-radius: 0 8px 8px 0;
  font-size: 0.86rem; color: {text3};
  font-style: italic;
}}

/* FOOTER */
footer {{
  border-top: 1px solid {border};
  padding: 24px 0;
  text-align: center;
  font-size: 0.74rem; color: {text4};
}}

html {{ scroll-behavior: smooth; }}
::selection {{ background: {accent_bg}; color: {text}; }}
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-thumb {{ background: {border}; border-radius: 3px; }}

@media (max-width: 640px) {{
  header {{ padding: 36px 0 28px; }}
  h1 {{ font-size: 1.4rem; }}
  .proj-grid {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>

<header>
  <div class="wrap">
    <div class="avatar"><div class="avatar-inner">AI</div></div>
    <h1>AI Systems Research</h1>
    <p class="subtitle">{intro}</p>
  </div>
</header>

<nav>
  <div class="wrap">
    <a href="#posts">博文</a>
    <a href="#projects">项目</a>
    <a href="#about">关于</a>
  </div>
</nav>

<main class="wrap">

  <section id="posts">
    <div class="sec-title">
      <span>最近文章</span>
      <span class="badge">{len(posts)} 篇</span>
    </div>
    {posts_html}
  </section>

  <section id="projects">
    <div class="sec-title"><span>开源项目</span></div>
    <div class="proj-grid">
      <div class="proj-card">
        <h3>dev-network</h3>
        <p>可执行知识网络引擎 — 31节点图驱动的代码生成框架</p>
        <span class="proj-stat">Python · 31 nodes</span>
      </div>
      <div class="proj-card">
        <h3>cognitive-expansion</h3>
        <p>认知展开器 — 将复合判断拆解为原子微问题序列</p>
        <span class="proj-stat">Python · 100% accuracy</span>
      </div>
      <div class="proj-card">
        <h3>system-orchestrated</h3>
        <p>系统编排框架 — 2B模型达成6/6=100%提取准确率</p>
        <span class="proj-stat">Python · F1 = 1.00</span>
      </div>
    </div>
  </section>

  <section id="about">
    <div class="sec-title"><span>关于</span></div>
    <div class="about">
      <p>{intro}</p>
      <p>核心发现：模型做不到100%的事交给程序。模型只负责语义理解，其余一切由代码完成。</p>
      <h4 style="font-size:0.9rem;color:{text};margin:20px 0 8px;">技术栈</h4>
      <div class="tags">
        <span class="tag">Qwen3.5-2B</span>
        <span class="tag">Python</span>
        <span class="tag">System Orchestration</span>
        <span class="tag">Knowledge Network</span>
        <span class="tag">LM Studio</span>
      </div>
      <h4 style="font-size:0.9rem;color:{text};margin:20px 0 8px;">设计哲学</h4>
      <blockquote>2B模型是单线程处理器。给它一件简单的事，它做得完美。给它两件事，它就崩。系统的工作是把复杂任务拆成一串简单问题。</blockquote>
    </div>
  </section>

</main>

<footer><div class="wrap">Powered by 2B Model + Executable Knowledge Network</div></footer>

</body>
</html>"""

    output_dir = Path(__file__).parent / f"output_final_{theme}"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "index.html").write_text(html)

    print(f"\n保存到: {output_dir}")
    print(f"HTML: {len(html)} chars（单文件，内联CSS，无JS依赖）")
    print("完成。")


if __name__ == "__main__":
    main()
