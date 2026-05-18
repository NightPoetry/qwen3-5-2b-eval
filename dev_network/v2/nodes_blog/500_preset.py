"""
自举节点 — 模板集活起来的核心。

用户说"保存这个布局叫xxx"时：
  1. 系统把当前html_fragments和css_fragments快照为JSON
  2. 写入saved_presets/xxx.json
  3. 下次用户说"用xxx布局"时，000_intent检测到预设名，
     加载预设碎片覆盖默认碎片

这样用户自定的模板就变成了一个"虚拟节点"：
  - 它的触发条件 = 用户提到这个名字
  - 它的执行 = 用预设碎片覆盖默认碎片
  - 它自然地参与网络路由

不需要2B参与。全是确定性操作。模板集自举。
"""
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

SAVED_DIR = Path(__file__).parent / "saved_presets"


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    # 检测保存意图
    save_match = re.search(r'(?:叫做?|命名为|存为)\s*[「"\'【]?(.+?)[」"\'】]?\s*$', task)
    if not save_match:
        save_match = re.search(r'(?:保存|存为).*?[叫为]\s*(\S+)', task)

    if not save_match:
        return ctx

    preset_name = save_match.group(1).strip()

    # 收集当前状态
    # 如果刚新建完，碎片在context中
    # 如果刚修改完，完整HTML在context中
    preset_data = {"name": preset_name}

    if ctx.get("html_fragments"):
        preset_data["html_fragments"] = ctx["html_fragments"]
    if ctx.get("css_fragments"):
        preset_data["css_fragments"] = ctx["css_fragments"]
    if ctx.get("theme"):
        preset_data["theme"] = ctx["theme"]
    if ctx.get("v"):
        preset_data["theme_vars"] = ctx["v"]
    if ctx.get("html"):
        preset_data["full_html"] = ctx["html"]

    # 保存
    SAVED_DIR.mkdir(exist_ok=True)
    preset_path = SAVED_DIR / f"{preset_name}.json"
    preset_path.write_text(json.dumps(preset_data, ensure_ascii=False, indent=2))

    ctx.setdefault("_changes", []).append(f"已保存预设「{preset_name}」→ {preset_path.name}")

    # 列出所有已保存预设
    presets = [f.stem for f in SAVED_DIR.glob("*.json")]
    ctx["_saved_presets"] = presets

    return ctx


node = Node(
    id="500_p", name="预设保存(自举)",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["保存", "存为", "命名为", "叫做"]},
    execute=execute, refs=["900_o"],
)
