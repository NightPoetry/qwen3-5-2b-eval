"""节点：接口契约生成（Phase 2）— 纯系统逻辑，不调用模型。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Node


# 静态元素规则
STATIC_RULES = [
    (["输入", "文本", "input"], "taskInput", "input"),
    (["添加", "提交", "button", "保存"], "addBtn", "button"),
    (["列表", "显示", "list", "ul"], "taskList", "ul"),
]

# 动态元素规则（列表项内）
DYNAMIC_RULES = [
    (["删除", "移除"], "delete-btn", "button"),
    (["完成", "标记", "checkbox", "勾选"], "toggle-done", "input[checkbox]"),
]


def execute(ctx: dict) -> dict:
    raw = ctx.get("components", "")
    lines = [l.strip().lstrip("-·•* ") for l in raw.strip().split("\n") if l.strip()]

    static_elements = []
    dynamic_elements = []
    used = set()

    for line in lines:
        for keywords, eid, tag in STATIC_RULES:
            if any(kw in line.lower() for kw in keywords) and eid not in used:
                static_elements.append({"id": eid, "tag": tag, "purpose": line})
                used.add(eid)
                break
        for keywords, cls, tag in DYNAMIC_RULES:
            if any(kw in line.lower() for kw in keywords) and cls not in used:
                dynamic_elements.append({"class": cls, "tag": tag, "purpose": line})
                used.add(cls)
                break

    # 保底
    for eid, tag, purpose in [
        ("taskInput", "input", "输入任务文本"),
        ("addBtn", "button", "添加任务"),
        ("taskList", "ul", "显示任务列表"),
    ]:
        if eid not in used:
            static_elements.append({"id": eid, "tag": tag, "purpose": purpose})

    if not dynamic_elements:
        dynamic_elements = [
            {"class": "delete-btn", "tag": "button", "purpose": "每项的删除按钮"},
            {"class": "toggle-done", "tag": "input[checkbox]", "purpose": "每项的完成勾选"},
        ]

    ctx["contract"] = {
        "elements": static_elements,
        "dynamic_elements": dynamic_elements,
        "data": {"storage_key": "todos", "format": "[{id: number, text: string, done: boolean}]"},
        "events": [
            {"element_id": "addBtn", "trigger": "click", "action": "添加项"},
            {"element_id": "taskInput", "trigger": "keypress(Enter)", "action": "回车添加"},
            {"element_id": "taskList", "trigger": "click(.delete-btn)", "action": "删除项"},
            {"element_id": "taskList", "trigger": "change(.toggle-done)", "action": "切换完成"},
        ],
    }
    return ctx


node = Node(
    id="030",
    name="接口契约",
    trigger={"type": "key_exists", "key": "components"},
    execute=execute,
    refs=["040", "050", "060"],
)
