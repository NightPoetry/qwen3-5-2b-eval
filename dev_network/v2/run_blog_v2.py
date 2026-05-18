"""
v2 商业级博客生成 — 模板系统碾压裸模型。

模型职责：只写纯文本内容（介绍、摘要）
系统职责：HTML结构+CSS样式+JS交互+验证修复

支持参数：--theme light/dark
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from llm import ask
from templates import blog_css, blog_html, blog_js


def gen_content():
    """模型只做内容生成（每次一个简单问题）。"""
    print("  [model] 个人介绍...")
    intro = ask(
        "只输出纯文本，不要markdown。",
        "写50字技术博客简介：你研究让小型AI模型通过系统编排完成复杂任务。",
        temperature=0.7, max_tokens=100
    ).strip()

    print("  [model] 博文摘要...")
    topics = [
        ("系统编排让2B模型写代码", "小模型如何通过管线分解完成复杂代码生成"),
        ("可执行知识网络", "从被动数据到主动程序的知识组织范式转变"),
        ("认知极限实验报告", "2B参数模型的能力边界和绕过策略"),
        ("事件层模板化", "用确定性代码取代模型生成达成100%正确率"),
        ("网状知识路由", "邻接可见和触发门控让知识按需激活"),
    ]

    posts = []
    for title, desc in topics:
        summary = ask(
            "只输出一句话（20字以内），不要标点以外的任何符号。",
            f"用一句话概括：{desc}",
            temperature=0.7, max_tokens=50
        ).strip().strip('"\'')
        posts.append({"title": title, "summary": summary})
        print(f"    [{title}] {summary[:30]}")

    return {
        "title": "AI Systems Research",
        "avatar_text": "AI",
        "intro": intro,
        "posts": posts,
        "projects": [
            {"name": "dev-network", "desc": "可执行知识网络引擎 — 31节点图驱动的代码生成框架",
             "lang": "Python", "stat": "31 nodes",
             "icon_path": "M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"},
            {"name": "cognitive-expansion", "desc": "认知展开器 — 将复合判断拆解为原子微问题序列",
             "lang": "Python", "stat": "100% accuracy",
             "icon_path": "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"},
            {"name": "system-orchestrated", "desc": "系统编排框架 — 2B模型达成6/6=100% F1的提取管线",
             "lang": "Python", "stat": "F1 = 1.00",
             "icon_path": "M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"},
        ],
        "tech_tags": ["Qwen3.5-2B", "Python", "System Orchestration",
                      "Knowledge Network", "Deterministic Validation", "LM Studio"],
        "about_extra": "核心发现：模型做不到100%的事交给程序。模型只负责语义理解，其余一切由代码完成。",
        "philosophy": "2B模型是单线程处理器。给它一件简单的事，它做得完美。给它两件事，它就崩。系统的工作是把复杂任务拆成一串简单问题。",
        "footer": "Powered by 2B Model + Executable Knowledge Network",
    }


def main():
    theme = "light"
    if "--dark" in sys.argv:
        theme = "dark"

    print(f"=== v2 商业级博客 ({theme}) ===\n")

    print("Step 1: 模型生成内容")
    content = gen_content()

    print(f"\nStep 2: 系统模板生成代码 ({theme})")
    html = blog_html.generate(content, theme)
    css = blog_css.generate(theme)
    js = blog_js.generate()
    print(f"  HTML: {len(html)} chars")
    print(f"  CSS:  {len(css)} chars")
    print(f"  JS:   {len(js)} chars")

    output_dir = Path(__file__).parent / f"output_blog_{theme}"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "index.html").write_text(html)
    (output_dir / "style.css").write_text(css)
    (output_dir / "app.js").write_text(js)

    print(f"\nStep 3: 保存到 {output_dir}")
    print("完成。")


if __name__ == "__main__":
    main()
