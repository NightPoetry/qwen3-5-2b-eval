"""知识节点：游戏引擎特效系统——三层架构/关键帧插值/预制效果。

融合：游戏引擎特效系统设计原则
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

EFFECTS_KNOWLEDGE = """你是游戏引擎特效系统设计专家。根据以下知识指导效果系统设计。

## 核心原则
每个属性独立插值，组合是用户的事。不同性质的属性之间没有插值路径，同类型数值属性各自平滑变化。

## 三层架构
- Layer 0（底层）：可插值单元（数值型属性）+ 不可插值扩展点（自定义逻辑）
- Layer 1（动画系统）：关键帧插值，只调度可插值的数值型属性
- Layer 2（预制效果）：独立命名空间，内部由Layer 1组装，用户不需了解细节
- 统一挂载接口：addEffect()

## 关键帧格式
交替状态帧与过渡：
- 状态帧含value和可选hold(到达后停留时长)
- 过渡含duration和可选easing
- 第一帧没有过渡，过渡对象放在相邻状态帧之间

## 命名语义
- 名称描述行为不描述操作对象（shader而非pixel）
- 避免与行业标准术语冲突（不用pixelShader因为是GPU术语）

## 预制效果原则
- 独立命名空间不污染底层API
- 纯静态工厂无状态
- 有内部时钟的一次性特效每次new，持久特效可复用实例
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        EFFECTS_KNOWLEDGE +
        "\n分析以下任务涉及的特效系统设计问题，给出建议（每条一行，不超过4条）。"
        "如果不涉及特效系统，回答'无相关问题'。",
        f"任务：{task[:500]}",
        max_tokens=250
    ).strip()
    if "无相关问题" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx

node = Node(id="E10", name="游戏特效系统",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["特效", "effect", "关键帧", "keyframe", "插值",
                          "动画", "animation", "预制", "preset",
                          "shader", "粒子", "particle"]},
    execute=execute, refs=["Y20"],
    metadata={"source": "Guild/游戏引擎设计/特效系统设计原则", "category": "domain_game"})
