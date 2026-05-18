"""知识节点：macOS问题修复手册——磁盘修复/卷显示/数据迁移/容器保全/元数据清理/权限修复。

覆盖7类常见macOS问题的诊断和修复流程。
核心原则：先诊断再修复，先备份再操作，先理解原理再执行命令。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

PROBLEM_CATEGORIES = {
    "exFAT磁盘不可挂载": {
        "symptoms": ["磁盘未安全弹出后无法挂载", "磁盘工具卡死"],
        "cause": "磁盘被标记脏标志(dirty bit)",
        "fix": "先拔盘→记录已挂载盘→插入→ioreg确认硬件→找disk编号→确认exFAT→sudo fsck_exfat -d /dev/diskXs1→mount",
    },
    "Finder不显示APFS卷": {
        "symptoms": ["ls /Volumes可见但Finder不显示", "终端改过卷名"],
        "cause": "隐藏标志/扩展属性/Finder偏好设置",
        "fix": "chflags nohidden→xattr -d com.apple.provenance→defaults write ShowExternalHardDrivesOnDesktop true→killall Finder",
    },
    "Docker容器数据风险": {
        "symptoms": ["迁移磁盘担心容器数据丢失"],
        "cause": "无bind mount的容器数据封在Docker.raw内",
        "fix": "docker inspect检查Binds→null表示高危→docker cp导出→有bind mount但路径失效→修改compose后重建",
    },
    "应用数据迁移(空间不足)": {
        "symptoms": ["内置盘空间不足", "需要移动应用数据到外置盘"],
        "cause": "应用硬编码了数据路径",
        "fix": "确认应用未运行→cp -a到目标→验证文件数和大小→rm原件→ln -s建链接→验证链接→创建保护性说明",
    },
    "多盘数据迁移引用修复": {
        "symptoms": ["数据分散多个磁盘", "移动后应用找不到文件"],
        "cause": "移动文件后各种配置中的路径引用未更新",
        "fix": "盘点→扫描引用依赖(json/plist/sqlite/docker/shell)→备份→移动→按格式更新引用→验证无残留",
    },
    "macOS元数据垃圾文件": {
        "symptoms": ["大量._前缀文件", "zip解压后多出文件"],
        "cause": "macOS自动生成Apple Double格式元数据",
        "fix": "find统计→抽样确认→find -delete清理→验证→可选defaults write禁止外置盘生成",
    },
    "应用存档权限错误": {
        "symptoms": ["快速存档崩溃PermissionError", "普通存档正常但快存不行"],
        "cause": "存档目录在.app包内，macOS限制unlink操作",
        "fix": "找save_directory名→复制存档到用户目录→删除.app内saves目录→清理编译缓存",
    },
}

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    # 让模型判断问题类别（一件简单事）
    categories = list(PROBLEM_CATEGORIES.keys())
    cat_str = " / ".join(categories)
    matched = ask(
        f"用户遇到的问题最可能属于哪个类别？从选项中选一个，只回答类别名。\n"
        f"选项：{cat_str}\n如果都不匹配回答'未知'。",
        f"用户说：{task}",
        max_tokens=30
    ).strip()

    guide = {"detected_category": matched}

    for cat_name, cat_info in PROBLEM_CATEGORIES.items():
        if cat_name in matched:
            guide["cause"] = cat_info["cause"]
            guide["fix_steps"] = cat_info["fix"]
            break

    if "cause" not in guide:
        guide["all_categories"] = {k: v["symptoms"][0] for k, v in PROBLEM_CATEGORIES.items()}

    guide["principle"] = "先诊断再修复，先备份再操作"
    ctx["_troubleshoot"] = guide
    return ctx

node = Node(id="750", name="macOS问题修复",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["磁盘", "disk", "挂载", "mount", "Finder", "Docker",
                          "迁移", "symlink", "权限", "permission", "._文件",
                          "元数据", "exFAT", "APFS", "空间不足"]},
    execute=execute, refs=["440"],
    metadata={"source": "Skills/电脑问题修复", "category": "ops"})
