"""知识节点：AI辅助创作工具设计——工具调用式AI集成、分支数据模型、建议-应用模式。

从AI驱动创作应用设计中提炼的通用模式：
  - 工具使用不解析自由文本：AI通过tool call返回结构化JSON
  - 建议+应用模式：AI返回结构化建议预览，用户确认后一键应用，可撤销
  - 三级撤销：内联修订(单句级) → 操作撤销(Ctrl+Z) → 分支(章节级)
  - 信息全互通：每个AI决策点都能看到完整上下文
  - 流式实时预览：流式过程中从不完整JSON提取已到达文本，直接写入DOM
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

CREATIVE_TOOL_PRINCIPLES = """你是AI辅助创作工具设计顾问。基于以下经过验证的设计模式回答问题。

## 工具使用式AI集成
- 核心原则：AI通过tool call返回结构化JSON，前端按字段精确分发，不解析自由文本
- 每个AI调用点定义明确的工具集，tool_choice控制必须调用
- 不支持tool call的模型回退到XML标签格式解析

## 建议+应用模式
- AI返回建议预览（结构化tool call），不直接修改数据
- 用户看到预览后一键应用，应用后可撤销回退
- 适用于所有AI编辑场景：正文修改、规则编辑、设定调整

## 三级撤销体系
- 内联修订（单句级）：选中文字→AI/手动修改→形成修订分支树
- 操作撤销（Ctrl+Z级）：全量快照nodes+rootNodeId，最多30层
- 分支撤销（章节级）：对整章不满意直接开分支，保留原始版本
- 修订定位用前后文锚点搜索（不用字符偏移，不怕其他位置编辑）

## 信息全互通原则
- 每个AI决策点必须能看到完整上下文（故事链、状态卡、设定等）
- 信息不互通会导致不一致决策（重复内容、矛盾设定）
- 新增任何AI调用点时必须检查上下文完整性

## 自动初始化策略
- 检查空字段，触发独立请求填充
- 每个空字段独立请求+tool_choice:required，绕过模型单工具限制
- prompt包含已有内容摘要，防止生成重复内容

## 流式实时预览
- 流式过程中用extractPartialStringValue从不完整JSON提取文本
- 直接写入DOM（textarea.value = text），throttle到requestAnimationFrame
- 大量文本一次到达时启动打字机逐字显示"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        CREATIVE_TOOL_PRINCIPLES,
        f"设计问题：{task}",
        max_tokens=300
    ).strip()
    ctx["_design_guidance"] = result
    return ctx

node = Node(id="973", name="AI辅助创作工具模式",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["tool call", "工具调用", "创作工具", "分支", "撤销体系",
                          "建议应用", "流式预览", "AI编辑", "结构化输出",
                          "自动初始化", "信息互通", "AI辅助"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "design/ai-creative-tools", "category": "design"})
