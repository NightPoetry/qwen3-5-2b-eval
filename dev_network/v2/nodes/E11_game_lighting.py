"""知识节点：2D游戏光照与阴影——光场传播/三函数管线/多体交互。

融合：游戏引擎光照系统设计原则 + 光场阴影系统设计原则
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

LIGHTING_KNOWLEDGE = """你是2D游戏引擎光照系统专家。根据以下知识指导光照设计。

## 核心洞察
光照有别于特效的本质：特效是f(自身像素)→输出，光照是{发光体}x{受光体}→交互→输出。
光照系统核心是跨实体数据流管线（收集→传播→吸收→交付），不是函数库。

## 九条设计原则
1. 多体关系是光照本质——核心是跨实体数据流管线
2. 内核永远是函数——元组和预制都是便利层，凡是写元组的地方都能写函数
3. 按函数签名分Kind——传播/作用/穿透/受光四种签名四种Kind
4. 职责不同必须拆开——穿透影响别人，受光影响自己，默认一致但可分离
5. FX放核心(Kind方法)，Preset放预制——预制可无限多，Kind就几个
6. 光强与穿透性博弈——穿透深度是光强与材质穿透性逐步博弈的自然结果
7. 效果归属看是否依赖光照——随光照变化→光照系统，无关→特效系统
8. 框架提供共性，个性让用户插——基础设施+默认行为+覆盖点
9. 阴影是光场传播的自然结果不是独立渲染效果

## 三函数阴影管线
投影函数(光源)→几何路径Path2D
  ↓
形状函数(受光体)→influence map(canvas, alpha=遮挡强度)
  ↓
叠加函数(光源)→合成到光场

- 投影函数：point(发散放大)/parallel(等大平移)/自定义
- 形状函数：输出逐位置强度值(不是二值轮廓)，含渐变和软边缘
- 叠加函数：subtract(destination-out)/multiply(柔化)/自定义
- 光场逐层传播：每经过受光体修改一次光场，阴影从中涌现
- 三个函数全部支持自定义——内置预制覆盖常见场景

## 与几何阴影对比
- 几何阴影硬编码梯形，复杂轮廓无法处理
- 光场阴影用连续强度值influence map，支持渐变软边缘
- 性能控制逐实体：简单物体用rect预制，复杂物体用自定义
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        LIGHTING_KNOWLEDGE +
        "\n分析以下任务涉及的2D光照/阴影系统设计问题，给出建议（每条一行，不超过4条）。"
        "如果不涉及光照系统，回答'无相关问题'。",
        f"任务：{task[:500]}",
        max_tokens=250
    ).strip()
    if "无相关问题" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx

node = Node(id="E11", name="2D光照阴影",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["光照", "light", "阴影", "shadow", "光场",
                          "light field", "穿透", "受光", "遮挡",
                          "2D引擎", "光源", "渲染"]},
    execute=execute, refs=["E10"],
    metadata={"source": "Guild/游戏引擎设计/光照系统+光场阴影", "category": "domain_game"})
