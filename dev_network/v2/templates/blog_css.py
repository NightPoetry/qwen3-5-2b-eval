"""
商业级博客CSS模板系统。

设计原则：
  - 超越模型裸生成的水平，否则编排毫无意义
  - 参数化主题（亮/暗），不靠模型选色
  - 专业排版、间距节奏、微交互、响应式
"""


def generate(theme="light"):
    if theme == "dark":
        return _dark()
    return _light()


def _light():
    return """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --c-bg: #ffffff;
  --c-surface: #f8fafc;
  --c-surface-2: #f1f5f9;
  --c-border: #e2e8f0;
  --c-border-hover: #cbd5e1;
  --c-text: #0f172a;
  --c-text-2: #334155;
  --c-text-3: #64748b;
  --c-text-4: #94a3b8;
  --c-accent: #2563eb;
  --c-accent-light: #dbeafe;
  --c-accent-hover: #1d4ed8;
  --c-purple: #7c3aed;
  --c-green: #059669;
  --c-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --c-shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
  --c-shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.04);
  --c-shadow-accent: 0 4px 14px -3px rgba(37,99,235,0.25);
  --radius: 12px;
  --radius-sm: 8px;
  --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

html { scroll-behavior: smooth; }

body {
  font-family: var(--font);
  background: var(--c-surface);
  color: var(--c-text-2);
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ===== LAYOUT ===== */
.container { max-width: 800px; margin: 0 auto; padding: 0 24px; }

/* ===== HEADER ===== */
header {
  background: var(--c-bg);
  border-bottom: 1px solid var(--c-border);
  padding: 48px 0 40px;
}

.header-inner { text-align: center; }

.avatar-ring {
  width: 72px; height: 72px;
  margin: 0 auto 20px;
  border-radius: 50%;
  padding: 3px;
  background: linear-gradient(135deg, var(--c-accent), var(--c-purple));
}

.avatar-ring .avatar-inner {
  width: 100%; height: 100%;
  border-radius: 50%;
  background: var(--c-bg);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem; font-weight: 700; color: var(--c-accent);
}

.site-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--c-text);
  letter-spacing: -0.02em;
  margin-bottom: 8px;
}

.site-subtitle {
  font-size: 0.92rem;
  color: var(--c-text-3);
  max-width: 480px;
  margin: 0 auto;
  line-height: 1.6;
}

/* ===== NAV ===== */
.nav-bar {
  position: sticky; top: 0; z-index: 100;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-bottom: 1px solid var(--c-border);
  padding: 0 24px;
}

.nav-inner {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.nav-item {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 14px;
  font-size: 0.84rem;
  font-weight: 500;
  color: var(--c-text-3);
  text-decoration: none;
  border-radius: var(--radius-sm);
  transition: all var(--transition);
  position: relative;
}

.nav-item svg { width: 15px; height: 15px; }
.nav-item:hover { color: var(--c-text); background: var(--c-surface-2); }

.nav-item.active {
  color: var(--c-accent);
  background: var(--c-accent-light);
  font-weight: 600;
}

/* ===== SECTIONS ===== */
.section { display: none; }
.section.active { display: block; animation: fadeUp 0.35s ease both; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.content { padding: 32px 0 64px; }

.section-header {
  display: flex; align-items: baseline; justify-content: space-between;
  margin-bottom: 20px; padding-bottom: 12px;
  border-bottom: 1px solid var(--c-border);
}

.section-header h2 {
  font-size: 1.15rem; font-weight: 600; color: var(--c-text);
  letter-spacing: -0.01em;
}

.badge {
  font-size: 0.72rem; font-weight: 600;
  color: var(--c-accent);
  background: var(--c-accent-light);
  padding: 3px 10px; border-radius: 99px;
}

/* ===== POST CARDS ===== */
.posts-list { display: flex; flex-direction: column; gap: 12px; }

.post-card {
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  padding: 20px 24px;
  transition: all var(--transition);
  animation: slideIn 0.4s ease both;
  animation-delay: var(--i, 0);
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.post-card:hover {
  border-color: var(--c-accent);
  box-shadow: var(--c-shadow-accent);
  transform: translateY(-1px);
}

.post-meta {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 10px;
}

.post-date { font-size: 0.76rem; color: var(--c-text-4); }

.post-tag {
  font-size: 0.68rem; font-weight: 600; letter-spacing: 0.02em;
  color: var(--c-accent); background: var(--c-accent-light);
  padding: 2px 8px; border-radius: 4px;
}

.post-title {
  font-size: 1.05rem; font-weight: 600; color: var(--c-text);
  margin-bottom: 6px; letter-spacing: -0.01em;
  transition: color var(--transition);
}

.post-card:hover .post-title { color: var(--c-accent); }

.post-summary {
  font-size: 0.86rem; color: var(--c-text-3);
  line-height: 1.6; margin-bottom: 10px;
}

.post-arrow {
  font-size: 0.8rem; font-weight: 500; color: var(--c-accent);
  opacity: 0; transform: translateX(-6px);
  transition: all var(--transition);
}

.post-card:hover .post-arrow { opacity: 1; transform: translateX(0); }

/* ===== PROJECT CARDS ===== */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

.project-card {
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  padding: 20px;
  transition: all var(--transition);
}

.project-card:hover {
  border-color: var(--c-purple);
  box-shadow: 0 4px 14px -3px rgba(124,58,237,0.2);
  transform: translateY(-1px);
}

.project-icon {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, var(--c-accent-light), #ede9fe);
  border-radius: 10px;
  margin-bottom: 12px;
  color: var(--c-accent);
}

.project-icon svg { width: 18px; height: 18px; }

.project-card h3 {
  font-size: 0.95rem; font-weight: 600; color: var(--c-text);
  margin-bottom: 6px;
}

.project-card p {
  font-size: 0.82rem; color: var(--c-text-3); line-height: 1.5;
  margin-bottom: 12px;
}

.project-stats {
  display: flex; gap: 12px;
  font-size: 0.72rem; color: var(--c-text-4); font-weight: 500;
}

.project-stats span::before { content: ''; display: inline-block; width: 6px; height: 6px; border-radius: 50%; margin-right: 5px; vertical-align: 1px; }
.project-stats span:first-child::before { background: var(--c-accent); }
.project-stats span:last-child::before { background: var(--c-green); }

/* ===== ABOUT ===== */
.about-content { max-width: 560px; }
.about-content h2 { font-size: 1.15rem; font-weight: 600; color: var(--c-text); margin-bottom: 16px; }
.about-text p { margin-bottom: 10px; font-size: 0.9rem; color: var(--c-text-3); }

.tech-stack { margin-top: 28px; }
.tech-stack h3 { font-size: 0.92rem; font-weight: 600; color: var(--c-text); margin-bottom: 10px; }
.tech-tags { display: flex; flex-wrap: wrap; gap: 6px; }

.tech-tag {
  font-size: 0.76rem; font-weight: 500;
  color: var(--c-text-2);
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  padding: 4px 12px; border-radius: 6px;
  transition: all var(--transition);
}

.tech-tag:hover { border-color: var(--c-accent); color: var(--c-accent); background: var(--c-accent-light); }

.philosophy { margin-top: 28px; }
.philosophy h3 { font-size: 0.92rem; font-weight: 600; color: var(--c-text); margin-bottom: 10px; }

blockquote {
  border-left: 3px solid var(--c-accent);
  padding: 14px 18px;
  background: var(--c-surface);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-size: 0.88rem; color: var(--c-text-3);
  font-style: italic; line-height: 1.6;
}

/* ===== FOOTER ===== */
footer {
  border-top: 1px solid var(--c-border);
  padding: 24px 0;
  text-align: center;
  font-size: 0.76rem; color: var(--c-text-4);
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--c-border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--c-text-4); }

::selection { background: var(--c-accent-light); color: var(--c-accent-hover); }

/* ===== RESPONSIVE ===== */
@media (max-width: 640px) {
  header { padding: 36px 0 28px; }
  .site-title { font-size: 1.5rem; }
  .nav-inner { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .post-card { padding: 16px 18px; }
  .projects-grid { grid-template-columns: 1fr; }
}
"""


