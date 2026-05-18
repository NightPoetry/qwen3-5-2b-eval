"""知识节点：重复检测——检查待蒸馏知识是否已存在于网络中。

避免创建重复节点。如果知识已被覆盖，标记为"增强"而非"新建"。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

def execute(ctx: dict) -> dict:
    classified = ctx.get("_knowledge_classified", {})
    knowledge = classified.get("raw_knowledge", "")
    if not knowledge:
        return ctx

    existing_nodes = ctx.get("_node_index", "")

    verdict = ask(
        "这条新知识是否已被现有节点网络覆盖？\n"
        "回答：完全覆盖（跳过）/ 部分覆盖（增强现有节点）/ 未覆盖（新建节点）\n"
        "如果部分覆盖或完全覆盖，指出最相关的现有节点。",
        f"新知识：{knowledge[:300]}\n\n现有节点概览：{str(existing_nodes)[:500]}",
        max_tokens=60
    ).strip()

    ctx["_duplicate_check"] = {
        "verdict": verdict,
        "action": "skip" if "完全覆盖" in verdict or "跳过" in verdict
                  else "enhance" if "部分" in verdict or "增强" in verdict
                  else "create",
    }
    return ctx

node = Node(id="725", name="重复检测",
    trigger={"type": "key_exists", "key": "_knowledge_classified"},
    execute=execute, refs=["726"],
    metadata={"source": "distillation-pipeline/processing", "category": "meta"})
