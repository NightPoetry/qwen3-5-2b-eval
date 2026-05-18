"""入口：意图解析 + 主题配置。"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

THEMES = {
    "light": {
        "bg": "#f8fafc", "bg2": "#ffffff", "border": "#e2e8f0",
        "text": "#0f172a", "text2": "#334155", "text3": "#64748b", "text4": "#94a3b8",
        "accent": "#2563eb", "accent_bg": "#dbeafe", "purple": "#7c3aed",
        "nav_bg": "rgba(255,255,255,0.85)",
        "shadow": "0 4px 14px -3px rgba(37,99,235,0.2)",
    },
    "dark": {
        "bg": "#0d1117", "bg2": "#161b22", "border": "#21262d",
        "text": "#f0f6fc", "text2": "#c9d1d9", "text3": "#8b949e", "text4": "#484f58",
        "accent": "#388bfd", "accent_bg": "rgba(56,139,253,0.15)", "purple": "#a855f7",
        "nav_bg": "rgba(13,17,23,0.85)",
        "shadow": "0 4px 14px -3px rgba(56,139,253,0.25)",
    },
}

SAVED_DIR = Path(__file__).parent / "saved_presets"


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    # 判断模式
    existing = ctx.get("existing_html")
    ctx["_mode"] = "modify" if existing else "create"

    # 主题
    if any(kw in task for kw in ["暗色", "dark", "深色"]):
        ctx["theme"] = "dark"
    elif any(kw in task for kw in ["亮色", "light", "白色"]):
        ctx["theme"] = "light"
    ctx.setdefault("theme", "light")
    ctx["v"] = THEMES[ctx["theme"]]

    # 检查是否引用了已保存的预设
    if SAVED_DIR.exists():
        for preset_file in SAVED_DIR.glob("*.json"):
            preset_name = preset_file.stem
            if preset_name in task:
                preset = json.loads(preset_file.read_text())
                ctx["_preset"] = preset
                ctx["_preset_name"] = preset_name
                # 预设中的主题变量覆盖默认
                if "theme_vars" in preset:
                    ctx["v"] = preset["theme_vars"]
                break

    # 初始化碎片收集器
    ctx.setdefault("html_fragments", {})
    ctx.setdefault("css_fragments", {})

    return ctx

node = Node(
    id="000", name="意图解析",
    trigger={"type": "entry"},
    execute=execute,
    refs=["010_c", "100_h", "200_s", "400_m", "500_p"],
)
