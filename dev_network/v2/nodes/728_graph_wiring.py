"""知识节点：图连接设计——为新节点设计refs和触发条件的图拓扑关系。

refs = 这个节点能看到谁。决定了知识在网络中的传播路径。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

WIRING_RULES = [
    "因果关系：A的输出是B的输入 → A.refs包含B",
    "互补关系：A和B共同处理同类问题 → 互相refs",
    "层级关系：A是B的前置检查 → A.refs包含B",
    "输出收口：叶节点必须refs到Y10/Y20/Y30/Y40之一",
    "不连不相关的节点——邻接=可见性，refs太多=选择压力",
    "角色节点→对应输出(Y10对话/Y20代码/Y30分析/Y40创作)",
    "新建节点必须被至少一个现有节点的refs引用，否则永远不会被执行到",
]

def execute(ctx: dict) -> dict:
    synthesized = ctx.get("_synthesized", {})
    if synthesized.get("action") == "skip":
        return ctx

    category = synthesized.get("category", "")
    name = synthesized.get("name", "")

    wiring = ask(
        "为新节点设计图连接。\n"
        "规则：\n" + "\n".join(f"- {r}" for r in WIRING_RULES) + "\n\n"
        "回答格式：refs=[节点ID列表]|应被哪个上游节点引用",
        f"新节点：{name}（类别：{category}）",
        max_tokens=60
    ).strip()

    synthesized["wiring"] = wiring
    synthesized["wiring_rules"] = WIRING_RULES
    ctx["_synthesized"] = synthesized
    return ctx

node = Node(id="728", name="图连接设计",
    trigger={"type": "key_exists", "key": "_synthesized"},
    execute=execute, refs=["729"],
    metadata={"source": "distillation-pipeline/generation", "category": "meta"})
