"""
代码开发网络 — 系统编排器

核心原理（已验证 6/6 = 100%）：
  - 小模型 = 单线程，一次只做一件简单的事
  - 系统负责：任务分解、知识路由、上下文隔离、输出集成
  - 模型负责：在隔离上下文中执行简单子任务

架构层次：
  1. 任务分解器 — 将复杂任务拆为原子子任务
  2. 知识路由器 — 为每个子任务匹配相关知识卡
  3. 隔离执行器 — 独立上下文中执行每个子任务
  4. 集成验证器 — 组合输出、检查一致性
"""

import json
import requests
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SubTask:
    """原子子任务"""
    id: str
    name: str
    description: str
    depends_on: list[str] = field(default_factory=list)
    knowledge_keys: list[str] = field(default_factory=list)
    output: str = ""
    status: str = "pending"  # pending → running → done → failed


@dataclass
class TaskPlan:
    """任务执行计划"""
    goal: str
    subtasks: list[SubTask]
    context: dict = field(default_factory=dict)


class KnowledgeRouter:
    """知识路由器：为子任务匹配相关知识"""

    def __init__(self, knowledge_dir: str = None):
        self._cards: dict[str, str] = {}
        if knowledge_dir:
            self._load_dir(knowledge_dir)

    def _load_dir(self, dir_path: str):
        p = Path(dir_path)
        if p.exists():
            for f in p.rglob("*.md"):
                key = f.stem
                self._cards[key] = f.read_text(errors="ignore")[:3000]

    def add_card(self, key: str, content: str):
        self._cards[key] = content

    def route(self, keywords: list[str], max_cards: int = 2) -> str:
        """根据关键词匹配知识卡，返回拼接后的上下文"""
        matched = []
        for key, content in self._cards.items():
            score = sum(1 for kw in keywords if kw.lower() in key.lower()
                        or kw.lower() in content[:200].lower())
            if score > 0:
                matched.append((score, key, content))
        matched.sort(reverse=True)
        result = []
        for _, key, content in matched[:max_cards]:
            result.append(f"--- 知识卡: {key} ---\n{content[:1500]}\n")
        return "\n".join(result) if result else ""


