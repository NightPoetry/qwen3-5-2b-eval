"""知识节点：LM API适配——OpenAI兼容接口的调用模式与常见问题。

融合：LMStudio-API适配工程师 + AI调用常见问题 + OpenAI兼容API转接服务 + CodingPlan接入
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

LM_API_KNOWLEDGE = """你是LLM API集成专家。根据以下知识判断任务涉及的API调用问题，给出具体建议。

## 基础调用规则
- temperature=0.0确定性输出，temperature>0创意输出
- max_tokens限制输出长度不是输入——输入由上下文窗口决定
- system/user/assistant三角色分离——system设角色，user提问题
- 隔离对话=每次独立messages数组，不共享历史
- 模型名必须精确匹配本地推理框架中加载的名字
- 超时设置考虑token生成速度：2B约100-200 tok/s，4096 tok需20-40s

## 本地推理框架对照
| 框架 | API格式 | 默认端口 | API路径 |
|------|---------|---------|--------|
| LM Studio | OpenAI兼容 | 1234 | /v1/chat/completions |
| Ollama | Ollama格式 | 11434 | /api/generate |
| vLLM | OpenAI兼容 | 8000 | /v1/chat/completions |

## URL路径自适应
base_url以/v1结尾时拼/chat/completions，否则拼/v1/chat/completions

## 响应体读取超时
思考模型先返回HTTP 200头，body等思考完才发送。解决：流式输出+空闲超时（每次收到数据重置计时）

## 思考模型输出空白
reasoning_content消耗tokens后max_tokens不够→content截断为空。解决：max_tokens从4096增到16384+

## API转接网关行为特征
- stream:true + tool_choice:auto时模型倾向纯文本不调工具→用tool_choice:required强制
- 每次响应只返回1个tool_call→批量操作用数组参数，多工具分多次请求
- content和tool_calls可能同时存在→优先用tool_calls数据
- 流式tool_call参数分块到达→必须累积所有delta拼接后再JSON.parse

## 聚合网关特殊请求头
某些聚合API网关需要特定User-Agent和版本头才能调用，缺少返回405。必须查阅具体网关文档确认所需请求头

## 排查检查清单
1.确认服务运行 2.确认API格式(OpenAI兼容/Ollama) 3.确认URL路径(/v1) 4.确认模型名 5.确认max_tokens够用 6.确认响应解析字段正确
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        LM_API_KNOWLEDGE +
        "\n分析以下任务涉及的API调用问题，给出具体建议（每条一行，不超过5条）。"
        "如果不涉及API调用问题，回答'无API问题'。",
        f"任务：{task[:600]}",
        max_tokens=300
    ).strip()
    if "无API问题" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx

node = Node(id="395", name="LM API适配",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["LLM", "模型调用", "API调用", "LM Studio", "chat/completions",
                          "temperature", "max_tokens", "Ollama", "vLLM", "stream",
                          "tool_choice", "tool_calls", "SSE", "流式"]},
    execute=execute, refs=["520"],
    metadata={"source": "Guild/AI与LLM应用+LMStudio-API适配工程师", "category": "domain_ai"})
