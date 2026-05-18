"""
测试：让 2B 模型通过系统编排完成"创建个人博客"。

每个子任务在隔离上下文中执行，模型一次只做一件简单的事。
知识卡从 Skills/ 和 Guild/ 注入相关规范。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orchestrator import Orchestrator, TaskPlan, SubTask

API_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-2b"

# 知识卡（从 Skills/UI设计 和 Guild 精简摘取）
KNOWLEDGE = {
    "html结构": """
HTML 页面基本结构要求：
- 使用语义化标签：header, nav, main, article, footer
- 必须有 meta viewport 适配移动端
- charset 使用 UTF-8
- 标题层级严格递减（h1 > h2 > h3）
""",
    "css布局": """
CSS 布局规范（横平竖直原则）：
- section padding: 12px 14px 最小
- 行间距: 8px
- 防溢出: flex 子元素加 min-width:0; overflow:hidden
- 文字截断: overflow:hidden; text-overflow:ellipsis
- 等分用 grid 不用 flex
- 禁止浏览器原生样式透出（加 reset）
- 间距甜区: 8-14px
""",
    "响应式": """
响应式设计要点：
- 移动优先: 默认样式针对手机，@media(min-width:768px) 加桌面样式
- max-width 限制内容区宽度（如 800px）
- margin: 0 auto 居中
- 图片 max-width: 100%
""",
    "博客内容": """
个人博客需要的页面和内容：
- 首页: 文章列表（标题+日期+摘要）
- 文章页: 正文+返回链接
- 关于页: 个人介绍
- 导航: 首页 | 关于
- 底部: 版权信息
""",
}


def create_blog_plan() -> TaskPlan:
    """创建博客任务分解计划"""
    return TaskPlan(
        goal="创建一个简洁美观的个人博客静态页面",
        subtasks=[
            SubTask(
                id="html",
                name="HTML 结构",
                description=(
                    "创建一个个人博客的 index.html。\n"
                    "要求：\n"
                    "- 用 <link rel='stylesheet' href='style.css'> 引用外部样式，不要写内联 <style>\n"
                    "- 导航链接: <a href='index.html'>首页</a> <a href='about.html'>关于</a>\n"
                    "- 3篇示例文章（标题+日期+摘要），用 <article> 包裹\n"
                    "- 页脚用 <footer>\n"
                    "- 使用语义化标签。添加 viewport meta\n"
                    "- 文章内容用中文"
                ),
                knowledge_keys=["html结构", "博客内容"],
            ),
            SubTask(
                id="css",
                name="CSS 样式",
                description=(
                    "为博客页面编写完整的 style.css 文件。\n"
                    "只输出纯 CSS 代码（不要 HTML，不要 ```css 标记）。\n"
                    "要求：\n"
                    "- 简洁现代风格，浅色背景(#f5f5f5)，深色文字(#333)\n"
                    "- 内容区 max-width:800px 居中\n"
                    "- 导航栏 position:sticky 固定顶部\n"
                    "- 文章卡片白色背景、圆角、间距\n"
                    "- 移动端 @media(max-width:768px) 适配"
                ),
                depends_on=["html"],
                knowledge_keys=["css布局", "响应式"],
            ),
            SubTask(
                id="about",
                name="关于页面",
                description=(
                    "创建 about.html（关于页面）。\n"
                    "要求：\n"
                    "- 和 index.html 用完全相同的 head/header/footer 结构\n"
                    "- 用 <link rel='stylesheet' href='style.css'> 引用外部样式\n"
                    "- 导航链接: <a href='index.html'>首页</a> <a href='about.html'>关于</a>\n"
                    "- 主体内容: 虚构一个中国开发者的个人简介（姓名、技术栈、兴趣）\n"
                    "- 不要写内联 <style>"
                ),
                depends_on=["html"],
                knowledge_keys=["html结构", "博客内容"],
            ),
        ],
    )


def main():
    orch = Orchestrator(API_URL, MODEL)

    # 注入知识卡
    for key, content in KNOWLEDGE.items():
        orch.load_knowledge(key, content)

    # 创建并执行计划
    plan = create_blog_plan()
    outputs = orch.execute_plan(plan, verbose=True)

    # 输出结果
    print(f"\n{'='*60}")
    print("生成结果")
    print(f"{'='*60}")

    output_dir = Path(__file__).parent / "output_blog"
    output_dir.mkdir(exist_ok=True)

    file_map = {"html": "index.html", "css": "style.css", "about": "about.html"}
    for task_id, filename in file_map.items():
        if task_id in outputs:
            content = outputs[task_id]
            # 提取代码块内容（如果模型输出了 markdown 代码块）
            if "```" in content:
                import re
                blocks = re.findall(r'```(?:\w+)?\n(.*?)```', content, re.DOTALL)
                if blocks:
                    content = blocks[0]
            (output_dir / filename).write_text(content)
            print(f"\n  {filename} ({len(content)} chars):")
            print(f"  {content[:200]}...")

    print(f"\n文件已保存到: {output_dir}")


if __name__ == "__main__":
    main()
