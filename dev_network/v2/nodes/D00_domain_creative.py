"""域抽象：创作域 — 纯路由，不调 LLM。"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    ctx["_domain_routed"] = True
    return ctx

node = Node(
    id="D00", name="创作域",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["写", "创作", "生成", "编写", "诗", "文案",
                          "口号", "故事", "段落", "开头", "文章"],
             "unless": "_domain_routed"},
    execute=execute,
    refs=["700", "973"],
    metadata={"category": "domain", "layer": "abstraction"})
