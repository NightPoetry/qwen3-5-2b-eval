"""知识节点：AI辅助翻译方法——翻译游戏或应用的完整流程和说人话原则。

六步流程：创建副本→摸清结构→配置字体→翻译文本→质量检查→交付。
翻译铁律：骂人词保持力度/口语用短句/情绪词优先/语调跟随场所切换。
AI翻译典型病：论文腔/逻辑腔/中性腔/含蓄病/发挥病。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

TRANSLATION_STEPS = [
    "1. 创建副本（永远不动原版）",
    "2. 摸清文件结构（哪些含用户可见文字，编码，翻译框架）",
    "3. 配置字体（中文字体不配=显示方框）",
    "4. 翻译文本（核心手动，场景并行，保持代码结构不变）",
    "5. 质量检查（语法错误、中文引号破坏字符串、翻译完整度）",
    "6. 交付（英文原版+中文版互不干扰）",
]

TRANSLATION_RULES = [
    "先复制再翻译——永远不动原版",
    "先配字体再翻译——否则看不到效果",
    "核心手动、场景并行——效率和质量兼顾",
    "语气匹配原文——原文粗鲁就粗鲁，原文文雅就文雅",
    "补充语境但不编造——中文需要比英文更具体，但不加原文没有的意思",
    "翻完自问像人话吗——读一遍，不像口语就重写",
]

AI_TRANSLATION_DISEASES = [
    "论文腔：'达到了极限''在某种程度上'→换口语：零、压根、根本",
    "逻辑腔：'如果A那么B，另一方面C'→断成短句去掉连接词",
    "中性腔：所有角色说话一个温度→先判断角色性格再选词",
    "含蓄病：AI倾向委婉→直接用对应力度的词",
    "发挥病：原文没有的内容被添加→对照原文逐句检查",
]

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    # 让模型判断翻译目标类型（一件简单事）
    target_type = ask(
        "这个翻译任务的目标是什么类型？从选项中选一个。\n"
        "选项：游戏/应用/文档/字幕/其他\n只回答类型名。",
        f"任务：{task}",
        max_tokens=10
    ).strip()

    ctx["_translation_guide"] = {
        "target_type": target_type,
        "steps": TRANSLATION_STEPS,
        "rules": TRANSLATION_RULES,
        "ai_diseases": AI_TRANSLATION_DISEASES,
        "check_items": [
            "中文引号会破坏字符串→翻译文本中引号只用英文单引号",
            "编译缓存冲突→删除旧缓存文件让程序重新编译",
            "像人话吗→读出声，想象真人站在面前说",
            "温度匹配吗→原文骂人/调情/叙述，中文是同一温度吗",
        ],
    }
    return ctx

node = Node(id="730", name="翻译方法",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["翻译", "translate", "汉化", "中文化", "本地化",
                          "localization", "i18n"]},
    execute=execute, refs=["700"],
    metadata={"source": "Skills/翻译作品", "category": "creation"})
