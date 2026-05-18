"""知识节点：全自动执行模式——系统能自动做的不问用户。

融合：全自动执行模式原则 + 反面案例（无意义监控浪费资源）。

原则：人类参与点越少越好。只在不可逆/歧义时才要求确认。
其余全部自动：默认值自动填、文件自动保存、格式自动修复。

反面教训：
- 例行状态（心跳等）不应每次通知
- 需要用户参与时应询问而非反复发送状态
- 2-3次无进展应暂停，切换其他任务
- 所有项待定时应终止并输出总结
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

AUTO_RULES = [
    "默认值：每个字段/配置项都有合理默认值",
    "自动保存：操作完成后自动持久化，不等用户点保存",
    "自动修复：格式错误自动纠正（markdown标记/多余空行/缩进不一致）",
    "自动跳过：可选步骤在急速模式下全部跳过（Enter即确认）",
    "自动回退：操作失败时自动恢复到上一个有效状态",
    "反资源浪费：例行状态不通知，2-3次无进展则暂停切换",
    "精确过滤：监控只关注关键事件（消息/错误/连接变化），排除例行心跳",
    "任务终止：全部待定时输出总结并终止，不持续空转",
]

def execute(ctx: dict) -> dict:
    # 向契约注入自动化规则
    contract = ctx.get("contract", {})
    contract.setdefault("auto_rules", []).extend(AUTO_RULES)
    ctx["contract"] = contract
    return ctx

node = Node(id="340", name="全自动执行",
    trigger={"type": "always"},
    execute=execute, refs=["Y20"],
    metadata={"source": "Guild/全自动执行模式+反面案例", "category": "architecture"})
