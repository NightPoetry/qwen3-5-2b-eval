"""修改路由 — 解析修改意图，分发到子节点。"""
import re
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

COLOR_SWAPS = {
    "to_dark": {
        "#f8fafc": "#0d1117", "#ffffff": "#161b22", "#e2e8f0": "#21262d",
        "#0f172a": "#f0f6fc", "#334155": "#c9d1d9", "#64748b": "#8b949e",
        "#94a3b8": "#484f58", "#2563eb": "#388bfd", "#dbeafe": "rgba(56,139,253,0.15)",
        "#7c3aed": "#a855f7",
        "rgba(255,255,255,0.85)": "rgba(13,17,23,0.85)",
        "rgba(37,99,235,": "rgba(56,139,253,",
    },
    "to_light": {
        "#0d1117": "#f8fafc", "#161b22": "#ffffff", "#21262d": "#e2e8f0",
        "#f0f6fc": "#0f172a", "#c9d1d9": "#334155", "#8b949e": "#64748b",
        "#484f58": "#94a3b8", "#388bfd": "#2563eb",
        "rgba(56,139,253,0.15)": "#dbeafe", "#a855f7": "#7c3aed",
        "rgba(13,17,23,0.85)": "rgba(255,255,255,0.85)",
        "rgba(56,139,253,": "rgba(37,99,235,",
    },
}

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") != "modify": return ctx

    html = ctx.get("existing_html", "")
    task = ctx.get("task", "")
    changes = []

    # 主题切换
    if any(kw in task for kw in ["暗色", "dark", "深色"]):
        for old, new in COLOR_SWAPS["to_dark"].items():
            html = html.replace(old, new)
        changes.append("切换为暗色主题")
    elif any(kw in task for kw in ["亮色", "light", "白色"]):
        for old, new in COLOR_SWAPS["to_light"].items():
            html = html.replace(old, new)
        changes.append("切换为亮色主题")

    # 布局修改
    layout_map = {
        "两列": "repeat(2,1fr)", "三列": "repeat(3,1fr)",
        "单列": "1fr", "网格": "repeat(auto-fill,minmax(280px,1fr))",
    }
    for kw, grid in layout_map.items():
        if kw in task:
            # 给posts section加grid
            html = re.sub(
                r'(<section id="posts"[^>]*>)',
                f'<section id="posts" style="display:grid;grid-template-columns:{grid};gap:12px">',
                html
            )
            # 去掉card的margin-bottom（grid用gap代替）
            html = re.sub(r'(\.card\{[^}]*?)margin-bottom:\d+px', r'\1margin-bottom:0', html)
            changes.append(f"布局改为{kw}")
            break

    # 标题修改
    if any(kw in task for kw in ["标题", "改名", "名字"]):
        from llm import ask
        new_title = ask("只输出纯文本，不要标记。",
            f"根据要求修改博客标题：{task}", temperature=0.7, max_tokens=30).strip()
        html = re.sub(r'(<h1>)(.*?)(</h1>)', rf'\1{new_title}\3', html)
        html = re.sub(r'(<title>)(.*?)(</title>)', rf'\1{new_title}\3', html)
        changes.append(f"标题改为：{new_title}")

    # 介绍修改
    if any(kw in task for kw in ["介绍", "简介", "描述"]):
        from llm import ask
        new_intro = ask("只输出纯文本50字。",
            f"根据要求重写简介：{task}", temperature=0.7, max_tokens=100).strip()
        html = re.sub(r'(<p class="sub">)(.*?)(</p>)', rf'\1{new_intro}\3', html)
        changes.append("介绍已更新")

    ctx["html"] = html
    ctx["_changes"] = changes
    return ctx

node = Node(id="400_m", name="修改路由",
    trigger={"type": "key_exists", "key": "existing_html"},
    execute=execute, refs=["900_o"])
