"""知识节点：内容创作——当任务是写文章/诗/文案时，模型在节点内完成。"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    result = ask(
        "根据用户要求创作内容。直接输出创作结果，不要解释。",
        task,
        temperature=0.7,
        max_tokens=500
    )

    ctx["_creative_output"] = result.strip()
    return ctx

node = Node(id="700", name="内容创作",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["写", "创作", "生成", "编写", "诗", "文案", "口号",
                          "故事", "段落", "开头", "文章"]},
    execute=execute, refs=["320", "Y40"],
    metadata={"source": "通用", "category": "creation"})
