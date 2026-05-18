"""节点：交互设计（Phase 0）"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Node
from llm import ask


def execute(ctx: dict) -> dict:
    task = ctx["task"]
    interactions = ask(
        "你是交互设计师。用最简方式描述用户和应用的交互。",
        (f"应用：{task}\n\n"
         "按以下格式描述交互（每行一个用户动作）：\n"
         "  用户动作 → 界面响应\n\n"
         "示例（计算器）：\n"
         "  点数字按钮 → 显示区追加数字\n"
         "  点运算符 → 保存当前数，等待下一个\n"
         "  点等号 → 计算结果显示\n\n"
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
