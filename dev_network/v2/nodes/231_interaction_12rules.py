"""知识节点：交互设计12条通用规则（从案例提取）。

在Phase2契约生成后注入适用的规则到契约。
反模式：每个删除都弹确认框/创建后清空选中/多步分散属性/图标无tooltip/操作无反馈/强制填非关键字段。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

RULES = [
    {"trigger": ["创建", "新建", "添加"], "rule": "创建型对话框包含所有此刻自然想到的配置项，每项有默认值"},
    {"trigger": ["创建", "新建", "添加"], "rule": "创建完成后对象自动选中，进入可编辑状态"},
    {"trigger": ["保存", "导出", "下载"], "rule": "文件保存对话框预判最可能的路径和文件名"},
    {"trigger": ["导出", "处理", "生成", "上传"], "rule": "长操作完成后多通道通知(视觉+听觉+系统)+预判下一步操作"},
    {"trigger": ["删除", "移除"], "rule": "可逆操作直接执行+撤销，不弹确认框"},
    {"trigger": ["删除", "合并", "覆盖"], "rule": "信息丢失型操作必须二次确认（将不同值抹成统一值=不可逆损失）"},
    {"trigger": ["拖拽", "吸附", "snap"], "rule": "音效标记状态跃迁（进入时响一次），不标记状态本身（用lastSnap去重）"},
    {"trigger": ["列表", "面板"], "rule": "内容量不可控区域必须有固定最大尺寸+内部滚动+可拖拽分割线+最小尺寸保底"},
    {"trigger": ["工具", "按钮", "图标"], "rule": "纯图标按钮必须有tooltip（工具名+一句话说明+快捷键）"},
    {"trigger": ["批量", "多选", "全选"], "rule": "单个操作必须有对应的批量操作方式（Shift多选+批量调整）"},
    {"trigger": ["列表", "类型", "分类"], "rule": "不同类型列表项用颜色+图标+内容三维度区分"},
    {"trigger": ["输入", "表单"], "rule": "每个输入字段有合理默认值，全跳过不出错"},
    {"trigger": ["迭代", "调试", "感觉"], "rule": "先做严格版本再根据实测放宽（先关再加，迭代收敛更快）"},
    {"trigger": ["拖拽", "拖动"], "rule": "拖动中每帧先恢复到mousedown原位再重算（弹力恢复，无累积误差）"},
]

def execute(ctx: dict) -> dict:
    interactions = ctx.get("interactions", "")
    task = ctx.get("task", "")
    combined = interactions + " " + task

    applicable = []
    for r in RULES:
        if any(kw in combined for kw in r["trigger"]):
            applicable.append(r["rule"])

    if applicable:
        contract = ctx.get("contract", {})
        contract.setdefault("interaction_patterns", []).extend(applicable)
        ctx["contract"] = contract

    return ctx

node = Node(id="231", name="12条交互规则",
    trigger={"type": "key_exists", "key": "interactions"},
    execute=execute, refs=["Y10"],
    metadata={"source": "交互设计/EXAMPLES", "category": "interaction"})
