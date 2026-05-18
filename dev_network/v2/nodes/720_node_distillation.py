"""知识节点：节点蒸馏方法论——从知识文档到可执行节点的批量转化。

蒸馏 = 把"需要理解才能用"的知识转化为"不需要理解也能用"的可执行程序。
单节点六步法：识别类型→设计trigger→设计execute→设计refs→脱敏→接入网络。
批量四阶段：扫描分类→映射(增强/新建)→并行蒸馏→验证脱敏。
实证：650文件→151节点（60新建+34增强），归并率~7:1。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

KNOWLEDGE_TYPES = [
    "原则(SKILL.md)→提取检查规则，trigger用keyword，execute做检查/注入",
    "方法论(METHOD.md)→提取步骤序列，execute按步骤展开",
    "领域事实(knowledge)→提取规则列表，trigger用领域关键词",
    "双轨记录(dual-track)→提取通用模式，变成Fix/Develop模板",
    "角色定义(Role)→提取核心立场+诊断步骤，编码为LLM system prompt",
    "设计文档(DesignAndThinking)→提取决策树+权衡矩阵，编码为设计指导",
    "反模式(ANTI-PATTERNS)→提取检测规则",
]

BATCH_PHASES = [
    "Phase1-扫描：并行探索目录，采样文件，识别内容模式和优先级",
    "Phase2-映射：比对现有节点，区分增强/新建，分配ID范围避免冲突",
    "Phase3-蒸馏：读文件→分组归并→脱敏→提取原则→编码execute→写节点",
    "Phase4-验证：ast.parse()语法检查 + grep脱敏词表检查 + 修复泄漏",
]

DISTILL_RULES = [
    "语义判断必须用LLM(ask())，禁止regex做语义决策",
    "格式解析可以用regex（代码大括号、HTML标签等）",
    "搜索节点regex仅做初筛，最终LLM判断",
    "每次ask()只问一个问题（2B单线程）",
    "知识精华编码为ask()的system prompt",
    "trigger宁严勿宽：误触发(噪声)比漏触发(没帮忙)更糟",
    "归并到主题级别：同角色/同主题的多文件合并为一个节点",
    "增强优先于新建：能补充到现有节点的不另建",
]

DISTILL_ANTI_PATTERNS = [
    "每个文件一个节点→节点爆炸触发冲突→归并到主题级别",
    "把整段文档塞进execute→超出2B处理能力→提取核心规则/步骤",
    "trigger用always→每个任务都激活成噪声→用精确keyword",
    "execute中让模型做多件事→小模型会崩→拆成多个节点",
    "refs连接太多节点→选择压力大→只连因果/互补相关",
    "不脱敏→泄露隐私→移除个人信息/项目名/URL",
    "蒸馏事实但不蒸馏操作→还是被动KG→必须有trigger+execute",
    "regex做语义判断→不理解上下文会误判→改用LLM",
]

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    ktype = ask(
        "这段内容需要怎样蒸馏为可执行节点？判断知识类型。\n"
        "选项：原则/方法论/领域事实/双轨记录/角色定义/设计文档/反模式\n"
        "只回答类型名。",
        f"知识内容：{task[:300]}",
        max_tokens=15
    ).strip()

    ctx["_distill_guide"] = {
        "detected_type": ktype,
        "knowledge_types": KNOWLEDGE_TYPES,
        "batch_phases": BATCH_PHASES,
        "rules": DISTILL_RULES,
        "anti_patterns": DISTILL_ANTI_PATTERNS,
        "checklist": [
            "trigger不会在无关任务上误触发",
            "execute中模型最多只做一件事",
            "语义判断用LLM不用regex",
            "refs只连接真正相关的节点",
            "已脱敏（无个人信息/项目名/URL）",
            "metadata标注了来源和类别",
            "相关文件已归并（不是1:1映射）",
        ],
        "principle": "蒸馏的产出不是文档摘要——是带trigger/execute/refs的可执行程序",
        "scale_reference": "650文件→60新节点+34增强，归并率~7:1",
    }
    return ctx

node = Node(id="720", name="节点蒸馏",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["蒸馏", "节点", "内化", "编成节点", "知识转化",
                          "批量蒸馏", "转化为节点"]},
    execute=execute, refs=["300"],
    metadata={"source": "Skills/节点蒸馏+实证方法论", "category": "meta"})
