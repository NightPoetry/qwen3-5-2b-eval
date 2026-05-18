"""节点：JS生成 — 分步：数据层(模型) + 渲染层(模型) + 事件层(系统模板)。"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Node
from llm import ask


def _clean_model_output(raw: str) -> str:
    """清理模型输出：去markdown、去script标签、去DOMContentLoaded包裹。"""
    cleaned = raw
    if "```" in cleaned:
        blocks = re.findall(r'```(?:\w+)?\n(.*?)```', cleaned, re.DOTALL)
        if blocks:
            cleaned = blocks[0]
    if "<script" in cleaned:
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', cleaned, re.DOTALL)
        if scripts:
            cleaned = max(scripts, key=len).strip()
    cleaned = re.sub(
        r"document\.addEventListener\(['\"]DOMContentLoaded['\"],\s*(?:\(\)\s*=>|function\s*\(\))\s*\{",
        "", cleaned
    )
    if cleaned.rstrip().endswith("});"):
        cleaned = cleaned.rstrip()[:-3]
    return cleaned.strip()


def _strip_event_handlers(code: str) -> str:
    """从渲染层去掉模型误加的addEventListener。"""
    lines = code.split("\n")
    result = []
    skip_depth = 0
    for line in lines:
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
        result.append(line)
    return "\n".join(result)


def execute(ctx: dict) -> dict:
    task = ctx["task"]
    contract = ctx["contract"]
    elements = contract["elements"]
    dynamic_elements = contract.get("dynamic_elements", [])
    data = contract["data"]

    storage_key = data["storage_key"]
    data_format = data["format"]
    dynamic_class_list = "\n".join(
        f'  .{e["class"]}({e["tag"]}): {e["purpose"]}' for e in dynamic_elements
    )

    # Step 1: 数据层（模型）
    data_code = ask(
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

    # Step 2: 渲染层（模型）
    render_code = ask(
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

    # Step 3: 事件层（系统模板）
    static_ids = [e["id"] for e in elements]
    get_lines = "\n".join(f"const {eid} = document.getElementById('{eid}');" for eid in static_ids)

    event_code = f"""{get_lines}

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

    # 组装
    data_clean = _clean_model_output(data_code)
    render_clean = _strip_event_handlers(_clean_model_output(render_code))

    assembled = (
        "document.addEventListener('DOMContentLoaded', () => {\n"
        f"\n// === 数据层 ===\n{data_clean}\n"
        f"\n// === 渲染层 ===\n{render_clean}\n"
        f"\n// === 事件层 ===\n{event_code}\n"
        "\n// === 初始化 ===\nloadData();\nrenderList();\n"
        "});\n"
    )
    ctx["raw_js"] = assembled
    return ctx


node = Node(
    id="060",
    name="JS生成(分步)",
    trigger={"type": "key_exists", "key": "contract"},
    execute=execute,
    refs=["072"],
)
