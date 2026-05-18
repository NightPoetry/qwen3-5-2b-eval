"""知识节点：AI辅助编程上下文管理——会话压缩/迁移/滑动窗口。

融合：ClaudeCode上下文管理经验 + 项目迁移经验
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

CONTEXT_KNOWLEDGE = """你是AI辅助编程工具专家。根据以下知识诊断上下文管理问题。

## 上下文价值分类
| 类型 | 后续价值 | 处理策略 |
|------|---------|---------|
| 用户请求 | 高 | 完整保留 |
| 文件读取原文 | 高 | 完整保留 |
| 代码修改 | 高 | 完整保留 |
| 原则思考 | 中 | 保留 |
| 执行决策 | 低 | 去除 |
| 循环轮询输出 | 低 | 合并摘要 |
| 错误堆栈 | 低频高值 | 外置存储+引用标记 |

## 压缩原则
- 压缩不是删除而是提炼
- 用独立进程压缩（执行压缩本身产生上下文）
- 新进程读取旧会话jsonl→压缩→提示用户重启

## 滑动窗口分析
- 以10条消息为窗口分析连续工具调用序列
- 识别状态变化的转折点
- 保留有意义变化，去除无变化的中间检查

## Thinking Block分类
- 含"本质/原则/策略/架构/经验/教训"→保留
- 含"我决定/让我/调用/执行"→去除
- 混合类→提取原则部分

## 项目迁移
- AI辅助工具的会话数据在~/.claude/projects/下按路径编码存储
- 路径编码规则：/→-，非ASCII字符→-，下划线→-，前缀-
- 迁移步骤：确认引用→移动目录→重命名编码路径→验证会话恢复
- history.jsonl和sessions/不需要改，它们不影响会话匹配
- 子路径的独立会话数据同样需要迁移
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        CONTEXT_KNOWLEDGE +
        "\n分析以下任务涉及的AI编程工具上下文管理问题，给出建议（每条一行，不超过4条）。"
        "如果不涉及此类问题，回答'无相关问题'。",
        f"任务：{task[:500]}",
        max_tokens=250
    ).strip()
    if "无相关问题" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx

node = Node(id="E00", name="AI编程上下文管理",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["上下文", "context", "会话", "session", "压缩",
                          "迁移", "migration", "claude", "jsonl", "token限制",
                          "窗口", "thinking block"]},
    execute=execute, refs=["Y20"],
    metadata={"source": "Guild/开发工具与工作流/ClaudeCode使用经验", "category": "domain_dev_tools"})
