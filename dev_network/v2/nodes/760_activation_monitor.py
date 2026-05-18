"""知识节点：激活监控——分析节点执行轨迹，发现网络行为模式。

从trace中提取：高频节点、从未激活的节点、频繁失败的节点、执行路径瓶颈。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

def execute(ctx: dict) -> dict:
    trace = ctx.get("_trace_history", "")
    if not trace:
        return ctx

    analysis = ask(
        "分析这些节点执行轨迹，发现模式：\n"
        "1. 哪些节点被频繁激活？（热点）\n"
        "2. 哪些节点从未被激活？（可能trigger太严或知识过时）\n"
        "3. 哪些节点频繁出错？（需要修复）\n"
        "4. 有没有执行路径的死胡同？（refs缺失导致无后续）\n"
        "简洁列出发现。",
        f"轨迹数据：{str(trace)[:800]}",
        max_tokens=200
    ).strip()

    ctx["_activation_analysis"] = analysis
    return ctx

node = Node(id="760", name="激活监控",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["分析轨迹", "节点统计", "执行分析", "监控",
                          "哪些节点", "激活率"]},
    execute=execute, refs=["761"],
    metadata={"source": "distillation-pipeline/self-improvement", "category": "meta"})
