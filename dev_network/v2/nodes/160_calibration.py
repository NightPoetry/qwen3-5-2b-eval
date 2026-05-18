"""知识节点：事实校准 — 用LLM检查生成内容中的不准确声明。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

def execute(ctx: dict) -> dict:
    texts = []
    for field in ["intro", "posts", "content_text"]:
        content = ctx.get(field)
        if content:
            texts.append(f"[{field}] {str(content)}")
    if not texts:
        return ctx

    result = ask(
        "你是内容审校员。检查以下生成内容中是否有未经验证的数字、比较或声明需要校准。"
        "如果有，列出需要校准的具体内容。如果没有，只回答'无'。",
        f"生成内容：\n{chr(10).join(texts)[:800]}",
        max_tokens=200
    ).strip()

    if result and result != "无":
        ctx.setdefault("_calibration", []).append(result)
    return ctx


node = Node(
    id="160",
    name="事实校准",
    trigger={"type": "keyword", "target": "_input",
             "keywords": ["博客", "文章", "报告", "介绍", "blog"]},
    execute=execute,
    refs=["Y30"],
    metadata={"source": "校准/system_prompt", "category": "reasoning"},
)
