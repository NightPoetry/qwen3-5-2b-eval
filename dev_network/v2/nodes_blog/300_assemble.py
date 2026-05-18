"""组装节点 — 收集所有碎片拼成完整HTML。不含业务逻辑。"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify": return ctx

    h = ctx.get("html_fragments", {})
    c = ctx.get("css_fragments", {})

    # 预设覆盖：如果有已保存的预设碎片，用预设替换默认
    preset = ctx.get("_preset", {})
    if "html_fragments" in preset:
        h.update(preset["html_fragments"])
    if "css_fragments" in preset:
        c.update(preset["css_fragments"])

    # 按key排序拼接CSS
    css_text = "\n".join(c[k] for k in sorted(c.keys()))

    # 按固定顺序拼接HTML
    html_order = ["header", "nav", "posts", "projects", "about", "footer"]
    body_parts = "\n".join(h.get(k, "") for k in html_order if k in h)

    title = ctx.get("blog", {}).get("title", "Blog")

    ctx["html"] = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
{css_text}
</style>
</head>
<body>
{body_parts}
</body>
</html>"""
    return ctx

node = Node(id="300_a", name="碎片组装",
    trigger={"type": "key_exists", "key": "html_fragments"},
    execute=execute, refs=["900_o"])
