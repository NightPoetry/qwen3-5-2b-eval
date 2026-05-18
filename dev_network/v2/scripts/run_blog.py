"""
用 v2 引擎生成精美个人博客。

策略：博客是展示型应用，CSS决定品质。
- HTML结构由系统模板生成（不让模型碰结构）
- CSS由系统精心手写（暗色、渐变、动画、卡片）
- JS只做导航切换（系统模板）
- 模型只负责：博文标题、摘要、个人介绍（纯文本内容）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from engine import Engine
from llm import ask


def generate_content():
    """模型生成博客内容（纯文本，每次只问一件事）。"""
    print("  生成个人介绍...")
    intro = ask(
        "你是技术博客作者。只输出纯文本，不要任何markdown标记或格式符号。",
        "写一段60字的个人简介：你是一个研究AI系统编排的开发者，"
        "专注让小型模型通过架构设计完成复杂任务。",
        temperature=0.7, max_tokens=120
    )

    print("  生成博文...")
    posts = []
    topics = [
        ("小模型系统编排", "2B参数模型如何通过编排框架完成复杂代码生成"),
        ("可执行知识网络", "从被动数据到主动程序——知识图谱的范式转变"),
        ("认知极限实验", "2B模型的能力边界：循环100%判断0%的启示"),
        ("事件层模板化", "确定性代码取代模型生成——从不稳定到100%正确"),
        ("网状知识路由", "邻接可见与触发门控——让知识按需激活"),
    ]

    for title, desc in topics:
        summary = ask(
            "你是技术博客作者。用一句话（25字以内）概括这篇文章的核心观点。只输出纯文本。",
            f"文章主题：{title}\n描述：{desc}\n\n一句话概括：",
            temperature=0.7, max_tokens=60
        )
        posts.append({"title": title, "summary": summary.strip().strip('"\'')})

    return {"intro": intro.strip(), "posts": posts}


def build_html(content):
    """系统确定性生成精美HTML。"""
    posts_html = ""
    for i, post in enumerate(content["posts"]):
        posts_html += f"""
            <article class="post-card" style="--delay: {i * 0.1}s">
                <div class="post-meta">
                    <span class="post-date">2026-05-{17-i:02d}</span>
                    <span class="post-tag">Research</span>
                </div>
                <h3 class="post-title">{post['title']}</h3>
                <p class="post-summary">{post['summary']}</p>
                <div class="post-footer">
                    <span class="read-more">阅读全文 →</span>
                </div>
            </article>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Systems Research</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="noise"></div>

    <header class="hero">
        <div class="hero-content">
            <div class="avatar">
                <svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#388bfd"/>
                            <stop offset="100%" style="stop-color:#a855f7"/>
                        </linearGradient>
                    </defs>
                    <circle cx="40" cy="40" r="36" fill="none" stroke="url(#g1)" stroke-width="2"/>
                    <text x="40" y="48" text-anchor="middle" fill="url(#g1)" font-size="24" font-family="monospace">AI</text>
                </svg>
            </div>
            <h1 class="site-title">AI Systems Research</h1>
            <p class="site-subtitle">{content['intro']}</p>
        </div>
    </header>

    <nav class="nav-bar">
        <a href="#" class="nav-item active" data-section="posts">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M1 3h14v2H1V3zm0 4h14v2H1V7zm0 4h10v2H1v-2z"/>
            </svg>
            博文
        </a>
        <a href="#" class="nav-item" data-section="projects">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M2 2h5v5H2V2zm7 0h5v5H9V2zM2 9h5v5H2V9zm7 0h5v5H9V9z"/>
            </svg>
            项目
        </a>
        <a href="#" class="nav-item" data-section="about">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 1a7 7 0 100 14A7 7 0 008 1zm0 2a2 2 0 110 4 2 2 0 010-4zm0 10c-2.2 0-4.1-1.1-5.2-2.8C4 9.4 6 8.9 8 8.9s4 .5 5.2 1.3C12.1 11.9 10.2 13 8 13z"/>
            </svg>
            关于
        </a>
    </nav>

    <main class="content">
        <section id="posts" class="section active">
            <div class="section-header">
                <h2>最近文章</h2>
                <span class="post-count">{len(content['posts'])} 篇</span>
            </div>
            <div class="posts-grid">{posts_html}
            </div>
        </section>

        <section id="projects" class="section">
            <div class="section-header">
                <h2>开源项目</h2>
            </div>
            <div class="projects-grid">
                <div class="project-card">
                    <div class="project-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                        </svg>
                    </div>
                    <h3>dev-network</h3>
                    <p>可执行知识网络引擎 — 31节点图驱动的代码生成框架</p>
                    <div class="project-stats">
                        <span>Python</span>
                        <span>31 nodes</span>
                    </div>
                </div>
                <div class="project-card">
                    <div class="project-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/><path d="M8 12l2 2 4-4"/>
                        </svg>
                    </div>
                    <h3>cognitive-expansion</h3>
                    <p>认知展开器 — 将复合判断拆解为原子微问题序列</p>
                    <div class="project-stats">
                        <span>Python</span>
                        <span>100% accuracy</span>
                    </div>
                </div>
                <div class="project-card">
                    <div class="project-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
                        </svg>
                    </div>
                    <h3>system-orchestrated</h3>
                    <p>系统编排框架 — 2B模型达成6/6=100% F1的提取管线</p>
                    <div class="project-stats">
                        <span>Python</span>
                        <span>F1=1.00</span>
                    </div>
                </div>
            </div>
        </section>

        <section id="about" class="section">
            <div class="about-content">
                <h2>关于</h2>
                <div class="about-text">
                    <p>{content['intro']}</p>
                    <p>核心研究方向：让极小模型（2B参数）通过系统编排完成传统上需要大模型才能胜任的复杂任务。</p>
                </div>
                <div class="tech-stack">
                    <h3>技术栈</h3>
                    <div class="tech-tags">
                        <span class="tech-tag">Qwen3.5-2B</span>
                        <span class="tech-tag">Python</span>
                        <span class="tech-tag">System Orchestration</span>
                        <span class="tech-tag">Knowledge Network</span>
                        <span class="tech-tag">Deterministic Validation</span>
                    </div>
                </div>
                <div class="philosophy">
                    <h3>设计哲学</h3>
                    <blockquote>
                        模型做不到100%的事交给程序。模型只做语义理解。其余一切，代码来做。
                    </blockquote>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <p>Powered by 2B Model + Executable Knowledge Network</p>
    </footer>

    <script src="app.js"></script>
