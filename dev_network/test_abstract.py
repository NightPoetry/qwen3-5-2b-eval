"""
抽象分层架构测试。

核心思想：各层共享抽象接口描述，不共享实现代码。
  Phase 1: 组件设计 — 有什么组件、每个做什么
  Phase 2: 接口定义 — 每个组件的元素ID、事件、数据流
  Phase 3: 分层实现 — HTML/CSS/JS 各自只看接口描述生成代码

模型在写 JS 时不看 HTML，写 CSS 时不看 JS。
它们共享的是"组件有什么、做什么"的抽象描述。
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import requests
from validator import validate_file, validate_id_consistency

API_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-2b"
TIMEOUT = 120


def isolated_chat(system: str, user: str, max_tokens: int = 512) -> str:
    resp = requests.post(API_URL, json={
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def phase0_interaction_design(task: str) -> str:
    """
    Phase 0: 交互设计（驱动一切的源头）。
    遵循"最少决定原则"：用户做什么 → 需要什么元素 → 元素怎么互动。
    """
    return isolated_chat(
        "你是交互设计师。用最简方式描述用户和应用的交互。",
        (f"应用：{task}\n\n"
         "按以下格式描述交互（每行一个用户动作）：\n"
         "  用户动作 → 界面响应\n\n"
         "示例（计算器）：\n"
         "  点数字按钮 → 显示区追加数字\n"
         "  点运算符 → 保存当前数，等待下一个\n"
         "  点等号 → 计算结果显示\n"
         "  点清除 → 清空显示区\n\n"
         "现在描述："),
        max_tokens=300
    )


def phase1_components(task: str, interactions: str) -> str:
    """Phase 1: 从交互设计中提取具体UI元素。"""
    return isolated_chat(
        "列出交互中涉及的具体UI元素。每行：标签类型 用途。不要解释。",
        (f"应用：{task}\n\n用户交互：\n{interactions}\n\n"
         "列出上述交互中需要的具体HTML元素：\n"
         "格式（每行一个）：\n"
         "  input 用户输入任务文本\n"
         "  button 点击添加\n"
         "  ul 显示列表\n\n"
         "只列出元素："),
        max_tokens=200
    )


def phase2_interface(task: str, components: str) -> dict:
    """
    Phase 2: 接口契约。
    模型只说"有什么元素、做什么"（语义），系统分配 ID（确定性）。

    关键区分：
      - static_elements: HTML中固定存在的顶级元素（有ID）
      - dynamic_elements: JS在列表项内动态创建的（有class，无顶级ID）
    """
    raw = isolated_chat(
        "列出应用的UI元素。每行：类型 用途。不要编号不要解释。",
        (f"应用：{task}\n\n"
         "列出可交互的UI元素：\n"
         "格式：\n"
         "  input 输入新任务的文本\n"
         "  button 点击添加任务\n"
         "  ul 显示任务列表\n\n"
         "现在列出："),
        max_tokens=200
    )

    # 系统确定性分配 ID
    # 静态元素：页面上始终存在的
    static_rules = [
        (["输入", "文本", "input"], "taskInput", "input"),
        (["添加", "提交", "button", "保存"], "addBtn", "button"),
        (["列表", "显示", "list", "ul"], "taskList", "ul"),
    ]
    # 动态元素：由JS在每个列表项中创建
    dynamic_rules = [
        (["删除", "移除"], "delete-btn", "button"),
        (["完成", "标记", "checkbox", "勾选"], "toggle-done", "input[checkbox]"),
    ]

    lines = [l.strip().lstrip("-·•* ") for l in raw.strip().split("\n") if l.strip()]

    static_elements = []
    dynamic_elements = []
    used_ids = set()

    for line in lines:
        for keywords, eid, tag in static_rules:
            if any(kw in line.lower() for kw in keywords) and eid not in used_ids:
                static_elements.append({"id": eid, "tag": tag, "purpose": line})
                used_ids.add(eid)
                break
        for keywords, cls, tag in dynamic_rules:
            if any(kw in line.lower() for kw in keywords) and cls not in used_ids:
                dynamic_elements.append({"class": cls, "tag": tag, "purpose": line})
                used_ids.add(cls)
                break

    # 保底：确保核心三静态元素存在
    for eid, tag, purpose in [
        ("taskInput", "input", "输入任务文本"),
        ("addBtn", "button", "添加任务"),
        ("taskList", "ul", "显示任务列表"),
    ]:
        if eid not in used_ids:
            static_elements.append({"id": eid, "tag": tag, "purpose": purpose})

    # 保底：确保动态元素描述存在
    if not dynamic_elements:
        dynamic_elements = [
            {"class": "delete-btn", "tag": "button", "purpose": "每项的删除按钮"},
            {"class": "toggle-done", "tag": "input[checkbox]", "purpose": "每项的完成勾选"},
        ]

    events = [
        {"element_id": "addBtn", "trigger": "click", "action": "读取输入框文本，添加到列表"},
        {"element_id": "taskInput", "trigger": "keypress(Enter)", "action": "回车也能添加"},
        {"element_id": "taskList", "trigger": "click(.delete-btn)", "action": "删除对应项"},
        {"element_id": "taskList", "trigger": "change(.toggle-done)", "action": "切换完成状态"},
    ]
    data = {"storage_key": "todos", "format": "[{id: number, text: string, done: boolean}]"}

    return {
        "elements": static_elements,
        "dynamic_elements": dynamic_elements,
        "data": data,
        "events": events,
    }


def _strip_inline_handlers(render_code: str) -> str:
    """
    从渲染层代码中剥离模型错误添加的 addEventListener 调用。
    渲染层只应创建DOM元素，事件由事件层统一委托处理。
    """
    lines = render_code.split("\n")
    result = []
    skip_depth = 0

    for line in lines:
        # 检测 addEventListener 调用开始
        if "addEventListener" in line and skip_depth == 0:
            skip_depth = line.count("{") - line.count("}")
            if skip_depth <= 0:
                skip_depth = 0
            continue

        if skip_depth > 0:
            skip_depth += line.count("{") - line.count("}")
            if skip_depth <= 0:
                skip_depth = 0
            continue

        # 跳过模型的啰嗦注释（包含"事件"/"绑定"/"委托"字样）
        stripped = line.strip()
        if stripped.startswith("//") and any(
            kw in stripped for kw in ["事件", "绑定", "委托", "addEventListener", "event"]
        ):
            continue

        result.append(line)

    return "\n".join(result)


def _generate_event_code(static_ids: list[str], storage_key: str) -> str:
    """系统确定性生成事件绑定代码。无需模型参与。"""
    # 获取元素
    get_lines = "\n".join(
        f"const {eid} = document.getElementById('{eid}');"
        for eid in static_ids
    )

    return f"""{get_lines}

