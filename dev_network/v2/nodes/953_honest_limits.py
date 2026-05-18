"""知识节点：诚实边界——理论和系统的真实限制清单。

结构主义的内在限制：
  - 全新概念无法生成——任何输出必然是已有子拓扑的某种组合
  - 创造性的本质=已有结构的远距离组合，不是真正的无中生有
  - 这与人类认知的实际限制一致

真正的理论缺口（实证问题，理论给不出答案）：
  1.激活函数形式——不同选择可能导致某些任务根本行不通
  2.全局归一化——"激活预算+侧抑制=softmax功能等价"未被实证
  3.稀疏attention可行性——某些任务可能需要稠密远程关联
  4.算法性计算——部分通过教材化训练降级(结构化数据输入)
  5.学习质量——框架是否能达到LLM级别生成质量？必须靠实证

诚实盘点原则：
  - 理论是一套自洽的猜想，完整性是逻辑层面的不是实证层面的
  - 内部一致性通过≠实际工作
  - 实证验证=零时不要声称"证明了"
  - 区分"理论可能"和"工程可行"
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    verdict = ask(
        system="你是可行性评估助手。",
        user=f"任务：{task}\n\n这个任务是否可能超出当前系统的能力边界？"
             "考虑以下限制：\n"
             "1.系统只能组合已有知识，不能创造全新概念\n"
             "2.精确数值计算需要程序化而非模型推理\n"
             "3.长距离跨文档关联可能不可靠\n"
             "回答是或否，简述理由。",
        max_tokens=150
    )

    if "是" in verdict:
        ctx.setdefault("_warnings", []).append(
            f"任务可能触及系统边界：{verdict.strip()}"
        )

    ctx.setdefault("_design_principles", []).extend([
        "诚实承认限制——不假装拥有没有的能力",
        "全新概念无法生成——但远距离组合能产生看似全新的结果",
        "精确计算用程序化——判断和执行分离",
        "理论自洽≠实际工作——需要实证验证",
    ])

    return ctx


node = Node(id="953", name="诚实边界检查",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["能不能", "是否可能", "限制", "边界", "极限",
                          "做不到", "impossible"]},
    execute=execute, refs=["380"],
    metadata={"source": "认知解构/11诚实盘点+08开放问题再攻打", "category": "meta"})
