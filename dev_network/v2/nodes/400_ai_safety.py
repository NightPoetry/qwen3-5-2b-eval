"""知识节点：AI Agent安全——指令完整性/风险分级/资源预算/用户主权/数据保护。

适用于涉及自主Agent、自动化执行、长跑AI系统的任务。
融合：ai-agent-safety
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SAFETY_KNOWLEDGE = """你是AI Agent安全专家。根据以下知识评估任务中的安全风险。

## 指令完整性与截断
- LLM输出+上下文压缩+流式拼接任何环节都可能让指令半截（如rm -rf截到rm -rf后接空）
- L1+指令执行前必须两条独立路径校验（同一推理结果不算二次验证）
- 截断检测启发式：rm -rf后空/SQL以WHERE结尾/引号未闭合奇数/命令以&&||;结尾/占位符未替换——命中即拒

## 风险分级（L0-L3）
- L0只读=一次解析；L1局部写=二次验证；L2跨界影响=二次验证+告知；L3不可逆=二次验证+警示UI+两阶段确认
- L3警示UI必须：警示色边框+完整指令逐字显示+影响范围量化+不可恢复性提示+3-5秒倒计时
- L1+指令全验证链必须写审计：原始字符串hash+解析结果+启发式结果+用户确认事件

## 资源预算（五维度）
- 长跑全权限系统必须有显式预算：LLM成本、磁盘、CPU、网络、时间（互不替代）
- 每维度软警告+硬上限双层；软停必须真的阻塞等用户输入
- 预算实时拦截（每次调用前check_before，完成后record_after），不是事后审计
- 大额操作（如全量扫描）须告知成本估算，超$0.10须确认
- 预算计入失败的重试

## 用户主权
- 用户原话永不修改/总结/删除（审计完整性根基）
- AI自动学到的偏好必须当次告知用户并允许一句话否决
- 用户必须能问"为什么做了X"得到完整决策链路
- 否决经验改applicability为rejected，不删除

## 数据保护
- 任何写入操作前必须完整备份+验证完整性+附还原说明
- schema变更须forward+rollback+idempotent迁移工具
- 敏感数据（API key/token/密码）写入日志前必须redact

## 失效模式
- 默认偏好fail-stop（保护用户数据+可溯源），只有影响有限+有降级才用fail-safe
- fail-stop后不自动崩溃：停止任务+持久化状态+flush审计+等用户决定
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        SAFETY_KNOWLEDGE +
        "\n分析以下任务涉及的AI安全风险，按风险等级（L0-L3）给出具体建议（每条一行，不超过5条）。"
        "如果任务不涉及Agent安全风险，回答'无Agent安全风险'。",
        f"任务：{task[:600]}",
        max_tokens=300
    ).strip()

    if "无Agent安全风险" not in result:
        ctx.setdefault("_safety_rules", []).append(result)
    return ctx

node = Node(id="400", name="AI安全规则",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["agent", "AI", "安全", "自动化", "自主", "autonomous",
                          "全权限", "长跑", "预算", "风险", "L3", "不可逆"]},
    execute=execute, refs=["470", "330"],
    metadata={"source": "knowledge/ai-agent-safety", "category": "safety"})
