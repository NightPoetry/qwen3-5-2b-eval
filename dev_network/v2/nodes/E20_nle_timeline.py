"""知识节点：NLE时间轴交互——坐标系/拖动/推开链/缩略图/播放引擎。

融合：多轨时间轴交互设计指南（去敏化：移除项目名）
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

TIMELINE_KNOWLEDGE = """你是非线性编辑器(NLE)交互设计专家。根据以下知识指导时间轴交互设计。

## 坐标系统一
- 整套交互只用一套坐标系：以clip-area的left为0，tlScrollX偏移，tlZoom比例尺
- time = (clientX - clipArea.left + tlScrollX) / tlZoom
- 所有点击seek/拖动clip/缩放/键盘步进都用同一公式

## 点击vs拖动
- 4像素拖动阈值：|dx|>4或|dy|>4才算开始拖动
- mousedown仍立即seek一次——用户主动点击的位置是确定目标

## 片段拖动
- 用grabOffset锁定光标而非dx增量——auto-scroll时clip不会从光标下漂走
- mousedown记录grabOffset=clickTime-clip.startTime
- mousemove: clip.startTime = cursorTime - grabOffset

## 自动滚动
- 死区>=8px才触发；慢速上限12px/帧；Shift加速3x
- 滚动后必须重新applyMove——用lastMoveEv重算clip位置

## 推开链+铆钉
- 同轨道clip不允许重叠——推开链实现物理排他
- 每帧先重置所有非拖动clip到origPos再重算——回拖时自动弹回
- 铆钉clip是推动链的墙，链条不能穿过
- t=0是虚拟铆钉——时间轴最左永远顶墙

## Trim
- Trim只阻挡不推开——拉边沿不应把后面整串clip顶走

## 播放头
- 拖动时playhead跟手：seekTo(cursorTime)
- trim-right: seekTo(cursorTime-0.001)预览clip内部最后帧
- _seekPending防闪回：seek未完成时用目标值绘制，完成后用video.currentTime

## timeline-time vs source-time
- timeline-time：轨道上位置(state.playheadTime, clip.startTime)
- source-time：媒体文件内部时间(video.currentTime, clip.sourceIn)
- split/ripple后两者解耦——必须用tlToSrc/srcToTl双向映射

## 音视频绑定
- linkId持久化：共享linkId的clip属同一绑定组
- Split后右半必须分新linkId——否则左右半粘到一起
- 所有操作(split/delete/duplicate/drag/trim)必须link-aware

## 缩略图
- 独立video元素生成(不用主video)——按sourceId缓存ImageBitmap
- updateTLPositions()只改style不重建DOM——消灭闪烁

## 滚动边界
- 双向夹：上界=内容宽度-视口宽度+40px余量
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        TIMELINE_KNOWLEDGE +
        "\n分析以下任务涉及的时间轴交互设计问题，给出建议（每条一行，不超过5条）。"
        "如果不涉及时间轴交互，回答'无相关问题'。",
        f"任务：{task[:500]}",
        max_tokens=300
    ).strip()
    if "无相关问题" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx

node = Node(id="E20", name="NLE时间轴交互",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["时间轴", "timeline", "NLE", "剪辑", "clip",
                          "playhead", "播放头", "trim", "拖动", "drag",
                          "推开", "铆钉", "pin", "缩略图", "thumbnail",
                          "seek", "视频编辑", "ripple"]},
    execute=execute, refs=["180", "181"],
    metadata={"source": "Guild/视频剪辑交互设计/多轨时间轴交互", "category": "domain_nle"})
