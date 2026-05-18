"""知识节点：自适应学习模式——从用户反馈中学习偏好。

核心规则：
  - 显式反馈（用户说的）和隐式反馈（用户做的）取max作为下限
  - 调整幅度±20%（收敛且不振荡）
  - 退避策略：被忽略时等待时间翻倍
  - 活跃时段从消息时间戳统计+指数衰减推断
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

ADAPTIVE_RULES = [
    "显式偏好(用户说的)和隐式行为(用户做的)不一致时取max",
    "每次调整幅度±20%——太大振荡，太小收敛慢",
    "被忽略时等待翻倍（指数退避），成功后立即重置",
    "一次性算出目标时间戳——不要周期性重新评估",
    "退出标记[SILENT]必须是一等选项——不是附带说明",
]

def execute(ctx: dict) -> dict:
    ctx.setdefault("_design_principles", []).extend(ADAPTIVE_RULES)
    return ctx

node = Node(id="490", name="自适应学习",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["学习", "偏好", "推荐", "自适应", "个性化", "习惯"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "knowledge/companion-ai-proactive", "category": "meta"})
