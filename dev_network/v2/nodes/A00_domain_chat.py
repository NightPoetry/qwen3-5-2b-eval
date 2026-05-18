"""域抽象：对话域 — 纯路由，不调 LLM。

所有对话类节点的入口。regex 匹配中文文本作为兜底。
位于 000.refs 的最后一个 = 栈优先级最低 = 只在工程/推理/创作都不匹配时才触发。
unless: _domain_routed 确保每轮只有一个域激活。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    ctx["_domain_routed"] = True
    return ctx

node = Node(
    id="A00", name="对话域",
    trigger={"type": "regex", "target": "task",
             "pattern": "[\\u4e00-\\u9fff]",
             "unless": "_domain_routed"},
    execute=execute,
    refs=["810", "820", "830", "840", "850", "870", "860", "800", "880", "890",
          "903", "906", "907", "908"],
    metadata={"category": "domain", "layer": "abstraction"})
