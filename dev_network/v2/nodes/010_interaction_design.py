"""节点：交互设计（Phase 0）"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Node
from llm import ask


def execute(ctx: dict) -> dict:
    task = ctx["task"]
    interactions = ask(
        "你是交互设计师。先理解用户要做什么类型的应用，再描述交互。\n"
        "重要：先用一句话说明这个应用的核心功能是什么，然后再列交互。",
        (f"用户要求：{task}\n\n"
         "第一步：用一句话描述这个应用的核心功能。\n"
         "第二步：按以下格式描述用户和应用的交互（每行一个）：\n"
         "  用户动作 → 界面响应\n\n"
         "示例（个人博客）：\n"
         "  核心功能：展示个人文章、项目和自我介绍的静态网站\n"
         "  访问首页 → 显示文章列表和导航\n"
         "  点击文章标题 → 展开文章正文\n"
         "  点击导航链接 → 切换到对应页面\n\n"
         "现在描述："),
        max_tokens=300
    )
    ctx["interactions"] = interactions
    return ctx


node = Node(
    id="010",
    name="交互设计",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["应用", "app", "网页", "页面", "工具", "系统",
                          "待办", "博客", "编辑器", "计算器", "看板"]},
    execute=execute,
    refs=["020", "150", "180"],
)
