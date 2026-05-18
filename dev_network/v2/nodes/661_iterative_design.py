"""知识节点：迭代设计精炼——从Opus4.6的8轮演进记录提炼的设计方法论。

典型演进路径（光照系统案例，8轮对话）：
  轮1-2: 多概念分离→API表面积大但清晰
  轮3: 用户要求统一表达→四元组统一描述（参数化）
  轮5: 用户指出局限→通用内核model(I,material)（函数化）
  轮6: 用户三连纠正→与已有架构对齐（一致性）
  轮7-8: 收敛为4 Kind最终版

设计演进六阶段模型：
  Stage1: 枚举(列出所有独立概念)
  Stage2: 统一(找到一个结构表达所有行为)
  Stage3: 参数化(用参数覆盖变化维度)
  Stage4: 函数化(用函数替代固定公式)
  Stage5: 对齐(与已有系统架构一致)
  Stage6: 收敛(最终数量不多不少)

用户纠正的三种类型：
  A.本质纠正："光照本质是多体关系"→改变建模粒度
  B.术语纠正："三元组是你自制的"→消除自创概念
  C.功能纠正："光强应该能传播的更深"→扩展能力范围
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    # 判断当前设计处于哪个阶段
    stage = ask(
        system="你是设计阶段识别助手。",
        user=f"任务：{task}\n\n判断这个设计任务当前处于哪个阶段：\n"
             "1.枚举阶段(正在列出独立概念)\n"
             "2.统一阶段(寻找统一表达)\n"
             "3.参数化阶段(用参数覆盖变化)\n"
             "4.函数化阶段(用函数替代固定公式)\n"
             "5.对齐阶段(与已有架构保持一致)\n"
             "6.收敛阶段(确定最终形态)\n"
             "回答阶段编号和一句话理由。",
        max_tokens=100
    )

    ctx["_design_stage"] = stage.strip()

    ctx.setdefault("_design_principles", []).extend([
        "设计从枚举开始→统一→参数化→函数化→架构对齐→收敛",
        "用户每轮反馈都可能是关键转折——认真对待每个纠正",
        "自创概念违反架构对齐——与已有系统API模式保持一致",
        "归属判断标准=谁驱动了变化——按因果而非直觉归属",
        "统一表达诉求=降低API表面积——一个结构表达所有行为",
        "收敛判据：少一个无法覆盖场景，多一个出现概念重叠",
        "参数化→函数化是质变——从固定公式跳到通用内核",
    ])

    return ctx


node = Node(id="661", name="迭代设计精炼",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["设计", "迭代", "演进", "改进", "重构", "统一",
                          "简化", "方案", "对比"]},
    execute=execute, refs=["610"],
    metadata={"source": "Agent/develop-records", "category": "methodology"})
