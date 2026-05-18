"""知识节点：超参数消除方法论——能从数据/结构推导的值不该硬编码。

核心原则（源自MDL比特账方法）：
  超参存在=用"假设"代替了"算账"。
  任何可以从比特数算出来的量，都不应该是超参。

三问消参法：
  Step1: 这个超参的本质是什么？
  Step2: 能不能用比特数表达？
  Step3: 能不能让数据自己决定？
  三问都得"能"→超参应该消掉。有"不能"→可能真的必需。

真正不可消的最小集（仅4个语言约定）：
  1.比特表示约定（每边权用多少bits、节点ID怎么分配）
  2.初始结构（完全空图无法启动，最简：256字节叶节点无边）
  3.激活函数形式（参数可由MDL学，形式本身需选）
  4.计算预算（何时停的物理约束，不是学习假设）

工程哲学差距：NN几十个超参=几十处"我猜"，本方法仅需少数"语言选择"。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

ELIMINATION_PATTERNS = [
    "硬编码数字 → 问：能从图/数据/结构推导吗？能就替换为推导公式",
    "TopK截断 → 如果有信息论阈值(score>0)就不需要额外截断",
    "context_window → 从衰减率推导有效窗口: lambda_auto(N) = (1/max_PMI)^(1/N)",
    "迭代次数 → 从层级深度推导(max_level+1)",
    "patch堆积 → 回退到纯公理模式，patch降级为opt-in",
    "softplus类平滑 → 检查是否让阈值失效（所有值都>0=阈值无用，实测99%+候选混入）",
    "边权增量 → 不需要DELTA超参，权重由计数自动决定: w=log(count(a,b)/count(a))",
    "衰减率 → 不需要DECAY_RATE，当累积节省<存储代价时自动剪枝",
    "凝聚阈值 → 不需要COMPRESSION_THRESHOLD，凝聚临界点=凝聚代价/单次节省",
    "槽位阈值 → 不需要ENTROPY_SLOT_THRESHOLD，用连续描述代价比较: L_enum(v)-L_param(v)",
    "学习率 → 自然年龄效应：图小时edge_cost小→易塑(快速学习)，图大时edge_cost大→保守(稳定)",
    "每次诱惑引入新超参时问自己：我能从比特数把它算出来吗？能就不要塞超参",
]

def execute(ctx: dict) -> dict:
    ctx.setdefault("_design_principles", []).extend(ELIMINATION_PATTERNS)
    return ctx

node = Node(id="500", name="超参消除方法论",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["参数", "阈值", "magic number", "配置", "常量", "硬编码",
                          "超参", "hyperparameter", "调参", "magic"]},
    execute=execute, refs=["380"],
    metadata={"source": "认知解构/09超参消除原则+17温度消参+19lambda双重身份", "category": "meta"})