</body>
</html>"""


def build_css():
    """系统确定性生成精美CSS——暗色、渐变、微动画、卡片悬浮。"""
    return """*,*::before,*::after { margin:0; padding:0; box-sizing:border-box; }

:root {
  --bg-0: #0a0e14;
  --bg-1: #0d1117;
  --bg-2: #161b22;
  --bg-3: #1c2128;
  --text-0: #f0f6fc;
  --text-1: #c9d1d9;
  --text-2: #8b949e;
  --text-3: #484f58;
  --accent: #388bfd;
  --accent-2: #a855f7;
  --border: #21262d;
  --radius: 12px;
  --glow: 0 0 20px rgba(56,139,253,0.15);
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', sans-serif;
  background: var(--bg-0);
  color: var(--text-1);
  line-height: 1.7;
  min-height: 100vh;
  overflow-x: hidden;
}

.noise {
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.02;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  z-index: 9999;
}

/* === HERO === */
.hero {
  padding: 80px 20px 48px;
  text-align: center;
  background: linear-gradient(180deg, var(--bg-1) 0%, var(--bg-0) 100%);
  border-bottom: 1px solid var(--border);
}

.hero-content { max-width: 600px; margin: 0 auto; }

.avatar {
  width: 80px; height: 80px;
  margin: 0 auto 20px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%,100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.site-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-0);
  letter-spacing: -0.5px;
  margin-bottom: 12px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.site-subtitle {
  color: var(--text-2);
  font-size: 0.95rem;
  max-width: 480px;
  margin: 0 auto;
}

