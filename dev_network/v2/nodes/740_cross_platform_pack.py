"""知识节点：跨平台打包方法——将仅有单平台版本的应用打包到另一平台。

核心原理：应用的内容层（脚本+资源）跟平台无关，差异只在运行时外壳。
转换思路：下载目标平台SDK/运行时，把内容文件夹塞进去。
以脚本引擎游戏（如视觉小说引擎）为典型场景。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

PACK_STEPS = [
    "1. 确认应用的引擎版本（SDK版本必须>=应用版本）",
    "2. 下载对应版本的SDK（包含目标平台运行时）",
    "3. 提取应用内容文件夹（脚本+资源，跨平台通用部分）",
    "4. 组装目标平台包结构（创建骨架→复制SDK→复制内容→创建启动脚本）",
    "5. 解除目标平台安全限制（macOS: xattr -cr; Windows: 解除阻止）",
    "6. 测试运行并排查启动问题",
]

MACOS_APP_STRUCTURE = [
    "*.app/Contents/Info.plist — 应用元信息",
    "*.app/Contents/MacOS/启动脚本 — bash启动入口",
    "*.app/Contents/Resources/game/ — 内容文件",
    "*.app/Contents/Resources/sdk/ — 引擎运行时",
]

COMMON_ISSUES = [
    "无法打开(macOS安全限制)→xattr -cr *.app",
    "脚本Permission denied→chmod +x启动脚本和运行时",
    "黑屏/闪退→SDK版本不匹配，确认版本>=应用版本",
    "找不到内容目录→检查启动脚本中的路径拼接",
    "存档写入PermissionError→存档目录不要放在.app包内，迁移到用户目录",
]

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    # 让模型判断源平台和目标平台（一件简单事）
    platforms = ask(
        "这个任务是从哪个平台转换到哪个平台？格式：源→目标。"
        "如果不确定回答'未知'。",
        f"任务：{task}",
        max_tokens=20
    ).strip()

    ctx["_pack_guide"] = {
        "platforms": platforms,
        "steps": PACK_STEPS,
        "macos_structure": MACOS_APP_STRUCTURE,
        "common_issues": COMMON_ISSUES,
        "principle": "内容层跟平台无关，差异只在运行时外壳",
    }
    return ctx

node = Node(id="740", name="跨平台打包",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["打包", "移植", "转换", ".app", "Win转Mac", "Mac转Win",
                          "跨平台", "cross-platform"]},
    execute=execute, refs=["730"],
    metadata={"source": "Skills/跨平台打包", "category": "engineering"})
