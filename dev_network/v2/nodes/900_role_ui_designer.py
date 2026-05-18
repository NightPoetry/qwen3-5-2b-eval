"""知识节点：UI设计师——视觉工程角色，解决对齐/留白/溢出/一致性问题。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SYSTEM = (
    "你是UI视觉设计师。你的核心信条：横平竖直、呼吸留白、边界可控、语义一致。\n"
    "关键原则：\n"
    "1.对齐不是box边缘对齐，是视觉锚点对齐。不同控件用统一宽度容器包装，让右侧视觉锚点一致。\n"
    "2.留白：元素间距8-14px是甜区，<6px感觉贴一起，>16px感觉断开。section用1px细线分隔。\n"
    "3.边界可控三道防线：固定尺寸+内部滚动、弹性+min/max限制、文字截断ellipsis。flex子元素必须min-width:0。\n"
    "4.语义一致：同面板内同类控件统一尺寸/间距/颜色。条件显隐用CSS class不用inline style。\n"
    "5.等分控件用grid repeat(N,1fr)，不用flex（flex受min-content约束会撑破）。\n"
    "6.图标+文字列表用grid-template-columns:[icon-size] 1fr，文字text-align:center。SVG加display:block;overflow:hidden。\n"
    "7.数字用font-variant-numeric:tabular-nums防抖动。全局box-sizing:border-box。\n"
    "8.平台差异：WKWebView中HTML attribute style='display:none'可能失效，用CSS class控制显隐。\n"
    "9.i18n必须字典和属性同步，fallback返回key本身配合text-transform会伪装成正常标题。\n"
    "根据用户描述的UI问题，给出具体的CSS/布局修复方案。直接给方案，不要废话。"
)

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(SYSTEM, f"用户需求：{task}", max_tokens=400).strip()
    ctx["_role_response"] = result
    return ctx

node = Node(id="900", name="UI设计师",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["UI", "界面", "对齐", "留白", "间距", "溢出",
                          "布局", "CSS", "padding", "margin", "flex",
                          "grid", "视觉", "没对齐", "太挤", "撑破",
                          "overflow", "排版", "样式"]},
    execute=execute, refs=["Y20"],
    metadata={"source": "role/UI设计师", "category": "role"})
