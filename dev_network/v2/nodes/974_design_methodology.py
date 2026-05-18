"""知识节点：设计方法论——三层文档管理、冲突覆盖原则、变更追溯。

从设计文档管理实践中提炼的通用方法论：
  - 三层文档结构：原文记录(完整保留) + 整理文档(保持简洁) + 变更日志(工作留痕)
  - 冲突覆盖原则：原文记录不删旧的(证据链)，整理文档删除旧的(可读性)
  - 一切皆可追溯：时间戳必须有
  - 讨论在先：组织方式、命名规则、更新模式，三问确认后再创建
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

METHODOLOGY_PRINCIPLES = """你是设计方法论顾问。基于以下经过验证的设计原则回答问题。

## 三层文档管理
- 原文记录：用户原话+时间戳，完整保留，不删除旧的（保留完整证据链）
- 整理文档：正式内容，保持简洁，删除旧的被覆盖的内容（可读性优先）
- 变更日志：记录每次修正，引用前后原文（工作留痕）

## 冲突覆盖处理
- 原文记录：追加新记录，旧记录不清除
- 整理文档：更新正文，删除旧的无用内容
- 变更日志：记录修正，标注纠正关系

## 文件组织约定
- 创建前三问：组织方式(要不要建文件夹)、命名规则(什么格式)、更新模式(一次性还是反复更新)
- 约定记录到共识区，下次同类请求按约定执行
- 复用约定：先检查有没有已约定的流程，有则执行，无则讨论后记录

## 知识记录分类
- 约定/规则 → 共识区（每次加载）
- 用户偏好 → 知识区（按需加载）
- 具体事件 → 经验区（按需加载）
- 文件/笔记 → 工作区（用户可见）

## 核心原则
- 一切皆可追溯：时间戳必须有
- 讨论在先：不单方面决定组织方式
- 原文不可篡改：原始记录是证据链"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        METHODOLOGY_PRINCIPLES,
        f"设计问题：{task}",
        max_tokens=300
    ).strip()
    ctx["_design_guidance"] = result
    return ctx

node = Node(id="974", name="设计方法论",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["文档管理", "变更日志", "原文记录", "整理文档", "冲突覆盖",
                          "追溯", "命名规则", "文件组织", "约定", "知识分类",
                          "文档结构", "设计流程"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "design/methodology", "category": "design"})
