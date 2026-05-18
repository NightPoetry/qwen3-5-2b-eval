"""域抽象：推理域 — 纯路由，不调 LLM。

覆盖结构化推理、词义消歧、事实校准、多维验收。
关键：不包含"为什么"——这个词在对话域下路由到哲学节点(840)，不应进入推理域。
用户要显式分析时会说"分析一下"而不只是"为什么"。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    ctx["_domain_routed"] = True
    return ctx

node = Node(
    id="C00", name="推理域",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["分析", "推理", "区别",
                          "绑定", "模型", "状态", "渲染",
                          "词义", "词源", "介词", "固定搭配", "本义", "语法",
                          "博客", "论文", "声明", "报告",
                          "验收", "评估", "指标"],
             "unless": "_domain_routed"},
    execute=execute,
    refs=["300", "310", "320", "570", "580",
          "160", "190", "200", "210", "230", "231", "250",
          "410", "460", "661", "662", "722", "723",
          "760", "762", "763", "951", "952", "953",
          "970", "971", "973", "974", "990", "991", "992",
          "994", "996", "997", "998", "999"],
    metadata={"category": "domain", "layer": "abstraction"})
