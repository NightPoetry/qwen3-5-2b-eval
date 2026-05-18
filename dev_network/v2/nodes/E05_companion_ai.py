"""知识节点：陪伴型AI系统设计——表达欲/主动消息/事件驱动调度。

融合：陪伴型AI表达欲与自主对话系统设计指南
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

COMPANION_KNOWLEDGE = """你是AI系统架构师。根据以下知识指导陪伴型AI系统设计。

## 核心理念
代码是信号提供者，AI是决策者。不用硬编码规则代替AI判断力。

## 表达欲（风格控制，不是频率控制）
- 三级：LOW(简洁不追问)/MEDIUM(正常)/HIGH(可发散引导)
- 分析最近8轮：消息长度、问号数量、回复频率
- 表达欲只影响风格不影响是否发言——内向的人也可能主动关心，只是方式简洁

## 主动消息（AI自主权）
- 注入信号：表达欲等级/距上次消息时间/当前时间/活跃时段/今日已主动次数/上次是否被回复
- AI返回正常文本=发送，返回[SILENT]=选择沉默
- 退避机制：连续SILENT时间隔翻倍(30min→60→120→240上限)，用户新消息重置

## 事件驱动调度（不轮询）
- 每次对话结束后计算精确的下次检查时间
- 告别语→次日起床+20min；忙碌→2.5h后；冷淡→1h后；突然中断→25min后
- 主循环只做if(millis()>=next_check_time)——零开销

## 用户作息学习
- 维护24小时活跃度数组，每收到消息对应小时+1
- 每日对数组做指数衰减(×0.75)——近期数据权重更高
- 推导wake_hour和sleep_hour，主动消息钳制在活跃时段内

## 双轨频率控制
- 显式偏好(min_hours)：AI通过工具调用设置，如用户说"不爱说话"→168h
- 隐式偏好(learned_hours)：系统自动学习——热情回复缩短20%，冷淡延长20%
- 实际生效值取两者中较大值
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        COMPANION_KNOWLEDGE +
        "\n分析以下任务涉及的AI陪伴系统设计问题，给出建议（每条一行，不超过4条）。"
        "如果不涉及此类问题，回答'无相关问题'。",
        f"任务：{task[:500]}",
        max_tokens=250
    ).strip()
    if "无相关问题" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx

node = Node(id="E05", name="陪伴型AI设计",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["陪伴", "companion", "主动消息", "proactive",
                          "表达欲", "自主对话", "作息", "退避",
                          "聊天机器人", "bot", "伴侣"]},
    execute=execute, refs=["395"],
    metadata={"source": "Guild/AI与LLM应用/陪伴型AI设计方案", "category": "domain_ai"})
