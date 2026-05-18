"""知识节点：Tauri桌面应用诊断 — build配置/CSP/协议/feature问题。

适用场景：任务涉及桌面应用、Tauri、Rust+前端集成。
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


TAURI_RULES = {
    "vite_base": {
        "trigger": "vite",
        "check": "base配置必须为'./'，否则tauri://localhost/协议下绝对路径解析失败",
        "fix": "vite.config中设置 base: './'",
    },
    "custom_protocol": {
        "trigger": "cargo build",
        "check": "cargo build --release不等于tauri build，缺少完整codegen",
        "fix": "必须用tauri build CLI走完整流程",
    },
    "csp_nonce": {
        "trigger": "unsafe-inline",
        "check": "Tauri自动注入nonce后，unsafe-inline被浏览器忽略",
        "fix": "移除unsafe-inline，使用Tauri的nonce机制",
    },
    "command_reexport": {
        "trigger": "#[tauri::command]",
        "check": "crate root的pub fn和宏同名会触发E0255",
        "fix": "命令放入pub mod cmds子模块",
    },
}


def execute(ctx: dict) -> dict:
    """检查生成的代码是否涉及Tauri场景，注入诊断规则。"""
    task = ctx.get("task", "")
    html = ctx.get("html", "")
    js = ctx.get("js", "")

    tauri_signals = ["tauri", "桌面", "desktop", "native", "electron", "wry"]
    if not any(s in (task + html + js).lower() for s in tauri_signals):
        return ctx

    warnings = []

    # 检查HTML中是否有绝对路径资源引用
    abs_paths = re.findall(r'(?:src|href)=["\']/((?!/).+?)["\']', html)
    if abs_paths:
        warnings.append(f"HTML有绝对路径引用{abs_paths[:3]}——Tauri协议下会404，改为相对路径")

    # 检查是否缺少withGlobalTauri
    if "__TAURI__" in js and "withGlobalTauri" not in ctx.get("_config", ""):
        warnings.append("JS引用window.__TAURI__但可能未配置withGlobalTauri:true")

    if warnings:
        ctx.setdefault("_warnings", []).extend(warnings)

    return ctx


node = Node(
    id="170",
    name="Tauri诊断",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["tauri", "桌面", "desktop", "native"]},
    execute=execute,
    refs=["171"],
    metadata={"source": "Tauri桌面应用工程师", "category": "platform"},
)
