"""知识节点：模块化架构 — 数据代码分离 + 硬编码迁移。

融合：
- 数据和代码分离原则：数据量>20行或可扩展的数据必须分离到独立文件
- 硬编码到数据驱动迁移：路由/映射写死在代码里->迁移到配置/数据库
- 模块化拆分：大文件拆分为子模块
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def execute(ctx: dict) -> dict:
    """检查模块化：文件过长、数据硬编码、硬编码路由。"""
    js = ctx.get("js", "")
    if not js:
        return ctx

    lines = js.split("\n")
    suggestions = []

    # 文件过长检查
    if len(lines) > 150:
        ctx.setdefault("_warnings", []).append(
            f"JS代码{len(lines)}行，建议拆分为多文件模块"
        )
        suggestions.append({
            "type": "split_files",
            "reason": "单文件过长，可拆分为 data.js + render.js + events.js",
            "threshold": 150,
            "current": len(lines),
        })

    # 数据硬编码检查：大型数组/对象字面量
    large_literals = re.findall(
        r'(?:const|let|var)\s+\w+\s*=\s*[\[{]', js
    )
    if large_literals:
        for match in large_literals:
            # 找到对应的变量名
            var_name = re.search(r'(?:const|let|var)\s+(\w+)', match)
            if var_name:
                # 检查该变量后面的数据有多少行
                pattern = re.escape(match)
                pos = js.find(match)
                if pos >= 0:
                    chunk = js[pos:pos+2000]
                    chunk_lines = chunk.count('\n')
                    if chunk_lines > 20:
                        suggestions.append({
                            "type": "data_separation",
                            "reason": f"变量{var_name.group(1)}包含>20行数据，应分离到独立JSON/数据文件",
                            "variable": var_name.group(1),
                        })

    # 硬编码路由/映射检查
    hardcoded = re.findall(
        r'if\s*\(\s*\w+\s*===?\s*["\'][^"\']+["\']\s*\)\s*.*(?:url|host|endpoint|api|route)',
        js, re.IGNORECASE
    )
    if len(hardcoded) > 2:
        suggestions.append({
            "type": "hardcode_to_data",
            "reason": f"发现{len(hardcoded)}处硬编码路由/映射，建议迁移到配置文件",
        })

    if suggestions:
        ctx.setdefault("_suggestions", []).extend(suggestions)

    return ctx


node = Node(
    id="200",
    name="模块化检查",
    trigger={"type": "key_exists", "key": "js"},
    execute=execute,
    refs=["Y20"],
    metadata={"source": "Guild/数据代码分离+硬编码迁移", "category": "architecture"},
)