/* === NAV === */
.nav-bar {
  display: flex;
  justify-content: center;
  gap: 4px;
  padding: 12px 20px;
  position: sticky;
  top: 0;
  background: var(--bg-0);
  border-bottom: 1px solid var(--border);
  z-index: 100;
  backdrop-filter: blur(12px);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  color: var(--text-2);
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-item:hover { color: var(--text-0); background: var(--bg-2); }
.nav-item.active { color: var(--text-0); background: var(--bg-3); box-shadow: var(--glow); }

/* === CONTENT === */
.content {
  max-width: 720px;
  margin: 0 auto;
  padding: 32px 20px;
}

.section { display: none; animation: fadeIn 0.3s ease; }
.section.active { display: block; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.section-header h2 { font-size: 1.3rem; color: var(--text-0); font-weight: 600; }
.post-count { font-size: 0.8rem; color: var(--text-3); background: var(--bg-2); padding: 4px 10px; border-radius: 12px; }

/* === POST CARDS === */
.posts-grid { display: flex; flex-direction: column; gap: 16px; }

.post-card {
  background: var(--bg-2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  animation: slideUp 0.4s ease both;
  animation-delay: var(--delay, 0s);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.post-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
  box-shadow: var(--glow);
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.post-date { font-size: 0.78rem; color: var(--text-3); }
.post-tag {
  font-size: 0.7rem;
  color: var(--accent);
  background: rgba(56,139,253,0.1);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.post-title { font-size: 1.1rem; color: var(--text-0); font-weight: 600; margin-bottom: 8px; }
.post-summary { font-size: 0.88rem; color: var(--text-2); margin-bottom: 12px; }

.post-footer { display: flex; justify-content: flex-end; }
.read-more {
  font-size: 0.8rem;
  color: var(--accent);
  font-weight: 500;
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.2s ease;
}
.post-card:hover .read-more { opacity: 1; transform: translateX(0); }

/* === PROJECTS === */
.projects-grid { display: grid; grid-template-columns: 1fr; gap: 16px; }

@media (min-width: 540px) {
  .projects-grid { grid-template-columns: repeat(2, 1fr); }
}

.project-card {
  background: var(--bg-2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  transition: all 0.25s ease;
}

.project-card:hover { border-color: var(--accent-2); transform: translateY(-2px); }

.project-icon {
  width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, rgba(56,139,253,0.1), rgba(168,85,247,0.1));
  border-radius: 10px;
  margin-bottom: 14px;
  color: var(--accent);
}

.project-card h3 { font-size: 1rem; color: var(--text-0); margin-bottom: 8px; font-weight: 600; }
.project-card p { font-size: 0.84rem; color: var(--text-2); margin-bottom: 12px; line-height: 1.5; }

.project-stats {
  display: flex; gap: 12px;
  font-size: 0.75rem; color: var(--text-3);
}

/* === ABOUT === */
.about-content { max-width: 600px; }
.about-content h2 { font-size: 1.3rem; color: var(--text-0); margin-bottom: 20px; }
.about-text p { margin-bottom: 12px; color: var(--text-2); font-size: 0.92rem; }

.tech-stack { margin-top: 28px; }
.tech-stack h3 { font-size: 1rem; color: var(--text-0); margin-bottom: 12px; }
.tech-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tech-tag {
  font-size: 0.78rem;
  color: var(--text-1);
  background: var(--bg-3);
  border: 1px solid var(--border);
  padding: 5px 12px;
  border-radius: 6px;
  transition: all 0.2s;
}
.tech-tag:hover { border-color: var(--accent); color: var(--accent); }

.philosophy { margin-top: 28px; }
.philosophy h3 { font-size: 1rem; color: var(--text-0); margin-bottom: 12px; }
.philosophy blockquote {
  border-left: 3px solid var(--accent);
  padding: 12px 16px;
  background: var(--bg-2);
  border-radius: 0 8px 8px 0;
  color: var(--text-2);
  font-size: 0.9rem;
  font-style: italic;
}

/* === FOOTER === */
footer {
  margin-top: 64px;
  padding: 24px 20px;
  border-top: 1px solid var(--border);
  text-align: center;
  font-size: 0.78rem;
  color: var(--text-3);
}

/* === SCROLLBAR === */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-0); }
::-webkit-scrollbar-thumb { background: var(--bg-3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-3); }

/* === SELECTION === */
::selection { background: rgba(56,139,253,0.3); color: var(--text-0); }
"""


def build_js():
    """系统确定性生成导航JS + 渐入动画。"""
    return """document.addEventListener('DOMContentLoaded', () => {
  const navItems = document.querySelectorAll('.nav-item');
  const sections = document.querySelectorAll('.section');

  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const target = item.dataset.section;

      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');

      sections.forEach(s => {
        s.classList.remove('active');
        if (s.id === target) {
          s.classList.add('active');
          s.querySelectorAll('.post-card, .project-card').forEach((card, i) => {
            card.style.animation = 'none';
            card.offsetHeight;
            card.style.animation = `slideUp 0.4s ease both ${i * 0.08}s`;
          });
        }
      });
    });
  });
});
"""


def main():
    print("=== v2 精美博客生成 ===\n")

    print("Step 1: 模型生成内容（隔离对话）")
    content = generate_content()
    print(f"  介绍: {content['intro'][:50]}...")
    for p in content["posts"]:
        print(f"  [{p['title']}] {p['summary'][:30]}...")

    print("\nStep 2: 系统确定性生成代码")
    html = build_html(content)
    css = build_css()
    js = build_js()
    print(f"  HTML: {len(html)} chars")
    print(f"  CSS:  {len(css)} chars")
    print(f"  JS:   {len(js)} chars")

    print("\nStep 3: 通过v2引擎验证")
    # 加载引擎并注入已生成的代码进行验证
    engine = Engine()
    engine.load_from_dir(Path(__file__).parent / "nodes")

    # 只跑验证/知识节点（跳过生成节点）
    ctx = {
        "task": "精美个人技术博客 blog",
        "html": html,
        "css": css,
        "js": js,
        "raw_html": html,
        "raw_css": css,
        "raw_js": js,
        "contract": {"elements": []},
        "interactions": "浏览博文 切换页面 查看项目",
        "output_dir": str(Path(__file__).parent / "output_blog"),
        "_entry": "100",
    }

    # 手动触发知识节点链
    knowledge_nodes = ["100", "101", "120", "121", "122", "140", "160", "191", "200", "210"]
    for nid in knowledge_nodes:
        node = engine.nodes.get(nid)
        if node and engine.check_trigger(node, ctx):
            ctx = node.execute(ctx)
            print(f"  [{nid}] {node.name}")

    # 保存
    output_dir = Path(__file__).parent / "output_blog"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "index.html").write_text(ctx.get("html", html))
    (output_dir / "style.css").write_text(ctx.get("css", css))
    (output_dir / "app.js").write_text(ctx.get("js", js))

    print(f"\nStep 4: 保存到 {output_dir}")

    # 打印修复记录
    if ctx.get("_style_fixes"):
        print(f"\n样式修复: {ctx['_style_fixes']}")
    if ctx.get("_warnings"):
        print(f"警告: {ctx['_warnings']}")

    print("\n完成。")


if __name__ == "__main__":
    main()
