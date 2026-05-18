"""知识节点：ECS游戏引擎模式——从Sonnet4.6的开发/修复记录提炼。

来源：Sonnet4.6 develop 001-008 + fix 001-008（15条ECS相关双轨记录）

Entity-Component-System核心模式：
  - ComponentRegistry = 纯查找表，register不做初始化
  - ComponentSystem = 抽象基类，提供SoA存储+initialize/shutDown
  - LifecycleManager = 唯一生命周期管理者，startup中按order初始化

SoA(Structure of Arrays)内存管理：
  - Float32Array预分配→改为DynamicTypedArray动态管理
  - 翻倍扩容(均摊O(1)) + 趋势统计缩容(防反复横跳)
  - 缩容需冷却期(5s)+增删趋势判断(creates>deletes*0.3则不缩)
  - TypedArray.set()是原生memmove——100K元素约0.05ms

渲染排序（画家算法）：
  - 高层遮挡低层→layer升序
  - 同层右侧遮挡左侧→x升序
  - 同层下侧遮挡上侧→y升序
  - 三个key均为升序，完美符合画家算法

物理碰撞级联递归：
  - 推方块A→A碰B→B碰墙(终止)→回溯确定位置
  - 防环：visited Set
  - 终止：kinematic物体
  - 防抖：bounceThreshold+positionSlop+冷却期
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    verdict = ask(
        system="你是游戏引擎模式识别助手。",
        user=f"任务：{task}\n\n这个任务是否涉及游戏引擎相关概念？"
             "（ECS/渲染/物理碰撞/动画/组件系统）回答是或否。",
        max_tokens=30
    )

    if "是" in verdict:
        ctx.setdefault("_design_principles", []).extend([
            "初始化必须在数据写入之前——否则SoA数组写入静默失败",
            "Float32Array(0)写入不报错——JS不抛异常但数据丢失",
            "惰性初始化守卫：if(!this._initialized) this.initialize()",
            "渲染排序=layer升序+x升序+y升序——画家算法",
            "碰撞级联递归+visited防环+kinematic终止",
            "缩容用趋势统计防反复横跳——不是简单利用率阈值",
            "系统执行顺序用order控制——正数升序，负数(如-1)最后执行",
        ])

    return ctx


node = Node(id="665", name="ECS游戏引擎模式",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["游戏", "game", "ECS", "渲染", "render", "碰撞",
                          "collision", "物理", "physics", "动画", "sprite"]},
    execute=execute, refs=["610"],
    metadata={"source": "Agent/Sonnet4.6 develop+fix×15(ECS系列)", "category": "domain"})