def _dark():
    return _light().replace(
        "--c-bg: #ffffff", "--c-bg: #0d1117"
    ).replace(
        "--c-surface: #f8fafc", "--c-surface: #0a0e14"
    ).replace(
        "--c-surface-2: #f1f5f9", "--c-surface-2: #161b22"
    ).replace(
        "--c-border: #e2e8f0", "--c-border: #21262d"
    ).replace(
        "--c-border-hover: #cbd5e1", "--c-border-hover: #30363d"
    ).replace(
        "--c-text: #0f172a", "--c-text: #f0f6fc"
    ).replace(
        "--c-text-2: #334155", "--c-text-2: #c9d1d9"
    ).replace(
        "--c-text-3: #64748b", "--c-text-3: #8b949e"
    ).replace(
        "--c-text-4: #94a3b8", "--c-text-4: #484f58"
    ).replace(
        "--c-accent-light: #dbeafe", "--c-accent-light: rgba(56,139,253,0.15)"
    ).replace(
        "rgba(255,255,255,0.85)", "rgba(10,14,20,0.85)"
    ).replace(
        "background: linear-gradient(135deg, var(--c-accent-light), #ede9fe)",
        "background: linear-gradient(135deg, rgba(56,139,253,0.12), rgba(124,58,237,0.12))"
    ).replace(
        "background: var(--c-accent-light); color: var(--c-accent-hover)",
        "background: rgba(56,139,253,0.3); color: var(--c-text)"
    )
