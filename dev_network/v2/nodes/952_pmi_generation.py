"""知识节点：PMI生成原则——兴奋与抑制统一的候选评分。

这是生成原则的理论更新：候选得分=语法基础×话题调制

问题根因：原始得分用原始频率→高频词(the/of)从任何词出发都最高→生成坍缩为高频循环。
缺少的关键概念："这个候选在当前上下文中有多特殊"=context specificity。

解决方案——PMI（逐点互信息）：
  PMI(B,context) = log P(B|context) / P(B)
  高频词(the): P(the)极高→PMI低→自然抑制
  话题词(Navy): P(Navy|French)>>P(Navy)→PMI高→被优选

  PMI>0 → 正边权 → 兴奋（组合特殊地常见）
  PMI=0 → 零边权 → 中性（独立，无关联）
  PMI<0 → 负边权 → 抑制（组合特殊地罕见）

这不是新机制——是公理A（边权可正可负）在生成端的完整启用。

实验教训：
  - softplus让score>0阈值失效（99%+候选混入）→删除softplus用硬阈值
  - T=1是bit单位下的自然温度→不需要额外temperature超参
  - prompt永驻不衰减=隐藏的无限激活→所有上下文统一按lambda^d衰减
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def execute(ctx: dict) -> dict:
    ctx.setdefault("_design_principles", []).extend([
        "候选评分=语法基础×话题调制——不是纯频率，是上下文特异性",
        "PMI自然区分兴奋和抑制——同一公式，不是两套机制",
        "高频词自然被PMI抑制——不需要额外的频率惩罚",
        "softplus类平滑可能让阈值完全失效——检查是否所有值都>0",
        "所有上下文统一按衰减率处理——不要有特殊的永驻激活",
        "模板循环的根因是某些激活永不衰减——不是n-gram重复问题",
    ])
    return ctx


node = Node(id="952", name="PMI生成原则",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["生成", "评分", "候选", "频率", "PMI", "互信息",
                          "高频", "重复", "循环"]},
    execute=execute, refs=["380", "500"],
    metadata={"source": "认知解构/15PMI与抑制+17温度消参+18序列MDL局限", "category": "meta"})
