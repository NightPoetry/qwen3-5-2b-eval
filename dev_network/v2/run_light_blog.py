"""
亮色博客测试 — CSS完全由模型生成，看2B能不能做出好看的亮色主题。
"""

import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from engine import Engine
from llm import ask


def main():
    print("=== 亮色博客生成（CSS由模型生成） ===\n")

    # Step 1: 模型生成CSS
    print("Step 1: 模型生成亮色CSS...")
    raw_css = ask(
        "你是 CSS 开发者。只输出纯 CSS 代码，不要 HTML，不要 markdown。",
        ("为一个精美的个人技术博客编写亮色主题CSS。\n\n"
         "要求：\n"
         "  - 白色或浅灰背景，深色文字\n"
         "  - max-width:720px 居中\n"
         "  - 现代简洁风格，有呼吸感\n"
         "  - 卡片有浅色阴影和圆角\n"
         "  - 导航栏横排\n"
         "  - 标题用渐变色\n"
         "  - 按钮和标签用品牌蓝色 #2563eb\n"
         "  - body字体用 -apple-system, sans-serif\n"
         "  - 间距用 8px 的倍数\n\n"
         "需要的选择器：\n"
         "  body, header, .site-title, .site-subtitle\n"
         "  .nav-bar, .nav-item, .nav-item.active\n"
         "  .section, .section.active\n"
         "  .post-card, .post-card:hover, .post-title, .post-summary, .post-date, .post-tag\n"
         "  .project-card, .project-icon, .tech-tag\n"
         "  blockquote, footer\n\n"
         "写完整的CSS："),
        temperature=0.3,
        max_tokens=2048
    )

    # 清理
    if "```" in raw_css:
        blocks = re.findall(r'```(?:\w+)?\n(.*?)```', raw_css, re.DOTALL)
        if blocks:
            raw_css = blocks[0]

    print(f"  模型输出: {len(raw_css)} chars")

    # Step 2: 通过知识节点验证修复
    print("\nStep 2: 知识节点验证...")
    engine = Engine()
    engine.load_from_dir(Path(__file__).parent / "nodes")

    ctx = {
        "task": "亮色博客",
        "css": raw_css,
        "raw_css": raw_css,
        "html": "",
        "js": "",
        "contract": {"elements": []},
        "interactions": "",
    }

    # 跑CSS相关知识节点
    for nid in ["121", "122", "210"]:
        node = engine.nodes.get(nid)
        if node and engine.check_trigger(node, ctx):
            ctx = node.execute(ctx)
            print(f"  [{nid}] {node.name}")

    final_css = ctx.get("css", raw_css)
    print(f"  修复后: {len(final_css)} chars")

    if ctx.get("_style_fixes"):
        for fix in ctx["_style_fixes"]:
            print(f"    - {fix}")

    # Step 3: 用同样的HTML结构（从暗色版复制，只换CSS）
    print("\nStep 3: 组装...")
    blog_dir = Path(__file__).parent / "output_blog"
    html = (blog_dir / "index.html").read_text() if (blog_dir / "index.html").exists() else ""
    js = (blog_dir / "app.js").read_text() if (blog_dir / "app.js").exists() else ""

    # 保存
    output_dir = Path(__file__).parent / "output_blog_light"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "index.html").write_text(html)
    (output_dir / "style.css").write_text(final_css)
    (output_dir / "app.js").write_text(js)

    print(f"\n保存到: {output_dir}")
    print("完成。")


if __name__ == "__main__":
    main()
