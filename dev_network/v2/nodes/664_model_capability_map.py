"""知识节点：模型能力图谱——从4个模型的双轨记录提炼的能力差异。

来源：GLM-5(11条) + Sonnet4.6(15条) + Opus4.6(22条) + Haiku4.5(1条)
共49条双轨记录的模型行为对比。

模型能力分层（从双轨数据提炼）：
  大模型(Opus4.6): 单次完成复杂推理，8轮迭代设计，600G数据迁移单次会话
  中模型(Sonnet4.6): ECS架构设计，物理系统多轮修复，需要明确引导
  小模型(GLM-5): 计费逻辑、API配置修复，需要拆细步骤
  轻模型(Haiku4.5): 指令执行（擦除U盘），需要人确认每步

对2B模型的启示（单线程原则）：
  - 2B=单线程处理器——每次只能处理一个简单认知操作
  - 大模型一次完成的=2B必须拆成多个原子步
  - 判断和执行必须分离——先ask一个问题，再根据结果行动
  - 上下文由系统维护——模型每次只看当前步骤所需

Fix/Develop模式切换模式：
  GLM-5: Fix→Develop→Fix（用户混用，灵活切换）
  Sonnet4.6: Develop→Fix(临时)→Develop（开发中发现bug临时转修）
  Opus4.6: 交替进行（22条中fix11+develop11几乎对半）
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def execute(ctx: dict) -> dict:
    ctx.setdefault("_design_principles", []).extend([
        "2B模型=单线程——每次只处理一个简单认知操作",
        "大模型单次完成=小模型分步完成——拆原子步是关键",
        "判断和执行分离——先ask判断，再根据结果行动",
        "上下文由系统维护——模型每次只看当前步骤所需信息",
        "模式切换灵活——用户可能随时从开发转修复或反之",
        "能力与任务匹配——简单执行用轻模型，复杂推理用大模型",
    ])
    return ctx


node = Node(id="664", name="模型能力图谱",
    trigger={"type": "always"},
    execute=execute, refs=["630"],
    metadata={"source": "Agent/4模型switch.md+49条双轨记录行为对比", "category": "methodology"})
