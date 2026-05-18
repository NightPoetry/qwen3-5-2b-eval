"""知识节点：资源预算守门——限制单次任务的资源消耗。"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

BUDGET_RULES = {
    "api_calls": {"max": 20, "desc": "单次管线最多20次模型调用"},
    "output_size": {"max": 50000, "desc": "单次输出最大50KB"},
    "node_visits": {"max": 50, "desc": "单次执行最多访问50个节点"},
}

def execute(ctx: dict) -> dict:
    ctx.setdefault("_budget", {})
    for key, rule in BUDGET_RULES.items():
        ctx["_budget"][key] = rule
    return ctx

node = Node(id="430", name="资源预算",
    trigger={"type": "always"},
    execute=execute, refs=["Y30"],
    metadata={"source": "Guild/资源预算守门", "category": "safety"})
