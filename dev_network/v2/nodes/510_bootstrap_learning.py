"""知识节点：自举学习——系统用自己的输出改进自己。

自举形式化：
  1. 系统S有基础能力C
  2. S用C生成新数据D'（含C的应用痕迹——隐式的跨段、跨实体模式）
  3. S重训吸收D'→涌现新能力C'>C
  4. 用C'生成D''→涌现C''>C'...递归自举

自举三条件：
  (a) 当前能力足以产生C'的雏形数据（不是纯噪声）
  (b) 学习算法能从雏形中蒸馏出C'（MDL普适学习满足）
  (c) 雏形→C'的提升单调正向（不会越自举越糟）

重复消除进阶（survival pressure方法）：
  - 重复是数据稀疏的征兆，不是bug
  - think/content交替：think段是可被自己读到的元状态（工作记忆）
  - 所有重复都判定为退化，强迫模型用think段自我证明合法重复
  - LLM在重复点动态蒸馏think段（context-aware，非周期性废话）
  - 把"分类问题"消成"行动问题"，把"程序判断"消成"训练压力"

在编排系统中的对应：
  用户保存预设→系统获得新模板→下次生成更好→用户保存更好的预设
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    ctx.setdefault("_design_principles", []).extend([
        "自举种子质量决定上限——确保初始模板/数据足够好",
        "每轮自举必须有质量门控——生成质量下降时停止自举",
        "数据不足时补数据比调算法有效——量变带来质变",
        "patch堆积是自举退化的信号——回退到纯公理模式",
        "跨段失效不是架构问题是数据问题——自生成数据+重训可涌现新层级",
        "MDL自带正则——噪声不会反复出现，自然被忽略；不过滤可能也OK",
        "重复是数据稀疏征兆——不要当bug修，要让系统意识到自己在重复",
        "think段是工作记忆——把无状态前向变成带工作记忆的状态机",
        "消除合法vs退化的分类难题——全判退化，强迫模型用think自证合法",
        "教材化训练=预结构化数据——概念有序定义+例题演示+练习强化",
    ])
    return ctx

node = Node(id="510", name="自举学习原则",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["自举", "bootstrap", "自我改进", "迭代", "训练",
                          "重复", "退化", "蒸馏", "distill"]},
    execute=execute, refs=["500"],
    metadata={"source": "认知解构/20自举学习+21重复检测survival_pressure+12教材化训练", "category": "meta"})
