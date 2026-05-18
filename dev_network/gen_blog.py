"""
博客生成器 — 让 2B 模型生成个人博客页面。

博客是静态展示型应用，不需要 localStorage/事件委托。
系统确定性提供：HTML结构模板、CSS暗色主题、简单的导航JS。
模型负责：内容生成（博文标题、摘要、个人介绍）。
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import requests
from validator import validate_file

API_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-2b"
TIMEOUT = 120


def isolated_chat(system: str, user: str, max_tokens: int = 512) -> str:
    resp = requests.post(API_URL, json={
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens,
    }, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def generate_blog_content() -> dict:
    """让模型生成博客内容（纯文本，不涉及代码）。"""

    # Step 1: 生成博主介绍
    intro = isolated_chat(
        "你是一个技术博客作者。只输出纯文本，不要markdown标记。",
        "写一段50字左右的个人简介，你是一个研究小型AI模型系统编排的开发者。",
        max_tokens=100
    )

    # Step 2: 生成3篇博文标题和摘要
    posts_raw = isolated_chat(
        "你是技术博客作者。按格式输出，每篇一行：标题|摘要（30字内）。不要编号。",
        ("写3篇关于以下主题的博文标题和摘要：\n"
         "  1. 小模型通过系统编排完成复杂任务\n"
         "  2. 知识图谱vs可执行知识网络\n"
         "  3. 2B参数模型的认知极限实验\n\n"
         "格式（每行）：标题|摘要"),
        max_tokens=300
    )

    # 解析博文
    posts = []
    for line in posts_raw.strip().split("\n"):
        line = line.strip().lstrip("-·•*0123456789. ")
        if "|" in line:
            parts = line.split("|", 1)
            posts.append({"title": parts[0].strip(), "summary": parts[1].strip()})
        elif line:
            posts.append({"title": line, "summary": ""})

    if len(posts) < 3:
        posts.extend([
            {"title": "系统编排让2B模型完成复杂任务", "summary": "单线程处理器也能搭建完整应用"},
            {"title": "从知识图谱到可执行知识网络", "summary": "被动数据vs主动程序的本质区别"},
            {"title": "2B模型认知极限实验", "summary": "循环100%，判断0%，组合崩溃"},
        ][:3 - len(posts)])

    return {"intro": intro.strip(), "posts": posts[:3]}


def generate_html(content: dict) -> str:
    """系统确定性生成HTML（模型不参与结构）。"""
    posts_html = ""
    for i, post in enumerate(content["posts"]):
        posts_html += f"""
        <article class="post-card" id="post{i}">
            <h2>{post['title']}</h2>
            <p class="summary">{post['summary']}</p>
            <span class="date">2026-05-17</span>
        </article>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Systems Research Blog</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1 id="siteTitle">AI Systems Research</h1>
        <p id="siteIntro">{content['intro']}</p>
    </header>

    <nav id="nav">
        <a href="#" class="nav-link active" data-section="posts">博文</a>
        <a href="#" class="nav-link" data-section="about">关于</a>
    </nav>

    <main id="content">
        <section id="posts" class="section active">{posts_html}
        </section>

        <section id="about" class="section">
            <h2>关于本站</h2>
            <p>本博客记录小型AI模型（2B参数）通过系统编排完成复杂任务的研究。</p>
            <p>核心发现：模型做不到100%的事交给程序，模型只做语义理解。</p>
            <h3>技术栈</h3>
            <ul>
                <li>模型：Qwen3.5-2B</li>
                <li>编排：Python 系统编排框架</li>
                <li>知识：可执行知识网络（非传统KG）</li>
            </ul>
        </section>
    </main>

    <footer>
        <p>Powered by 2B Model + System Orchestration</p>
    </footer>

    <script src="app.js"></script>
</body>
</html>"""


def generate_css() -> str:
    """系统确定性生成CSS暗色主题。"""
    return """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #0d1117;
  color: #c9d1d9;
  line-height: 1.6;
  max-width: 720px;
  margin: 0 auto;
  padding: 40px 20px;
}

header {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #21262d;
}

header h1 {
  font-size: 1.8rem;
  color: #f0f6fc;
  margin-bottom: 8px;
}

header p {
  color: #8b949e;
  font-size: 0.95rem;
}

nav {
  margin-bottom: 32px;
  display: flex;
  gap: 16px;
}

.nav-link {
  color: #8b949e;
  text-decoration: none;
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.2s;
}

.nav-link:hover {
  color: #f0f6fc;
  background: #161b22;
}

.nav-link.active {
  color: #f0f6fc;
  background: #21262d;
}

.section {
  display: none;
}

.section.active {
  display: block;
}

.post-card {
  background: #161b22;
  border: 1px solid #21262d;
  border-radius: 8px;
  padding: 20px 24px;
  margin-bottom: 16px;
  transition: border-color 0.2s;
}

.post-card:hover {
  border-color: #388bfd;
}

.post-card h2 {
  font-size: 1.2rem;
  color: #f0f6fc;
  margin-bottom: 8px;
}

.post-card .summary {
  color: #8b949e;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.post-card .date {
  color: #484f58;
  font-size: 0.8rem;
}

#about h2 {
  color: #f0f6fc;
  margin-bottom: 12px;
}

#about h3 {
  color: #f0f6fc;
  margin-top: 20px;
  margin-bottom: 8px;
}

#about p {
  margin-bottom: 8px;
  color: #8b949e;
}

#about ul {
  list-style: none;
  padding-left: 0;
}

#about li {
  padding: 4px 0;
  color: #8b949e;
}

#about li::before {
  content: "→ ";
  color: #388bfd;
}

footer {
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid #21262d;
  text-align: center;
  color: #484f58;
  font-size: 0.8rem;
}
"""


def generate_js() -> str:
    """系统确定性生成导航JS。"""
    return """document.addEventListener('DOMContentLoaded', () => {
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('.section');

  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const target = link.dataset.section;

      navLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');

      sections.forEach(s => s.classList.remove('active'));
      document.getElementById(target).classList.add('active');
    });
  });
});
"""


def run():
    print("=== 个人博客生成 ===\n")

    # 模型生成内容
    print("Step 1: 模型生成博客内容...")
    content = generate_blog_content()
    print(f"  介绍: {content['intro'][:40]}...")
    for p in content["posts"]:
        print(f"  博文: {p['title']}")

    # 系统生成代码
    print("\nStep 2: 系统确定性生成代码...")
    html = generate_html(content)
    css = generate_css()
    js = generate_js()

    # 验证
    print("\nStep 3: 验证修复...")
    all_files = {"index.html": html, "style.css": css, "app.js": js}
    html, html_issues = validate_file("index.html", html, all_files)
    css, css_issues = validate_file("style.css", css, all_files)
    js, js_issues = validate_file("app.js", js, all_files)

    for name, issues in [("HTML", html_issues), ("CSS", css_issues), ("JS", js_issues)]:
        if issues:
            for iss in issues:
                print(f"  [{name}] {iss.message} → {iss.fix}")
        else:
            print(f"  [{name}] 无问题")

    # 保存
    output_dir = Path(__file__).parent / "output_blog_v3"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "index.html").write_text(html)
    (output_dir / "style.css").write_text(css)
    (output_dir / "app.js").write_text(js)

    print(f"\n保存到: {output_dir}")
    return output_dir


if __name__ == "__main__":
    run()
