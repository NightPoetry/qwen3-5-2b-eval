"""知识节点：能力缺口检测——发现网络中缺失的知识领域。

信号：用户请求无节点匹配、执行轨迹过短（未覆盖到深层节点）、用户频繁纠正同类错误。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

GAP_SIGNALS = [
    "用户请求直接落到通用对话节点(890)，没有专业节点处理",
    "执行轨迹只有入口→域路由→通用输出，无中间专业节点",
    "用户在同一领域反复纠正，说明该领域知识不足",
    "节点输出被用户否定的比率高于平均",
    "用户明确说'你不懂这个''这个领域你不行'",
]

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    activation = ctx.get("_activation_analysis", "")

    gaps = ask(
        "根据以下信息，判断知识网络有哪些能力缺口：\n"
        "缺口信号：\n" + "\n".join(f"- {s}" for s in GAP_SIGNALS) + "\n\n"
        "如果发现缺口，描述缺什么类型的知识节点。\n"
        "如果没有明显缺口，回答'当前无明显缺口'。",
        f"轨迹分析：{activation[:300]}\n用户反馈：{task[:300]}",
        max_tokens=150
    ).strip()

    ctx["_detected_gaps"] = {
        "gaps": gaps,
        "signals_checked": GAP_SIGNALS,
    }
    return ctx

node = Node(id="761", name="能力缺口",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["缺什么", "缺口", "不懂", "不会", "能力不足",
                          "需要补充", "缺少节点"]},
    execute=execute, refs=["721"],
    metadata={"source": "distillation-pipeline/self-improvement", "category": "meta"})
