"""知识节点：创建型操作交互模式 — 对话框包含所有当下自然的配置项。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


PATTERNS = [
    "创建完成后对象自动选中，系统进入可编辑状态",
    "创建型对话框包含所有此刻自然想到的配置项",
    "每个配置项必须有合理默认值，用户可以全部跳过",
    "文件保存对话框预判最可能的路径和文件名",
]


def execute(ctx: dict) -> dict:
    """向交互设计阶段注入创建流模式。"""
    interactions = ctx.get("interactions", "")

    # 检查是否涉及创建型操作
    create_keywords = ["添加", "创建", "新建", "保存", "导出", "生成"]
    if not any(kw in interactions for kw in create_keywords):
        return ctx

    # 注入交互模式提示到契约
    contract = ctx.get("contract", {})
    contract.setdefault("interaction_patterns", []).extend([
        "创建完成后输入框自动清空，焦点回到输入框",
        "列表项创建后自动出现在可见区域",
    ])
    ctx["contract"] = contract
    return ctx


node = Node(
    id="110",
    name="创建流模式",
    trigger={"type": "keyword", "target": "interactions",
             "keywords": ["添加", "创建", "新建", "保存"]},
    execute=execute,
    refs=["111"],
    metadata={"source": "交互设计/EXAMPLES", "category": "interaction"},
)
