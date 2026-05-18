"""知识节点：文件系统迁移——跨卷/跨文件系统/应用配置/Docker/IDE工作区。

适用于涉及文件迁移、路径修复、卷改名、symlink代理的任务。
融合：filesystem-migration
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

MIGRATION_KNOWLEDGE = """你是文件系统迁移专家。根据以下知识评估迁移风险。

## 文件系统差异
- exFAT默认簇128KB-256KB，APFS用4KB块。大量小文件（git objects、node_modules）迁到APFS后实际占用显著缩小
- 跨文件系统mv不是原子操作（实际cp+rm），中途失败源和目标都有残留，大文件优先rsync
- exFAT不支持POSIX权限和ACL，移动含.git/objects的目录时可能部分失败

## 卷改名连锁反应
- diskutil rename会立即使所有引用旧路径的配置失效，改名前须扫描完整依赖图
- /Volumes/目录由系统管理，创建符号链接需sudo

## symlink代理迁移
- 将数据目录移到外置卷、原位放symlink可实现应用无感切换
- 某些应用本体嵌入在Application Support深处，移动后Gatekeeper会重新验证
- 使用路径哈希的应用（如某些IDE的workspaceStorage）对symlink无效——路径变哈希就变
- symlink所在卷根目录须放README防止误删断链

## Docker容器数据
- 无bind mount的容器数据在可写层，docker rm=数据永久丢失
- Docker.raw是稀疏文件，ls -lh显示的大小远大于du -sh实际占用
- bind mount路径写入时固化到内部数据库，修改compose须down+up重建

## IDE工作区迁移
- VS Code系workspaceStorage使用路径的自定义哈希作为目录名，无法预计算新哈希
- 迁移方法：用CLI打开新路径让IDE自动生成新哈希文件夹，再复制旧state.vscdb

## 应用配置路径存储方式
- JSON明文→sed/python替换
- Binary plist→plutil convert xml1→sed→convert binary1
- SQLite数据库→sqlite3 UPDATE
- 加密数据库→无法修改，只能导出可读部分
- Docker内部→docker inspect查看，重建容器更新

## 缓存清理
- 网络条件差时包管理器缓存是宝贵资源，清理前确认网络状况或移动而非删除
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        MIGRATION_KNOWLEDGE +
        "\n分析以下任务涉及的迁移风险，给出具体建议（每条一行，不超过5条）。"
        "如果不涉及文件迁移风险，回答'无迁移风险'。",
        f"任务：{task[:600]}",
        max_tokens=300
    ).strip()

    if "无迁移风险" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx

node = Node(id="440", name="文件迁移模式",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["迁移", "migration", "移动文件", "复制", "备份", "同步",
                          "symlink", "卷", "volume", "rename", "Docker", "plist"]},
    execute=execute, refs=["Y20"],
    metadata={"source": "knowledge/filesystem-migration", "category": "domain_system"})