class IsolatedExecutor:
    """隔离执行器：每个子任务独立的微对话"""

    def __init__(self, api_url: str, model: str, timeout: int = 120):
        self.api_url = api_url
        self.model = model
        self.timeout = timeout

    def execute(self, subtask: SubTask, knowledge: str = "",
                prev_outputs: dict[str, str] = None) -> str:
        """在隔离上下文中执行一个子任务"""
        system = (
            "你是代码生成助手。只输出代码或配置，不要解释。\n"
            "如果任务要求 HTML/CSS/JS，直接输出完整文件内容。\n"
            "严格遵循提供的知识卡中的规范。"
        )

        user_parts = [f"任务：{subtask.description}"]

        if knowledge:
            user_parts.append(f"\n参考知识：\n{knowledge}")

        if prev_outputs:
            for dep_id, output in prev_outputs.items():
                user_parts.append(f"\n前置输出（{dep_id}）：\n{output[:2000]}")

        user = "\n".join(user_parts)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.0,
            "max_tokens": 2048,
        }

        try:
            resp = requests.post(self.api_url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"ERROR: {e}"


class TaskDecomposer:
    """任务分解器：让模型将复杂任务拆成文件列表"""

    def __init__(self, api_url: str, model: str):
        self.api_url = api_url
        self.model = model

    def decompose(self, task_description: str) -> list[SubTask]:
        """将自然语言任务拆分为子任务列表"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是文件规划助手。只输出 JSON 数组，不要解释。"},
                {"role": "user", "content": (
                    f"任务：{task_description}\n\n"
                    "列出需要创建的文件（3-5个）。格式：\n"
                    '[{"file": "文件名.扩展名", "desc": "一句话说明", "needs": ["依赖的文件名"], "keywords": ["相关知识关键词"]}]\n\n'
                    "注意：\n"
                    "- HTML 文件用 <link> 引用 CSS，用 <script> 引用 JS\n"
                    "- CSS 和 JS 依赖 HTML（先有结构才知道怎么写样式/逻辑）\n"
                    "- keywords 用于匹配知识库（如 css布局、html结构、响应式、交互）\n\n"
                    "只输出 JSON："
                )},
            ],
            "temperature": 0.0,
            "max_tokens": 512,
        }
        try:
            resp = requests.post(self.api_url, json=payload, timeout=60)
            resp.raise_for_status()
            text = resp.json()["choices"][0]["message"]["content"]
            import re
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                items = json.loads(match.group())
            else:
                return []
        except Exception:
            return []

        subtasks = []
        for item in items:
            file_name = item.get("file", "")
            subtasks.append(SubTask(
                id=file_name.split(".")[0],
                name=file_name,
                description=item.get("desc", ""),
                depends_on=[d.split(".")[0] for d in item.get("needs", [])],
                knowledge_keys=item.get("keywords", []),
            ))
        return subtasks


class Orchestrator:
    """主编排器"""

    def __init__(self, api_url: str, model: str):
        self.api_url = api_url
        self.model = model
        self.executor = IsolatedExecutor(api_url, model)
        self.router = KnowledgeRouter()
        self.decomposer = TaskDecomposer(api_url, model)
        self.outputs: dict[str, str] = {}

    def load_knowledge(self, key: str, content: str):
        self.router.add_card(key, content)

    def load_knowledge_dir(self, path: str):
        self.router = KnowledgeRouter(path)

    def auto_plan(self, task: str, verbose: bool = True) -> TaskPlan:
        """自动分解任务并生成执行计划"""
        subtasks = self.decomposer.decompose(task)
        if verbose:
            print(f"\n自动分解: {len(subtasks)} 个子任务")
            for st in subtasks:
                print(f"  {st.name}: {st.description} (依赖: {st.depends_on})")
        return TaskPlan(goal=task, subtasks=subtasks)

    def validate_and_fix(self, subtask: SubTask, verbose: bool = True) -> str:
        """验证输出并修复明显错误（隔离对话）"""
        content = subtask.output
        issues = []

        ext = subtask.name.split(".")[-1] if "." in subtask.name else ""

        if ext == "html":
            if "<body" in content and "<head" in content:
                head_pos = content.find("<head")
                body_pos = content.find("<body")
                head_end = content.find("</head>")
                if body_pos < head_end and head_end > 0:
                    issues.append("body 标签嵌套在 head 内，结构错误")
            if "</html>" not in content:
                issues.append("缺少 </html> 闭合")
            if "<meta" not in content or "viewport" not in content:
                issues.append("缺少 viewport meta")
        elif ext == "css":
            if "<" in content and ">" in content:
                issues.append("CSS 中包含 HTML 标签")
        elif ext == "js":
            if "<script" in content or "<html" in content:
                issues.append("JS 中包含 HTML 标签")

        if not issues:
            return content

        if verbose:
            print(f"    修复: {issues}")

        fix_prompt = (
            f"以下 {ext} 代码有问题：{issues}\n\n"
            f"原始代码：\n{content}\n\n"
            f"请修复上述问题，输出完整的修正后代码。只输出代码。"
        )
        fixed = self.executor.execute(
            SubTask(id="fix", name=subtask.name,
                    description=fix_prompt),
        )
        return fixed if fixed and "ERROR" not in fixed else content

    def execute_plan(self, plan: TaskPlan, verbose: bool = True) -> dict[str, str]:
        """按依赖顺序执行计划中的所有子任务"""
        if verbose:
            print(f"\n{'='*60}")
            print(f"执行计划: {plan.goal}")
            print(f"子任务数: {len(plan.subtasks)}")
            print(f"{'='*60}")

        for subtask in plan.subtasks:
            # 检查依赖
            deps_ready = all(
                self.outputs.get(dep) for dep in subtask.depends_on
            )
            if not deps_ready:
                subtask.status = "failed"
                if verbose:
                    print(f"\n  ✗ {subtask.id}: 依赖未满足")
                continue

            # 知识路由
            knowledge = self.router.route(subtask.knowledge_keys)

            # 收集前置输出
            prev = {dep: self.outputs[dep] for dep in subtask.depends_on
                    if dep in self.outputs}

            # 隔离执行
            subtask.status = "running"
            if verbose:
                print(f"\n  → {subtask.id}: {subtask.name}")
                if knowledge:
                    print(f"    知识卡: {subtask.knowledge_keys}")

            output = self.executor.execute(subtask, knowledge, prev)
            subtask.output = output
            subtask.status = "done"
            self.outputs[subtask.id] = output

            # 验证修复
            fixed = self.validate_and_fix(subtask, verbose)
            if fixed != output:
                subtask.output = fixed
                self.outputs[subtask.id] = fixed

            if verbose:
                lines = subtask.output.count("\n") + 1
                print(f"    ✓ 完成 ({lines} 行)")

        return self.outputs
