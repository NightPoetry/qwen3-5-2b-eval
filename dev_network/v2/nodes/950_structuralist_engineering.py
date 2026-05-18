"""知识节点：结构主义工程化——从理论公理到可运行系统的实现路径。

将认知解构的四条公理翻译为具体的数据结构和算法选择：
  - 纯整数运算（边权i16，激活值i32）——CPU友好，无NaN/inf
  - 稀疏访问模式（只处理当前激活节点）——计算量随活跃子图自适应
  - 局部更新（无全局梯度）——所有学习都是共激活统计驱动
  - 可解释（图结构直接可读）——不是黑盒

关键实现选择：
  - 节点不存储"是知识/理解/经验"——这是动态属性
  - 边用稀疏CSR格式——内存是主瓶颈，边比节点占空间
  - 激活态用稀疏存储——绝大多数节点每时刻都是0
  - 冷启动从256字节叶节点开始——完全空图无法学习
  - BPE风格递归压缩自动产生字节→词→短语→句式层级
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    verdict = ask(
        system="你是系统架构评估助手。判断任务是否涉及底层架构选择。",
        user=f"任务：{task}\n\n这个任务是否涉及以下任何一项？回答是或否并说明理由。\n"
             "1.数据结构选择（稀疏vs稠密、整数vs浮点）\n"
             "2.内存/计算优化策略\n"
             "3.系统冷启动或初始化策略\n"
             "4.可解释性vs性能权衡",
        max_tokens=200
    )

    principles = [
        "整数运算优先——比浮点快2-3倍，无精度损失累积，可在低端硬件运行",
        "稀疏访问——典型激活节点数远小于总节点数(100-10000倍缩减)",
        "热路径数据集中在CPU cache——冷数据可放磁盘惰性加载",
        "SIMD友好的数据布局——激活节点和边权打包为连续数组",
        "多线程并行——不同子图的传播彼此独立，可按子图分片并行",
        "死循环三道防护——步数上限+激活衰减+死区阈值",
        "不追求完美子图同构检测——MDL多次观察会自愈",
    ]

    if "是" in verdict:
        ctx.setdefault("_design_principles", []).extend(principles)

    return ctx


node = Node(id="950", name="结构主义工程化",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["架构", "数据结构", "内存", "性能", "优化",
                          "稀疏", "整数", "CPU", "SIMD", "初始化"]},
    execute=execute, refs=["380", "500"],
    metadata={"source": "认知解构/04工程化实现+07开放问题+08再攻打", "category": "meta"})
