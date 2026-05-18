"""知识节点：系统内核设计方法——从膨胀到收敛的六步法、统一管线内核。

从游戏引擎系统设计中提炼的通用系统内核发现方法论：
  - 六步收敛法：确立最少机制→借鉴已验证模式→正确边界切分→识别共性合并→寻找统一原语→收敛到内核方程
  - 统一管线内核：所有管线共享同一骨架(order+排序+分组+钩子)，差异通过子类重写钩子解决
  - 内核判定标准：增加任何概念多余 + 删除任何概念失去表达力 + 效果是配置的涌现
  - 递归组合：管线就是节点，节点就是管线
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

KERNEL_DESIGN_PRINCIPLES = """你是系统内核设计顾问。基于以下经过验证的设计方法论回答问题。

## 从膨胀到收敛的六步法
1. 确立"最少机制"目标：不是先列功能再实现，而是先确立约束——用尽可能少的机制
2. 借鉴已验证的模式：不为新系统发明新模式，同一项目的所有系统应共享同一套元模式
3. 在正确的边界切分：按角色(谁发出/谁接收)切而非按步骤切，组合爆炸留给用户而非系统内部
4. 识别共性合并概念：函数签名相同+数据流向相同+取值范围相同→可能是同一件事
5. 寻找统一原语：固定尺寸、全覆盖（无无效配置）、可预制、可直写的参数化原语
6. 收敛到内核方程：一个方程覆盖全部交互，效果是涌现的，参数极少

## 内核判定标准
- 增加任何概念都是多余的——新概念能被已有概念的组合表达
- 删除任何概念都会失去表达力——每个概念覆盖不了的空间
- 效果是配置的涌现——不需要模式切换，不同配置自然产生不同效果
- 反例检测：需要if(mode===X)分支处理新场景→还没找到内核

## 统一管线内核(OrderedPipeline)
- 不变的骨架：register/unregister、按order排序、按order分组组内并行、顺序执行各组
- 可重写的钩子：onBeforeRegister、onAfterRegister、onInitialize、onShutDown
- 差异参数化：注册时注入什么、传递什么上下文、执行模式(广播/链式)——全部通过子类重写钩子
- 递归：管线就是节点，节点就是管线，可无限嵌套

## 辅助原则
- 模型是分类不是系统：一个系统内有不同计算模型，分类为了选择不为了建墙
- 独立维度独立变化：可以独立取值且组合有意义就不要绑定
- 预制是命名好的配置值：不是另一套API，用户用预制因为方便，用原语因为灵活
- 三层类型体系：内核(函数) → 框架(参数化元组) → 预制(命名配置值)"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        KERNEL_DESIGN_PRINCIPLES,
        f"设计问题：{task}",
        max_tokens=300
    ).strip()
    ctx["_design_guidance"] = result
    return ctx

node = Node(id="976", name="系统内核设计方法",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["内核", "kernel", "最少机制", "管线", "pipeline", "收敛",
                          "统一原语", "概念合并", "order", "钩子", "hook",
                          "系统设计", "架构简化", "骨架"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "design/system-kernel", "category": "design"})
