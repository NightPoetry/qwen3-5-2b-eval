"""商业级博客HTML模板。参数化内容插入。"""


def generate(content: dict, theme="light") -> str:
    posts_html = ""
    for i, post in enumerate(content.get("posts", [])):
        delay = f"{i * 0.06}s"
        posts_html += f"""
                <article class="post-card" style="--i: {delay}">
                    <div class="post-meta">
                        <span class="post-date">{post.get('date', '2026-05-17')}</span>
                        <span class="post-tag">{post.get('tag', 'Research')}</span>
                    </div>
                    <h3 class="post-title">{post['title']}</h3>
                    <p class="post-summary">{post['summary']}</p>
                    <span class="post-arrow">阅读全文 →</span>
                </article>"""

    projects_html = ""
    for proj in content.get("projects", []):
        projects_html += f"""
                <div class="project-card">
                    <div class="project-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                            <path d="{proj.get('icon_path', 'M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5')}"/>
                        </svg>
                    </div>
                    <h3>{proj['name']}</h3>
                    <p>{proj['desc']}</p>
                    <div class="project-stats">
                        <span>{proj.get('lang', 'Python')}</span>
                        <span>{proj.get('stat', '')}</span>
                    </div>
                </div>"""

    tech_tags = ""
    for tag in content.get("tech_tags", []):
        tech_tags += f'<span class="tech-tag">{tag}</span>'

    intro = content.get("intro", "")
    title = content.get("title", "Blog")
    avatar_text = content.get("avatar_text", title[:2])

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <div class="container header-inner">
            <div class="avatar-ring">
                <div class="avatar-inner">{avatar_text}</div>
            </div>
            <h1 class="site-title">{title}</h1>
            <p class="site-subtitle">{intro}</p>
        </div>
    </header>

    <div class="nav-bar">
        <nav class="nav-inner container">
            <a href="#" class="nav-item active" data-section="posts">
                <svg viewBox="0 0 16 16" fill="currentColor"><path d="M1.5 2.5h13a.5.5 0 010 1h-13a.5.5 0 010-1zm0 4h13a.5.5 0 010 1h-13a.5.5 0 010-1zm0 4h8a.5.5 0 010 1h-8a.5.5 0 010-1z"/></svg>
                博文
            </a>
            <a href="#" class="nav-item" data-section="projects">
                <svg viewBox="0 0 16 16" fill="currentColor"><path d="M1 2.5h6v6H1v-6zm8 0h6v6H9v-6zM1 10.5h6v3H1v-3zm8 0h6v3H9v-3z"/></svg>
                项目
            </a>
            <a href="#" class="nav-item" data-section="about">
                <svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 1a7 7 0 100 14A7 7 0 008 1zm0 2.5a2 2 0 110 4 2 2 0 010-4zM4 11.6C5 10.4 6.4 9.6 8 9.6s3 .8 4 2c-1 1.2-2.4 2-4 2s-3-.8-4-2z"/></svg>
                关于
            </a>
        </nav>
    </div>

    <main class="content container">
        <section id="posts" class="section active">
            <div class="section-header">
                <h2>最近文章</h2>
                <span class="badge">{len(content.get('posts', []))} 篇</span>
            </div>
            <div class="posts-list">{posts_html}
            </div>
        </section>

        <section id="projects" class="section">
            <div class="section-header">
                <h2>开源项目</h2>
            </div>
            <div class="projects-grid">{projects_html}
            </div>
        </section>

        <section id="about" class="section">
            <div class="about-content">
                <h2>关于</h2>
                <div class="about-text">
                    <p>{intro}</p>
                    <p>{content.get('about_extra', '')}</p>
                </div>
                <div class="tech-stack">
                    <h3>技术栈</h3>
                    <div class="tech-tags">{tech_tags}</div>
                </div>
                <div class="philosophy">
                    <h3>设计哲学</h3>
                    <blockquote>{content.get('philosophy', '')}</blockquote>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>{content.get('footer', 'Powered by System Orchestration')}</p>
        </div>
    </footer>

    <script src="app.js"></script>
</body>
</html>"""
