"""知识节点：并行执行优化——从双轨记录提炼的并行化方法论。

并行化的核心规则（来自双轨order语义）：
  - 相同order的操作可以并行——前提是它们之间无数据依赖
  - 正数从小到大顺序执行
  - 负数从大到小顺序执行（渲染等最后执行的用-1）
  - 依赖标注是并行安全的关键——"T05依赖T02+T03"必须显式标注

Fix模式中的并行机会：
  - F03并行排除：编译产物/缓存/配置/环境同时检查
  - F07并行修复：独立的修改点可同时进行
  - T03+T04并行：检查前端编码和后端解码可同时进行

Develop模式中的并行机会：
  - D03并行方案设计：多个方案可同时设计
  - D05并行实现：独立子任务可拆分并行
  - T03+T04并行：扩容方案和缩容方案可同时设计

跨盘传输并行案例（数据迁移项目）：
  - exFAT→APFS跨盘mv实际是cp+rm，速度8-30MB/s
  - 大文件传输后台并行，前台处理配置更新
  - 先备份后移动——编号管理注明来源

多Agent翻译并行案例：
  - 6个Agent并行审校42个文件
  - 每个Agent独立分配文件，无交叉依赖
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    # 判断任务是否有并行机会
    verdict = ask(
        system="你是任务并行化分析助手。",
        user=f"任务：{task}\n\n分析这个任务中有哪些操作可以并行执行。\n"
             "规则：两个操作可以并行，当且仅当它们之间无数据依赖。\n"
             "列出可并行的操作组（如果有）。如果全部串行则说明原因。",
        max_tokens=200
    )

    ctx["_parallel_analysis"] = verdict.strip()

    ctx.setdefault("_design_principles", []).extend([
        "相同order可并行——前提是无数据依赖",
        "依赖标注是并行安全的关键——必须显式标注",
        "大文件传输后台进行——前台处理配置和验证",
        "先备份后操作——防止单点失败导致数据丢失",
        "独立子任务可拆分给多个执行者——每人独立分配无交叉",
    ])

    return ctx


node = Node(id="662", name="并行执行优化",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["并行", "parallel", "同时", "批量", "拆分",
                          "多线程", "concurrent"]},
    execute=execute, refs=["630"],
    metadata={"source": "Agent/双轨order并行语义+Opus4.6数据迁移+翻译并行", "category": "methodology"})
