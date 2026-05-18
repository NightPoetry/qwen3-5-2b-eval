"""知识节点：操作反馈模式 — 长操作多通道通知 + 音效标记状态跃迁。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def execute(ctx: dict) -> dict:
    """检查交互中是否有需要反馈的操作，注入反馈模式到契约。"""
    interactions = ctx.get("interactions", "")

    feedback_rules = []

    # 长操作需要进度+完成通知
    if any(kw in interactions for kw in ["导出", "上传", "下载", "处理", "生成"]):
        feedback_rules.append("长操作完成后：Toast提示+自动定位结果")

    # 删除/修改需要视觉反馈
    if any(kw in interactions for kw in ["删除", "移除", "完成", "标记"]):
        feedback_rules.append("状态变更后：元素视觉立即变化(class切换)")

    # 添加成功需要确认
    if any(kw in interactions for kw in ["添加", "创建"]):
        feedback_rules.append("添加成功：新项出现+输入清空=隐式确认")

    if feedback_rules:
        contract = ctx.get("contract", {})
        contract.setdefault("interaction_patterns", []).extend(feedback_rules)
        ctx["contract"] = contract

    return ctx


node = Node(
    id="111",
    name="操作反馈模式",
    trigger={"type": "key_exists", "key": "interactions"},
    execute=execute,
    refs=["Y10"],
    metadata={"source": "交互设计/EXAMPLES+STYLE", "category": "interaction"},
)
