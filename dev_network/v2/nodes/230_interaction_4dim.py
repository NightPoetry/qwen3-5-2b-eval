"""知识节点：交互设计四维度——最少决定/最少步骤/最自然/最少转折。

非代码生成节点。在Phase0交互设计后，系统按4维度检查交互列表质量。
交互设计的「最少决定」和「理解」方法的「最少前提」是同一种思维在不同领域的投影。
辅助风格三原则：拟物直觉/弹力恢复/轨道推动。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

DIMENSIONS = {
    "最少决定": {
        "check": "每个需要用户做决定的地方是否能合并/默认/延迟",
        "methods": ["合并相关决定到同一时机", "每项有默认值", "不紧急的推迟到之后"],
    },
    "最少步骤": {
        "check": "完成一个意图的操作次数",
        "methods": ["能在当前上下文完成的不跳转", "创建后自动选中", "高频操作单键"],
    },
    "最自然": {
        "check": "是否符合用户心理模型",
        "methods": ["空间即语义（位置暗示功能）", "感官一致（上行=增加）", "光标即模式"],
    },
    "最少转折": {
        "check": "上下文切换次数",
        "methods": ["操作完焦点在对的地方", "可逆不弹确认框", "模态窗可Enter跳过"],
    },
}

STYLE_PRINCIPLES = [
    "拟物直觉：UI元素表现得像实物，物理常识能预测反应（拿起东西时其他不该自己动）",
    "弹力恢复：任何过界操作无成本撤回原位（每次mousemove先恢复再重算，无累积误差）",
    "轨道推动：同类元素在同一容器互相推让不穿透（推一个后面整串顶走，遇铆钉停）",
]

DESIGN_PROCESS = [
    "1. 画出用户意图链（意图→步骤→每步决定）",
    "2. 对每个决定问：能合并？能消除？能延迟？",
    "3. 对每个保留的决定设计默认值",
    "4. 设计后续状态（操作完用户在哪，下一步最可能做什么）",
    "5. 自检：跑一遍急速用户路径+精细用户路径",
]

def execute(ctx: dict) -> dict:
    interactions = ctx.get("interactions", "")
    if not interactions:
        return ctx

    suggestions = []
    lines = [l.strip() for l in interactions.split("\n") if "→" in l]

    # 检查决定数
    decision_keywords = ["输入", "选择", "填写", "设置"]
    decisions = [l for l in lines if any(kw in l for kw in decision_keywords)]
    if len(decisions) > 3:
        suggestions.append(f"用户决定点{len(decisions)}个，建议合并/默认/延迟至3个以内")

    # 检查转折：是否有"先关闭再打开""切换到""找到"
    switch_keywords = ["切换", "找到", "跳转", "返回", "关闭再"]
    switches = [l for l in lines if any(kw in l for kw in switch_keywords)]
    if switches:
        suggestions.append(f"有{len(switches)}处上下文切换，考虑内联操作消除")

    if suggestions:
        ctx.setdefault("_interaction_review", []).extend(suggestions)

    # 注入风格原则和设计流程
    ctx.setdefault("_design_principles", []).extend(STYLE_PRINCIPLES)
    ctx.setdefault("_design_process", []).extend(DESIGN_PROCESS)

    return ctx

node = Node(id="230", name="交互四维度检查",
    trigger={"type": "key_exists", "key": "interactions"},
    execute=execute, refs=["110"],
    metadata={"source": "交互设计/SKILL", "category": "interaction"})
