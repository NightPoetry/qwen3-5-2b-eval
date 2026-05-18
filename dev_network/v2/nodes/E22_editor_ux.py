"""知识节点：编辑器UX模式——音效系统/工具栏组织/资源库管理。

融合：编辑器音效系统 + 工具栏与子工具切换 + 资源库与素材管理（去敏化）
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

EDITOR_UX_KNOWLEDGE = """你是GUI编辑器UX设计专家。根据以下知识指导编辑器交互设计。

## WebAudio合成音效（零包体积）
- 不加载wav/mp3——用OscillatorNode合成，即调即出
- 三个原语：_p(单频音)/_ps(频率扫描sweep)/_chord(和弦)
- exponentialRamp衰减到0.001(-60dB)——自然衰减不是截断
- 多oscillator叠加除以sqrt(N)保持感知响度一致

## 音效语义图谱
- 轻点击=高频sine短音；重确认=中高频双音上扬
- 错误=低频sawtooth长音(独一无二不复用)
- 删除=低频triangle；切割=极高频square极短双音(咔嚓)
- 互补动作用相反方向：mute=down sweep, unmute=up sweep
- 同类动作用相同音色族——让用户根据音色猜动作类型

## 何时播音效
- 播：用户主动触发的成功操作、被拒绝操作、实质状态变化、完成里程碑
- 不播：渲染循环每帧、内部状态变化、鼠标hover、自动触发、drag中间过程
- 拖动完成只在clip真正移动了才播(abs(delta)>0.001)
- snap去重：只在"未吸附→进入吸附"那帧播

## 工具栏组织
- toolbar(顶部)vs时间轴控制条——按钮位置取决于是否依赖当前playhead/选中clip
- 文件组(Import/Export/Save)/工具组(Select/Polygon/Record)/历史组(Undo/Redo)/视图组
- 右键切换子工具=PS长按模式——同组语义相近互斥行为(如录音sync/silent)
- 子工具右键只在语义成立的入口提供——该入口不存在多种细分就不带右键
- 同名功能双入口用不同图标不同tooltip——视觉差异让用户知道是两个不同动作

## 资源库管理
- source pool和clip是多对多——sources[]通过sourceId被clips[]引用
- 双击=当前playhead位置插入；拖拽=落点位置插入
- 类型不兼容拒绝+红色高亮——不要静默转换
- video source插入自动配对audio clip共享linkId
- 位置冲突用ripple insert后移而非reject/覆盖
- 删除source带反向引用确认："此资源被N个片段使用，同时删除？"
- 缩略图异步回填：generateThumbs完成时显式调renderLibrary()
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        EDITOR_UX_KNOWLEDGE +
        "\n分析以下任务涉及的编辑器UX设计问题，给出建议（每条一行，不超过5条）。"
        "如果不涉及编辑器UX，回答'无相关问题'。",
        f"任务：{task[:500]}",
        max_tokens=300
    ).strip()
    if "无相关问题" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx

node = Node(id="E22", name="编辑器UX模式",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["音效", "SFX", "sound", "WebAudio",
                          "工具栏", "toolbar", "子工具", "右键菜单",
                          "资源库", "素材", "asset", "library",
                          "拖拽", "drag", "drop", "编辑器"]},
    execute=execute, refs=["220", "E20"],
    metadata={"source": "Guild/视频剪辑交互设计/音效+工具栏+资源库", "category": "domain_nle"})
