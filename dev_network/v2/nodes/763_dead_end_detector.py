"""知识节点：死区检测——发现节点网络中的死胡同和孤立节点。

死区 = 节点被激活后没有后续去处（refs为空或refs指向的节点全部trigger不满足）。
孤立 = 没有任何节点的refs指向它，永远不会被执行到。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

DEAD_END_TYPES = [
    "refs为空且不是输出节点(Y*) → 执行到这里就停了",
    "refs指向的所有节点trigger条件过严 → 实际上等于死胡同",
    "没有任何上游节点refs引用 → 永远不会被栈展开触发",
    "循环refs但visited阻止 → 一次执行只经过一次，可能遗漏",
    "trigger关键词与实际用户输入模式不匹配 → 名义上可达但实际不被触发",
]

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    trace = ctx.get("_trace_history", "")

    analysis = ask(
        "分析以下执行轨迹或节点配置，检测是否有死区问题：\n"
        "死区类型：\n" + "\n".join(f"- {d}" for d in DEAD_END_TYPES) + "\n\n"
        "如果发现死区，说明哪个节点、什么类型的死区、建议如何修复。\n"
        "如果没有死区，回答'未检测到死区'。",
        f"内容：{task[:300]}\n轨迹：{str(trace)[:500]}",
        max_tokens=200
    ).strip()

    ctx["_dead_ends"] = {
        "analysis": analysis,
        "has_dead_ends": "未检测到" not in analysis,
        "types_checked": DEAD_END_TYPES,
    }
    return ctx

node = Node(id="763", name="死区检测",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["死区", "死胡同", "孤立", "不可达", "没有去处",
                          "断开", "dead end"]},
    execute=execute, refs=["728", "Y30"],
    metadata={"source": "distillation-pipeline/self-improvement", "category": "meta"})
