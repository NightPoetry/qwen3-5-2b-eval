"""知识节点：资料管理系统 — 文件夹规则+三层文档+发行版。

文件夹核心规则：
  1. 每个文件夹必须有README（用途/使用规则/命名规范）
  2. 进入文件夹先读README获取规则
  3. 无README时推断风格（观察命名后缀/内容格式/三层结构）

三层文档结构：
  - 原文记录.md（原始证据，永不修改）
  - 整理文档.md（结构化整理，可更新有版本号）
  - 变更日志.md（留痕记录，每次变更）

Guild发行版规则：
  - 敏感信息用占位符：<手机号> <API_KEY> <地址> <密码>
  - 精简操作步骤，凝练操作思想
  - 另一个AI可理解和复刻

知识三层抽象：
  经验(具体案例) -> 知识(共性/不变条件) -> 理解(推理规则/最少假设)
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

FILE_MGMT_SYSTEM = """You are a file management advisor. Apply these rules:

FOLDER RULES:
1. Every folder MUST have README.md (purpose, usage rules, naming conventions)
2. Upon entering a folder: read README first to get rules
3. No README: infer style from existing files (naming suffixes, content format, three-layer structure)

THREE-LAYER DOCUMENT STRUCTURE:
- Original record (suffix: ——原文记录.md): user's exact words, timestamped, NEVER modified
- Organized document (suffix: ——整理文档.md): structured, updatable, version numbered (+0.1 each update)
- Change log (suffix: ——变更日志.md): audit trail, every change recorded with timestamp

CORRECTION FLOW:
1. Original record: ADD new record (marked as correction), never modify existing
2. Organized doc: update content based on correction, add change note, increment version
3. Change log: add entry referencing before/after originals, note impact scope

RELEASE VERSION RULES (发行版):
- Sensitive info replaced with placeholders: <phone> <API_KEY> <address> <password>
- Streamlined operation steps, distilled principles
- Another AI can understand and replicate from the release version alone

KNOWLEDGE THREE-LAYER ABSTRACTION:
- Experience: specific cases with preconditions, preserved objectively
- Knowledge: commonalities, invariant conditions and invariant results
- Understanding: inference rules, minimum assumptions to maximum deductions

DIRECTORY STRUCTURE:
- Role/: role definitions (knowledge/ + experience/ + understanding/ per role)
- Guild/: specific knowledge guides (topic folders with three-layer docs + release versions)
- DesignAndThinking/: design and thought documents

Given the file management question, recommend appropriate structure and naming."""


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    advice = ask(
        FILE_MGMT_SYSTEM,
        f"File management scenario: {task[:300]}",
        max_tokens=150
    ).strip()
    ctx["_file_mgmt_advice"] = advice
    return ctx

node = Node(id="E33", name="资料管理规范",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["文件夹", "目录", "命名", "归档", "整理", "README",
                          "folder", "directory", "organize", "naming"]},
    execute=execute, refs=["995"],
    metadata={"source": "Guild/文件夹规则+三层文档+知识抽象", "category": "methodology"})
