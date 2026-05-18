"""知识节点：根因分析工作流——从29个fix双轨记录提炼的诊断方法。

核心方法：先排除再定位，先思考再动手。

从4个模型(GLM-5/Sonnet4.6/Opus4.6/Haiku4.5)的fix记录提炼的根因分类体系：
  - 接口不对等(API不做预期处理) → 查底层框架源码确认行为
  - 时序错误(初始化顺序) → 画出执行流程，找"在X之前调用了Y"
  - 静默失败(写入不报错) → 在关键路径加日志确认实际值
  - 引用错误(字段不存在=undefined) → 查类型定义，undefined比较永假
  - 死代码(分支永不执行) → 检查条件是否永真/永假
  - 凭证过期(Token/Session) → 检查是否解析了expires，是否有刷新机制
  - 资源碎片(内存/磁盘) → 检查分配模式，重复new/delete=碎片源
  - 路径断裂(配置硬编码) → grep所有引用路径，评估改名/迁移影响
  - 权限不足(只读目录) → 检查运行时路径是否在可写区域
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

ROOT_CAUSE_CATEGORIES = {
    "接口不对等": "底层API不做你以为它做的事(如URL解码/JSON解析)——查框架源码确认",
    "时序错误": "在初始化之前使用了资源——画执行时序图定位",
    "静默失败": "操作不报错但实际没生效(如TypedArray(0)写入)——加日志确认实际值",
    "引用错误": "访问不存在的字段得到undefined——查类型定义",
    "死代码": "条件永真/永假导致分支不执行——检查条件的运行时值",
    "凭证过期": "Token/Session超时无刷新——检查expires解析和刷新逻辑",
    "资源碎片": "重复分配释放导致碎片——改为静态分配或池化",
    "路径断裂": "配置中硬编码路径，迁移后失效——grep所有引用评估影响",
    "权限不足": "运行时目录只读——检查是否在app bundle或系统目录内",
}


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    # 让LLM判断最可能的根因类别
    categories_text = "\n".join(
        f"- {k}: {v}" for k, v in ROOT_CAUSE_CATEGORIES.items()
    )
    classification = ask(
        system="你是根因分类助手。根据问题描述选择最可能的根因类别。",
        user=f"问题描述：{task}\n\n根因类别：\n{categories_text}\n\n"
             "选择1-2个最可能的类别名称，用逗号分隔。只输出类别名称。",
        max_tokens=100
    )

    ctx["_root_cause_hint"] = classification.strip()
    ctx["_root_cause_categories"] = ROOT_CAUSE_CATEGORIES

    ctx.setdefault("_design_principles", []).extend([
        "先排除后定位——并行检查多个假设，用排除法缩小范围",
        "影响范围评估——grep所有调用点，分类受影响vs不受影响",
        "静态分配消碎片——嵌入式场景一次分配运行时永不释放",
        "就地操作零额外内存——src/dst双指针，decoded总<=原始长度",
        "多轮迭代修复——第一轮修主因，第二轮修次因，每轮独立验证",
    ])

    return ctx


node = Node(id="660", name="根因分析工作流",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["根因", "root cause", "为什么", "原因", "诊断",
                          "排查", "分析问题"]},
    execute=execute, refs=["600"],
    metadata={"source": "Agent/GLM-5+Sonnet4.6+Opus4.6 fix记录×29", "category": "methodology"})
