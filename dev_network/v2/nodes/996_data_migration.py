"""知识节点：数据迁移方法论 — 无损迁移+引用扫描+symlink代理。

融合：多盘数据整理与无损迁移 + 文件夹使用规则 + 终端Finder同步。

无损迁移流程：
  盘点现状->扫描引用依赖->备份->移动->更新引用->验证

关键步骤：引用扫描（最关键！）
  - JSON/文本配置：grep -rl "旧路径"
  - macOS plist(二进制)：plutil -convert xml1
  - SQLite：SELECT WHERE value LIKE '%旧路径%'
  - Docker容器：docker inspect
  - 卷改名后所有引用立即失效，必须预扫描

symlink代理迁移：
  1.确认应用未运行 2.移动数据 3.创建符号链接 4.验证

终端/Finder同步：
  - 卷操作用diskutil（会通知Finder），不直接umount
  - 文件属性修改后可能需killall Finder
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

MIGRATION_SYSTEM = """You are a data migration advisor. Apply these principles:

LOSSLESS MIGRATION FLOW:
Inventory -> Scan reference dependencies -> Backup -> Move -> Update references -> Verify

REFERENCE SCANNING (MOST CRITICAL STEP):
Before moving ANY file, scan ALL configurations referencing that path:
- JSON/text configs: grep -rl "old_path" ~/Library/Application\\ Support/ ~/.config/
- macOS binary plist: plutil -convert xml1 then grep
- SQLite databases: SELECT key,value FROM table WHERE value LIKE '%old_path%'
- Docker containers: docker inspect --format '{{json .HostConfig.Binds}}'
- IDE workspace: uses path hash mapping, path change = old storage disconnected

SYMLINK PROXY MIGRATION:
1. Confirm application not running (pgrep -x "AppName")
2. Move data to target location (mv old new)
3. Create symbolic link (ln -s new old)
4. Verify (ls -la should show -> new_path)
- /opt/ and system dirs need sudo
- Some apps trigger Gatekeeper re-verification after move

REFERENCE UPDATE METHODS:
- JSON plaintext: sed or Python replace
- Binary plist: plutil xml1 -> sed -> plutil binary1
- SQLite: UPDATE SET value=REPLACE(value,'old','new')
- Docker compose: modify .env then docker-compose down && up
- Encrypted DB: cannot modify, export readable part as archive

VOLUME RENAME: diskutil rename immediately invalidates all /Volumes/oldname/ paths.
Must complete reference scan before rename, batch update after.

CROSS-DISK TRANSFER:
- exFAT -> APFS mv is actually cp + rm, NOT atomic
- Large files: rsync -av, verify, then manually delete source
- exFAT permission issues on rm are normal

TERMINAL/FINDER SYNC:
- Volume operations: use diskutil (notifies Finder), not raw umount
- File attribute changes: may need killall Finder to refresh
- defaults write: needs killall Finder to take effect

Given the migration scenario, identify risks and recommend the safe migration path."""


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    advice = ask(
        MIGRATION_SYSTEM,
        f"Migration scenario: {task[:300]}",
        max_tokens=150
    ).strip()
    ctx["_migration_advice"] = advice
    return ctx

node = Node(id="996", name="数据迁移方法论",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["迁移", "移动", "搬", "备份", "引用", "路径", "symlink",
                          "migrate", "move", "backup", "volume", "卷"]},
    execute=execute, refs=["620"],
    metadata={"source": "Guild/无损迁移+文件夹规则+终端Finder同步", "category": "architecture"})