function addItem() {{
  const text = taskInput.value.trim();
  if (!text) return;
  items.push({{ id: Date.now(), text: text, done: false }});
  saveData();
  renderList();
  taskInput.value = '';
}}

addBtn.addEventListener('click', addItem);
taskInput.addEventListener('keypress', (e) => {{
  if (e.key === 'Enter') addItem();
}});

taskList.addEventListener('click', (e) => {{
  if (e.target.classList.contains('delete-btn')) {{
    const id = Number(e.target.dataset.id);
    items = items.filter(item => item.id !== id);
    saveData();
    renderList();
  }}
}});

taskList.addEventListener('change', (e) => {{
  if (e.target.classList.contains('toggle-done')) {{
    const li = e.target.closest('li');
    if (!li) return;
    const id = Number(li.dataset.id);
    const item = items.find(i => i.id === id);
    if (item) {{
      item.done = !item.done;
      saveData();
      renderList();
    }}
  }}
}});"""


def phase3_generate_js_decomposed(task: str, contract: dict) -> str:
    """
    Phase 3-JS: 分步生成 JS（每步独立隔离调用）。

    拆为三层：
      Step 1: 数据层 — localStorage 读写 + 状态定义
      Step 2: 渲染层 — renderList 函数（从状态生成DOM）
      Step 3: 事件层 — addEventListener 绑定

    系统负责组装，模型只写单层逻辑。
    """
    elements = contract.get("elements", [])
    dynamic_elements = contract.get("dynamic_elements", [])
    data = contract.get("data", {})
    events = contract.get("events", [])

    static_id_list = "\n".join(f'  #{e["id"]}: {e["purpose"]}' for e in elements)
    dynamic_class_list = "\n".join(
        f'  .{e["class"]}({e["tag"]}): {e["purpose"]}' for e in dynamic_elements
    )
    storage_key = data.get("storage_key", "data")
    data_format = data.get("format", "[{id, text, done}]")

    # Step 1: 数据层
    data_code = isolated_chat(
        "你是 JavaScript 开发者。只输出纯 JS 代码，不要任何 HTML。",
        (f"为 {task} 编写数据层。\n\n"
         f"要求：\n"
         f"  1. 定义 let items = [];\n"
         f"  2. 写 loadData() 函数：从 localStorage.getItem('{storage_key}') 读取 JSON 赋值给 items\n"
         f"  3. 写 saveData() 函数：把 items 存入 localStorage\n"
         f"  4. 数据格式：{data_format}\n\n"
         f"只写这3个东西，不要事件绑定，不要DOM操作。"),
        max_tokens=512
    )

    # Step 2: 渲染层
    render_code = isolated_chat(
        "你是 JavaScript 开发者。只输出纯 JS 代码，不要任何 HTML。",
        (f"为 {task} 编写渲染函数。\n\n"
         f"已有变量：items 数组，格式 {data_format}\n"
         f"列表容器ID：taskList\n\n"
         f"每个列表项内动态创建的子元素：\n{dynamic_class_list}\n\n"
         f"要求：\n"
         f"  1. 写 renderList() 函数\n"
         f"  2. 清空 taskList 的 innerHTML\n"
         f"  3. 遍历 items，每项创建 <li>，设置 li.dataset.id = item.id：\n"
         f"     - span 显示 item.text\n"
         f"     - button class='delete-btn'，textContent='×'，dataset.id=item.id\n"
         f"     - input type='checkbox' class='toggle-done'，checked=item.done\n"
         f"     - 如果 item.done=true，li 加 class 'done'\n"
         f"  4. 用 document.getElementById('taskList') 获取容器\n\n"
         f"只写 renderList 函数，不要事件绑定，不要数据存储代码。"),
        max_tokens=768
    )

    # Step 3: 事件层（系统确定性模板生成，不需要模型）
    # 事件绑定是确定性的：给定契约中的元素ID和事件描述，代码是固定的
    static_ids = [e["id"] for e in elements]
    event_code = _generate_event_code(static_ids, storage_key)

    # 清理模型输出（数据层、渲染层）
    model_parts = []
    for raw in [data_code, render_code]:
        cleaned = raw
        # 去 markdown 代码块
        if "```" in cleaned:
            blocks = re.findall(r'```(?:\w+)?\n(.*?)```', cleaned, re.DOTALL)
            if blocks:
                cleaned = blocks[0]
        # 去 script 标签
        if "<script" in cleaned:
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', cleaned, re.DOTALL)
            if scripts:
                cleaned = max(scripts, key=len).strip()
        # 去掉模型自带的 DOMContentLoaded 包裹（系统统一包裹）
        cleaned = re.sub(
            r"document\.addEventListener\(['\"]DOMContentLoaded['\"],\s*(?:\(\)\s*=>|function\s*\(\))\s*\{",
            "", cleaned
        )
        # 去掉对应的末尾闭合
        if cleaned.rstrip().endswith("});"):
            cleaned = cleaned.rstrip()[:-3]
        model_parts.append(cleaned.strip())

    # 渲染层后处理：剥离模型错误添加的事件绑定
    render_cleaned = _strip_inline_handlers(model_parts[1])
    model_parts[1] = render_cleaned

    # 系统确定性组装（事件层由系统模板生成，无需清理）
    assembled = (
        "document.addEventListener('DOMContentLoaded', () => {\n"
        "\n// === 数据层 ===\n"
        f"{model_parts[0]}\n"
        "\n// === 渲染层 ===\n"
        f"{model_parts[1]}\n"
        "\n// === 事件层 ===\n"
        f"{event_code}\n"
        "\n// === 初始化 ===\n"
        "loadData();\n"
        "renderList();\n"
        "});\n"
    )
    return assembled


def phase3_generate(task: str, contract: dict, target: str) -> str:
    """Phase 3: 分层实现（每层只看接口契约中自己需要的部分）"""
    elements = contract.get("elements", [])
    data = contract.get("data", {})
    events = contract.get("events", [])

    # JS 使用分步生成
    if target == "js":
        return phase3_generate_js_decomposed(task, contract)

    # 系统层构建：从契约中提取每层需要的信息（确定性）
    id_list = ", ".join(f'{e["id"]}({e["tag"]})' for e in elements)
    purpose_list = "\n".join(f'  #{e["id"]}: {e["purpose"]}' for e in elements)

    if target == "html":
        system = (
            "你是 HTML 开发者。只输出 HTML 代码。使用中文文本。\n"
            "head 中用 <link rel=\"stylesheet\" href=\"style.css\">。\n"
            "body 末尾用 <script src=\"app.js\"></script>。\n"
            "不写 <style>，不写 inline JS。"
        )
        user = (
            f"创建 {task} 的 HTML 页面。\n\n"
            f"【必须使用以下 ID（不得改名）】：\n{purpose_list}\n\n"
            f"元素标签：{id_list}\n"
            f"页面标题用中文。"
        )
    elif target == "css":
        system = (
            "你是 CSS 开发者。只输出纯 CSS 代码（不要 HTML）。\n"
            "简洁现代风格，max-width:600px 居中。"
        )
        user = (
            f"为 {task} 编写样式。\n\n"
            f"需要样式的元素：\n{purpose_list}\n\n"
            f"要求：容器居中、输入框全宽、按钮醒目、列表项有间距。"
        )
    else:
        return ""

    return isolated_chat(system, user, max_tokens=2048)


def run(task: str, output_name: str):
    print(f"\n{'='*60}")
    print(f"任务: {task}")
    print(f"{'='*60}")

    # Phase 0
    print("\nPhase 0: 交互设计")
    interactions = phase0_interaction_design(task)
    print(f"  {interactions}")

    # Phase 1
    print("\nPhase 1: 元素提取")
    components = phase1_components(task, interactions)
    print(f"  {components}")

    # Phase 2
    print("\nPhase 2: 接口契约")
    contract = phase2_interface(task, components)
    print(f"  static:  {[e['id'] for e in contract.get('elements', [])]}")
    print(f"  dynamic: {[e['class'] for e in contract.get('dynamic_elements', [])]}")
    print(f"  data: {contract.get('data', {})}")
    print(f"  events: {len(contract.get('events', []))} 个")

    # Phase 3
    print("\nPhase 3: 分层实现（每层读取同一份契约）")
    results = {}
    for target, filename in [("html", "index.html"), ("css", "style.css"), ("js", "app.js")]:
        raw = phase3_generate(task, contract, target)

        # 去 markdown 标记
        if "```" in raw:
            blocks = re.findall(r'```(?:\w+)?\n(.*?)```', raw, re.DOTALL)
            if blocks:
                raw = blocks[0]

        # 确定性验证修复
        all_files = {"index.html": "", "style.css": "", "app.js": ""}
        fixed, issues = validate_file(filename, raw, all_files)

        status = "无问题" if not issues else f"修复 {len(issues)} 个问题"
        print(f"  {filename}: {len(fixed)} chars — {status}")
        for iss in issues:
            print(f"    [{iss.severity}] {iss.message} → {iss.fix}")

        results[filename] = fixed

    # Phase 4: ID一致性验证（跨文件）
    print("\nPhase 4: ID一致性验证")
    html_fixed, js_fixed, id_issues = validate_id_consistency(
        contract, results["index.html"], results["app.js"]
    )
    if id_issues:
        results["index.html"] = html_fixed
        results["app.js"] = js_fixed
        for iss in id_issues:
            print(f"  [{iss.severity}] {iss.message} → {iss.fix}")
    else:
        print("  所有契约ID已在HTML和JS中找到 ✓")

    # 保存
    output_dir = Path(__file__).parent / output_name
    output_dir.mkdir(exist_ok=True)
    for name, content in results.items():
        (output_dir / name).write_text(content)

    print(f"\n保存到: {output_dir}")
    return results


def main():
    run("待办事项 Web 应用（添加、删除、标记完成，localStorage 存储）",
        "output_todo_v3")


if __name__ == "__main__":
    main()
