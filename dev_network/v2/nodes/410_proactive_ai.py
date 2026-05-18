"""知识节点：主动式AI——调度策略/退出标记/自适应学习/行为模式识别。

核心：AI主动表达不是无限生成，而是有节制的社交智能。
融合：companion-ai-proactive
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

PROACTIVE_KNOWLEDGE = """你是AI主动行为设计专家。根据以下知识评估主动行为的设计。

## 调度策略
- 下一次动作时间确定时，一次性算出目标时间戳并比较，非周期性重新评估
- 轮询式"每N秒检查一次是否该做某事"是最常见的资源浪费模式
- 社交场景中主动触发应注入原始信号（沉默时长、当前时间、用户活跃模式），非注入决策

## LLM自主行为控制
- 给LLM主动发起对话能力时，必须提供显式退出标记（如[SILENT]）作为一等选项
- 没有退出标记时LLM会永远生成内容——生成就是它被训练来做的事
- 主动消息被忽略或冷淡回应时，等待时间翻倍（设上限）——指数退避在社交场景同样适用

## 自适应学习
- 从稀疏二值反馈中学习最优间隔：每次按固定百分比（如+-20%）调整，能收敛且不振荡
- 用户显式偏好和隐式行为经常不一致，用max(显式,隐式)作为下限

## 用户行为模式识别
- 按小时统计消息量并施加每日指数衰减（如x0.75），形成揭示活跃时段的分布
- 以峰值活跃度25%为阈值划分醒睡边界，无需显式询问
- 对话结束检测：告别语/忙碌信号是可靠显式信号；回复变短是统计模式，需>=2数据点才下结论
"""

PROACTIVE_RULES = [
    "生成完成后主动运行验证——不等用户发现问题",
    "检测到潜在问题时主动警告——不等它爆炸",
    "预判用户下一步操作——生成完自动打开预览",
    "记住用户偏好——下次自动应用（预设系统）",
    "失败时自动重试一次——瞬时错误不暴露给用户",
    "主动行为必须有显式退出标记——LLM无退出选项时会永远生成",
    "被忽略的主动消息应指数退避——模拟人类社交直觉",
    "注入原始信号让AI自己决策，不要硬编码触发规则",
]

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    # 如果任务涉及主动行为设计，用LLM做更深入分析
    proactive_signals = ["主动", "推送", "通知", "提醒", "定时", "触发", "调度"]
    if any(s in task for s in proactive_signals):
        result = ask(
            PROACTIVE_KNOWLEDGE +
            "\n分析以下任务中主动行为设计的风险和建议（每条一行，不超过4条）。"
            "如果不涉及主动行为设计，回答'无主动行为风险'。",
            f"任务：{task[:500]}",
            max_tokens=250
        ).strip()
        if "无主动行为风险" not in result:
            ctx.setdefault("_design_principles", []).append(result)

    ctx.setdefault("_design_principles", []).extend(PROACTIVE_RULES)
    return ctx

node = Node(id="410", name="主动式AI",
    trigger={"type": "always"},
    execute=execute, refs=["Y30"],
    metadata={"source": "knowledge/companion-ai-proactive", "category": "meta"})
