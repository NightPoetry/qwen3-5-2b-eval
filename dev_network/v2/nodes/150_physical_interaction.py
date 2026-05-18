"""知识节点：拟物交互风格 — 拖拽/推开/弹力/轨道模式。

适用于涉及拖拽、排序、移动的交互。
向事件层注入物理交互模式代码。
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


# 物理交互代码模板
DRAG_TEMPLATE = """
// 拟物拖拽：mousedown记录快照，mousemove纯函数计算，mouseup确认
let dragState = null;

function startDrag(e, item) {
  dragState = {
    id: item.id,
    startX: e.clientX,
    originPos: item.getBoundingClientRect(),
    snapshot: [...items], // 快照：弹力恢复的基础
  };
}

function onDrag(e) {
  if (!dragState) return;
  const dx = e.clientX - dragState.startX;
  // 每帧从快照重算（弹力恢复：无累积误差）
  // 实现取决于具体场景
}

function endDrag() {
  dragState = null;
}
"""

SORTABLE_TEMPLATE = """
// 轨道推动：同容器元素互相推让
function reorderItems(dragId, targetIndex) {
  const idx = items.findIndex(i => i.id === dragId);
  if (idx === -1) return;
  const [item] = items.splice(idx, 1);
  items.splice(targetIndex, 0, item);
  saveData();
  renderList();
}
"""


def execute(ctx: dict) -> dict:
    """当交互涉及拖拽/排序时，注入物理交互模板。"""
    interactions = ctx.get("interactions", "")
    task = ctx.get("task", "")
    combined = interactions + " " + task

    drag_keywords = ["拖拽", "拖动", "排序", "移动", "拖放", "drag", "sortable"]
    if not any(kw in combined for kw in drag_keywords):
        return ctx

    # 注入到契约中供JS生成参考
    contract = ctx.get("contract", {})
    contract.setdefault("interaction_patterns", []).extend([
        "拖拽使用快照模式：mousedown记录初始状态，mousemove从快照重算",
        "同容器元素互相推让不穿透（轨道推动）",
        "操作过程是状态的纯函数，回拖能完整归位（弹力恢复）",
    ])
    ctx["contract"] = contract
    ctx.setdefault("_style_fixes", []).append("注入拟物交互模式")
    return ctx


node = Node(
    id="150",
    name="拟物交互模式",
    trigger={"type": "keyword", "target": "interactions",
             "keywords": ["拖拽", "拖动", "排序", "移动", "drag"]},
    execute=execute,
    refs=["Y10"],
    metadata={"source": "交互设计/STYLE+交互设计师", "category": "interaction"},
)
