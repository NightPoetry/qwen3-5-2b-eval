"""知识节点：工具交互设计模式——双画布渲染、径向菜单、坐标空间分离。

从多个工具产品设计中提炼的通用交互模式：
  - 双画布/双坐标空间：图像空间(随缩放)+屏幕空间(固定像素)，解决边框在任意缩放下可见
  - 径向菜单：固定总半径，层级向外生长，内环压缩让位
  - 网格吸附：所有移动操作统一参与网格对齐
  - 撤销策略：全量快照 vs 增量差异，数据小时全量更优
  - 高DPI适配：canvas尺寸×dpr + style尺寸不变 + ctx.scale(dpr)
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

UX_PATTERN_PRINCIPLES = """你是工具交互设计顾问。基于以下经过验证的设计模式回答问题。

## 双坐标空间渲染
- 问题：标注/边框在缩放时要么消失要么变粗
- 方案：图像空间画布(随CSS transform缩放) + 屏幕空间画布(固定像素宽度)
- 图像空间负责：区域填充、网格线（随缩放一起变化）
- 屏幕空间负责：边框、标签、十字线、绘制预览（始终固定像素宽度）
- 坐标转换：imgToScreen(ix,iy) = panOffset + imageCoord × zoom
- 像素对齐：Math.round(pos) + 0.5 让1px线条清晰

## 高DPI适配
- canvas.width = displayWidth × devicePixelRatio
- canvas.style.width = displayWidth + 'px'
- ctx.scale(dpr, dpr)
- 每次绘制前重置transform：ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

## 径向菜单设计
- 总半径恒定：无论展开几层，扇形总半径不变
- 自然信息约束：内环空间小→根菜单精简(3-5项)，外环空间大→子菜单容纳更多
- 弧段裁切：clip-path: path(...)裁切为弧段形状
- 内容定位：弧段质心处，绝对定位+transform
- 展开动画：每段独立scale弹出，逐项stagger延迟
- 适用：角落触发、需要层级但不想下拉；不适用：超6项根级、3层以上、移动端

## 网格吸附统一
- 所有移动操作统一参与：绘制新区域、鼠标拖拽、键盘移动、复制拖拽
- snapMove(v, grid) = grid > 0 ? Math.round(v / grid) * grid : v

## 撤销系统设计
- 全量快照 vs 增量差异：数据量小时(如<100条区域)全量快照代价可忽略
- 键盘移动批处理：连续按住只记录一次撤销点
- 拖拽撤销：mouseup时回退到原始坐标→pushHistory→再应用新坐标

## 标签命中检测
- 非DOM元素的命中检测：每帧渲染时收集命中矩形(labelHitRects)
- mousedown时遍历检测，倒序遍历保证上层优先"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        UX_PATTERN_PRINCIPLES,
        f"设计问题：{task}",
        max_tokens=300
    ).strip()
    ctx["_design_guidance"] = result
    return ctx

node = Node(id="972", name="工具交互设计模式",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["画布", "canvas", "缩放", "zoom", "坐标空间", "径向菜单",
                          "radial", "网格吸附", "snap", "撤销", "undo", "高DPI",
                          "dpr", "像素对齐", "标注工具", "编辑器交互"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "design/tool-ux-patterns", "category": "design"})
