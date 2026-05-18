"""知识节点：AI能力增强脚手架——为能力有限的模型提供结构化辅助。

从小模型辅助设计和嵌入式AI伴侣系统中提炼的模式：
  - 模板辅助：小模型不独立生成，基于模板填充，结构正确+内容由模型负责
  - 分层知识架构：灵魂层(锁定) → 共识层(全量加载) → 索引层(自动加载) → 知识层(按需)
  - 工具递归上限：最多N层工具调用，防止无限循环
  - 流式优先：API响应流式接收，不在内存中缓冲完整内容
  - 消息批量处理：队列收集用户消息，一次性整合后回复
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SCAFFOLDING_PRINCIPLES = """你是AI系统辅助设计顾问。基于以下经过验证的设计模式回答问题。

## 模板辅助模式（小模型增强）
- 核心理念：小模型不完全依赖自身生成，基于模板填充
- 模板负责：结构、骨架、框架；模型负责：内容、逻辑、细节
- 三种实现：模板库文件(加载填充)、模板嵌入提示词(直接参考)、模板检索系统(关键词匹配)
- 类比：新手程序员依赖IDE补全，小模型依赖模板库

## 分层知识架构
- 灵魂层：人格/规则定义，锁定不可修改，始终加载
- 共识层：与用户达成的约定，体积小，每次全量加载
- 索引层：知识目录README，自动加载，AI看索引按需读取
- 知识层：具体知识文件，按需渐进加载
- 写入新文件后必须更新对应索引

## 资源受限环境设计
- 静态分配：长生命周期对象启动时分配，运行时不释放，防堆碎片
- 流式优先：API响应流式接收，文件上传流式写入，不缓冲完整内容
- 分时复用：不能同时两个TLS连接时分时使用
- 工具递归上限：最多5层工具调用，防止无限循环

## 消息处理策略
- 批量处理：消息队列持续收集，下次处理时一次性写入+调用LLM
- 内心所想机制：连续消息不逐条回复，标记thought但不发送，等停下后整合回复
- 队列式工具调用：LLM一次返回多个tool_calls，全部执行后一次送回
- TLS连接复用：工具调用链期间保持keep-alive

## 灵魂不可变原则
- AI通过积累经验和知识调整行为方式，但核心人格不能变
- 可写区域和锁定区域有明确权限控制"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        SCAFFOLDING_PRINCIPLES,
        f"设计问题：{task}",
        max_tokens=300
    ).strip()
    ctx["_design_guidance"] = result
    return ctx

node = Node(id="971", name="AI能力增强脚手架",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["小模型", "模板", "scaffold", "辅助结构", "嵌入式AI",
                          "资源受限", "分层知识", "工具调用", "流式",
                          "批量处理", "消息队列", "模板库"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "design/ai-scaffolding", "category": "design"})
