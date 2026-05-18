"""
干净的端到端测试。

原则：
  - 程序能做的不让模型做（验证、修复、格式化）
  - 模型只做程序做不了的（生成代码内容、理解语义）
  - 每次隔离执行，不共享上下文
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orchestrator import Orchestrator, SubTask, TaskPlan
from validator import validate_file

API_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-2b"

KNOWLEDGE = {
    "html": "HTML: 语义标签(header/nav/main/article/section/footer), UTF-8, 外部CSS用link, 外部JS用script",
    "css": "CSS: box-sizing:border-box全局, max-width居中, sticky导航, 圆角卡片, 间距8-14px, grid等分",
    "js": "JS: const/let不用var, DOMContentLoaded, localStorage, JSON.parse/stringify, addEventListener",
    "响应式": "响应式: max-width:800px, margin:0 auto, @media(max-width:768px), 图片max-width:100%",
}


def spec_expand(task_goal: str, filename: str, file_desc: str) -> str:
    """规格展开（隔离微对话）：细化文件具体内容。"""
    import requests
    resp = requests.post(API_URL, json={
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "列出文件需要的具体元素。每行一个，简短。不要解释。"},
            {"role": "user", "content": (
                f"项目：{task_goal}\n"
                f"文件 {filename} 用途：{file_desc}\n"
                "需要包含哪些具体元素？"
            )},
        ],
        "temperature": 0.0,
        "max_tokens": 200,
    }, timeout=60)
    return resp.json()["choices"][0]["message"]["content"]


def build_prompt(subtask: SubTask, all_files: list[str],
                 task_goal: str, knowledge: str, spec: str) -> str:
    """构建子任务的完整 prompt（系统层构建，确定性约束）。"""
    ext = subtask.name.split(".")[-1]
    css_files = [f for f in all_files if f.endswith(".css")]
    js_files = [f for f in all_files if f.endswith(".js")]

    parts = [f"创建 {subtask.name}。\n"]
    parts.append(f"项目目标：{task_goal}\n")
    parts.append(f"具体内容：\n{spec}\n")

    if knowledge:
        parts.append(f"规范参考：\n{knowledge}\n")

    parts.append("技术要求：\n")
    if ext == "html":
        if css_files:
            parts.append(f"- head 中：<link rel=\"stylesheet\" href=\"{css_files[0]}\">\n")
        if js_files:
            parts.append(f"- body 末尾：<script src=\"{js_files[0]}\"></script>\n")
        parts.append("- 不写 <style> 标签，不写内联样式\n")
        parts.append("- 使用中文内容\n")
        parts.append("- 必须有完整的 html>head+body 结构\n")
    elif ext == "css":
        parts.append("- 只输出纯 CSS，不要 HTML，不要 ``` 标记\n")
    elif ext == "js":
        parts.append("- 只输出纯 JS，不要 HTML，不要 ``` 标记\n")
        parts.append("- 用 DOMContentLoaded 包裹\n")

    return "".join(parts)


def run(task: str, output_name: str = "output"):
    orch = Orchestrator(API_URL, MODEL)
    for k, v in KNOWLEDGE.items():
        orch.load_knowledge(k, v)

    # Step 1: 自动分解
    plan = orch.auto_plan(task, verbose=True)
    if not plan.subtasks:
        print("分解失败!")
        return

    all_files = [st.name for st in plan.subtasks]

    # Step 2: 规格展开 + 构建 prompt + 执行（每个文件隔离）
    print("\n执行:")
    results = {}
    for st in plan.subtasks:
        # 依赖检查（id 匹配文件名前缀）
        result_ids = {f.split(".")[0]: f for f in results}
        deps_ok = all(d in result_ids for d in st.depends_on)
        if not deps_ok:
            print(f"  ✗ {st.name}: 依赖未满足 {st.depends_on} vs {list(result_ids.keys())}")
            continue

        # 规格展开（隔离微对话）
        spec = spec_expand(task, st.name, st.description)

        # 知识路由
        knowledge = orch.router.route(st.knowledge_keys)

        # 构建 prompt（系统层确定性构建）
        st.description = build_prompt(st, all_files, task, knowledge, spec)

        # 隔离执行
        # 预处理依赖（确定性提取，不传原始代码给模型）
        prev = {}
        ext = st.name.split(".")[-1]
        for d in st.depends_on:
            if d not in result_ids:
                continue
            dep_content = results[result_ids[d]]
            dep_file = result_ids[d]
            if ext == "js" and dep_file.endswith(".html"):
                # JS 文件只需要知道 HTML 中有哪些 ID 和 class
                ids = re.findall(r'id=["\']([^"\']+)["\']', dep_content)
                classes = re.findall(r'class=["\']([^"\']+)["\']', dep_content)
                prev[d] = f"HTML中的元素：\nIDs: {ids}\nClasses: {classes}"
            elif ext == "css" and dep_file.endswith(".html"):
                # CSS 只需知道 HTML 中使用的标签和 class
                tags = set(re.findall(r'<(\w+)', dep_content))
                classes = re.findall(r'class=["\']([^"\']+)["\']', dep_content)
                prev[d] = f"HTML使用的标签：{sorted(tags)}\nClasses: {classes}"
            else:
                prev[d] = dep_content[:500]
        output = orch.executor.execute(st, prev_outputs=prev)

        # 提取代码（去掉 markdown 包裹）
        if "```" in output:
            blocks = re.findall(r'```(?:\w+)?\n(.*?)```', output, re.DOTALL)
            if blocks:
                output = blocks[0]

        # Step 3: 确定性验证修复（程序做，不问模型）
        fixed, issues = validate_file(st.name, output, dict(zip(all_files, [""] * len(all_files))))
        if issues:
            print(f"  → {st.name}: 生成完成，修复 {len(issues)} 个问题")
            for iss in issues:
                print(f"      [{iss.severity}] {iss.message} → {iss.fix}")
        else:
            print(f"  → {st.name}: 生成完成，无问题")

        results[st.name] = fixed

    # Step 4: 保存
    output_dir = Path(__file__).parent / output_name
    output_dir.mkdir(exist_ok=True)
    print(f"\n文件:")
    for name, content in results.items():
        (output_dir / name).write_text(content)
        print(f"  {name} ({len(content)} chars, {content.count(chr(10))+1} lines)")

    print(f"\n保存到: {output_dir}")
    return results


def main():
    print("=" * 60)
    print("测试 1: 待办事项应用")
    print("=" * 60)
    run("创建一个待办事项 Web 应用，纯前端，用 localStorage 存储", "output_todo_v2")

    print("\n\n")
    print("=" * 60)
    print("测试 2: 个人博客")
    print("=" * 60)
    run("创建一个简洁的个人博客，包含首页（文章列表）和关于页面", "output_blog_v2")


if __name__ == "__main__":
    main()
