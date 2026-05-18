# v2 可执行知识网络

164 个节点 × 栈展开引擎 = 让 2B 模型具备远超裸能力的任务处理能力。

## 架构

```
engine.py   — 执行引擎（栈展开 + 触发检查 + 三级光标续入），~200 行
llm.py      — LLM 调用（隔离对话，每次只问一个问题），~25 行
nodes/      — 164 个可执行节点（每个 = trigger + execute + refs）
web/        — Flask Web 界面 + Three.js 3D 可视化
```

## 节点编写规范

```python
"""知识节点：名称——一句话描述。"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask("你的角色和知识...", f"用户问题：{task}", max_tokens=200)
    ctx["_output_key"] = result.strip()
    return ctx

node = Node(id="XXX", name="名称",
    trigger={"type": "keyword", "target": "task", "keywords": [...]},
    execute=execute, refs=["Y30"],
    metadata={"source": "...", "category": "..."})
```

**铁律**：
- `execute` 中 LLM 只做一件事（2B 单线程）
- 语义判断用 `ask()`，不用 regex
- `refs` 必须非空（除非是输出节点 Y*）
- 每个节点必须被至少一个上游节点的 refs 引用（否则不可达）

## 触发类型

| type | 说明 | 示例 |
|------|------|------|
| `keyword` | task 中包含任一关键词 | `{"keywords": ["修复", "bug"]}` |
| `regex` | task 匹配正则（仅用于格式匹配） | `{"pattern": "[\\u4e00-\\u9fff]"}` |
| `key_exists` | context 中存在某个 key | `{"key": "_reasoning"}` |
| `condition` | 表达式求值为真 | `{"expr": "len(_turns) > 3"}` |
| `always` | 无条件触发（通常被 refs 控制到达） | |
| `entry` | 仅入口节点使用 | |

## 节点 ID 约定

| 范围 | 类别 |
|------|------|
| 000-090 | 核心生成管线 |
| 100-250 | 质量精炼 |
| 300-399 | 推理认知 |
| 400-499 | 安全监控 |
| 500-599 | 元方法论 |
| 600-699 | 开发方法论/平台 |
| 700-799 | 技能/蒸馏管线 |
| 800-899 | 对话 |
| 900-949 | 角色行为 |
| 950-999 | 理论/设计/通用原则 |
| A00-D00 | 域路由 |
| E00-E99 | 扩展领域 |
| Y10-Y40 | 输出锚点 |

## 运行

```bash
# 环境变量（可选，默认 localhost:1234）
export LLM_API_URL="http://<IP>:1234/v1/chat/completions"
export LLM_MODEL="qwen3.5-2b"

# Web 界面
cd web && python app.py
```
