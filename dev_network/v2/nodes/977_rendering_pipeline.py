"""知识节点：渲染管线设计模式——光照系统演进、特效动画三层架构、阴影三函数管线。

从2D游戏引擎渲染系统设计中提炼的管线模式：
  - 概念坍缩：穿透+透光+响应→统一材质穿透性，一个方程I(next)=model(I,material)
  - LightCurve四元组：[start,hold,power,end]统一描述所有光照行为曲线
  - 特效三层架构：底层原语(matrix/filter/draw/shader) → animate关键帧 → FXPreset命名预制
  - 阴影三函数管线：投影函数(几何路径) → 形状函数(influence map) → 叠加函数(合成模式)
  - Effect驱动：组件只管身份标识和开关，所有行为通过addEffect挂载
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

PIPELINE_PRINCIPLES = """你是渲染管线设计顾问。基于以下经过验证的设计模式回答问题。

## 光照系统内核方程
- I(next) = model(I_current, material(position))
- 三个模型：propagation(强光更深,物理直觉) / curve(固定深度,美术可控) / custom(逃逸舱口)
- 概念坍缩过程：穿透≠透光≠响应 → 穿透≈透光(共享签名) → 穿透=透光=响应=material(统一)
- 强度决定深度：intensity=2穿过material=0.7 → 2.0→1.4→0.98→0.69(四层可见)

## LightCurve统一原语
- 四元组[start, hold, power, end]统一描述所有光照曲线
- t≤hold→start; t>hold→start+(end-start)×((t-hold)/(1-hold))^power
- 消灭type枚举：点光源/聚光灯不是不同类型，是不同曲线配置的自然涌现
- 预制=命名好的曲线值，展开运算符组合

## 特效三层架构
- Layer 0底层原语：matrix(零开销仿射变换) / filter(GPU CSS filter) / draw(自定义Canvas) / shader(逐像素CPU)
- Layer 1动画层：animate()单轨关键帧插值，交替状态帧与过渡
- Layer 2预制层：FXPreset独立命名空间，内部由animate/draw/shader组装
- 全部通过addEffect()唯一挂载接口
- 每个属性独立插值，组合是用户的事

## 阴影三函数管线
- 投影函数(光源端)：决定阴影几何路径Path2D(point发散/parallel平行/自定义)
- 形状函数(受光体端)：在canvas上绘制influence map(alpha=逐位置遮挡强度,不是二值轮廓)
- 叠加函数(光源端)：决定influence map如何合成到光场(subtract/multiply/自定义)
- 阴影是光场传播的自然产物，不是画上去的几何形状
- 光场逐级传播：按距离排序遇到受光体→三函数协作修改光场→修改后继续传播

## 四种Effect Kind
- 传播(propagation)：光在空间怎么分布
- 作用(apply)：光到了做什么
- 穿透(absorption)：光经过材质还剩多少
- 受光(compute)：材质表面显示什么
- 判断归属：效果随光照变化→光照系统；效果与光照无关→特效系统"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        PIPELINE_PRINCIPLES,
        f"设计问题：{task}",
        max_tokens=300
    ).strip()
    ctx["_design_guidance"] = result
    return ctx

node = Node(id="977", name="渲染管线设计模式",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["光照", "lighting", "渲染", "render", "特效", "effect",
                          "阴影", "shadow", "管线", "pipeline", "衰减", "falloff",
                          "动画系统", "关键帧", "材质", "穿透"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "design/rendering-pipeline", "category": "design"})
