"""知识节点：Git工作流与安全推送——隐私扫描/私有仓库/敏感信息防护。

融合：git推送私有仓库指南
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

GIT_RULES = [
    "先扫描再提交——提交后清理历史很麻烦(git filter-branch/BFG)",
    "git rm --cached不删本地文件——配合.gitignore使用",
    "文档中的示例URL容易遗漏——单独检查md文件中的私有域名/IP",
    "用sed替换文档中嵌入的私有URL为占位符(your-host.example.com)",
    "gh repo create --private --source=. --push一步创建并推送",
    "验证无残留：git ls-files | xargs grep -l -E '密码|密钥|私有URL'",
    "敏感文件模式：.env, credentials.json, *secret*, *token*, *key*",
]

def execute(ctx: dict) -> dict:
    ctx.setdefault("_domain_rules", []).extend(GIT_RULES)
    return ctx

node = Node(id="E01", name="Git安全工作流",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["git", "push", "推送", "仓库", "repo", "GitHub",
                          "private", "私有", ".gitignore", "敏感", "secret",
                          "credential", "token"]},
    execute=execute, refs=["Y20"],
    metadata={"source": "Guild/开发工具与工作流/git推送方式", "category": "domain_dev_tools"})
