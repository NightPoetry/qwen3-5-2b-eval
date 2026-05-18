"""
端到端测试：用户只说一句话，系统自动完成全部开发。

流程：
  用户输入 → 自动分解 → 知识路由 → 隔离执行 → 文件输出
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orchestrator import Orchestrator, SubTask

API_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-2b"

KNOWLEDGE = {
    "html结构": "HTML: 语义化标签(header/nav/main/footer), viewport meta, charset UTF-8, 外部CSS用<link>",
    "css布局": "CSS: box-sizing:border-box, max-width居中, flex/grid布局, 间距8-14px, 防溢出min-width:0",
    "响应式": "响应式: 移动优先, @media(min-width:768px), max-width限制, 图片max-width:100%",
    "javascript": "JS: DOM操作, addEventListener, localStorage读写, JSON.parse/stringify",
    "交互": "交互: 用户操作即时反馈, 状态可见, 撤销可逆, 动画smooth",
    "表单": "表单: input验证, placeholder提示, submit防重复, 回车提交",
}


def spec_expand(task_goal: str, subtask: SubTask) -> str:
    """规格展开：让模型细化子任务需要的具体内容（隔离对话）"""
    import requests
    resp = requests.post(API_URL, json={
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你是需求分析师。用 3-5 个要点列出文件需要包含的具体内容。简短。"},
            {"role": "user", "content": (
                f"项目目标：{task_goal}\n"
                f"文件：{subtask.name}\n"
                f"文件用途：{subtask.description}\n\n"
                f"这个文件需要包含哪些具体内容？列出要点："
            )},
        ],
        "temperature": 0.0,
        "max_tokens": 256,
    }, timeout=60)
    return resp.json()["choices"][0]["message"]["content"]


def enhance_subtask_description(subtask: SubTask, all_subtasks: list[SubTask],
                                task_goal: str) -> str:
    """系统层增强子任务描述：规格展开 + 跨文件约束"""
    # 规格展开（隔离微对话）
    spec = spec_expand(task_goal, subtask)

    desc = f"{subtask.description}\n\n具体内容要求：\n{spec}\n\n技术约束：\n"
    ext = subtask.name.split(".")[-1] if "." in subtask.name else ""

    if ext == "html":
        css_files = [st.name for st in all_subtasks if st.name.endswith(".css")]
        js_files = [st.name for st in all_subtasks if st.name.endswith(".js")]
        if css_files:
            desc += f"- 用 <link rel='stylesheet' href='{css_files[0]}'> 引用样式\n"
        if js_files:
            desc += f"- 在 </body> 前用 <script src='{js_files[0]}'></script> 引用脚本\n"
        desc += "- 不要写 <style> 标签\n- 使用中文内容\n"
    elif ext == "css":
        desc += "- 只输出纯 CSS 代码，不要 HTML，不要 ```css 标记\n"
        desc += "- 包含基础 reset（box-sizing, margin:0）\n"
    elif ext == "js":
        desc += "- 只输出纯 JavaScript 代码，不要 HTML，不要 ```js 标记\n"
        desc += "- 使用 DOMContentLoaded 包裹\n- 用 const/let，不用 var\n"

    return desc


def run_e2e(task: str, output_name: str = "output"):
    orch = Orchestrator(API_URL, MODEL)
    for key, content in KNOWLEDGE.items():
        orch.load_knowledge(key, content)

    # 自动分解
    plan = orch.auto_plan(task, verbose=True)
    if not plan.subtasks:
        print("分解失败!")
        return

    # 增强子任务描述（规格展开 + 跨文件约束）
    print("\n规格展开...")
    for st in plan.subtasks:
        st.description = enhance_subtask_description(st, plan.subtasks, task)
        print(f"  {st.name}: 展开完成")

    # 执行
    outputs = orch.execute_plan(plan, verbose=True)

    # 保存文件
    output_dir = Path(__file__).parent / output_name
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print(f"生成文件:")
    print(f"{'='*60}")

    for subtask in plan.subtasks:
        if subtask.output:
            content = subtask.output
            if "```" in content:
                blocks = re.findall(r'```(?:\w+)?\n(.*?)```', content, re.DOTALL)
                if blocks:
                    content = blocks[0]
            (output_dir / subtask.name).write_text(content)
            print(f"  {subtask.name} ({len(content)} chars)")

    print(f"\n保存到: {output_dir}")


def main():
    tasks = [
        ("帮我创建一个待办事项 Web 应用，纯前端，用 localStorage 存储数据",
         "output_todo"),
    ]

    for task, out_name in tasks:
        print(f"\n{'#'*60}")
        print(f"# 用户: {task}")
        print(f"{'#'*60}")
        run_e2e(task, out_name)


if __name__ == "__main__":
    main()
