"""知识节点：不可逆信息丢失保险——脏标+智能保存+退出拦截三件套。

凡是会导致用户已投入劳动凭空消失的操作，都必须经过显式确认。
三件套缺一不可：
  1. 脏标(dirty flag)：任何进undo历史的操作→markDirty（在pushH末尾自动追加）
  2. 智能保存：首次弹路径选择，之后静默直存（Cmd+S / Cmd+Shift+S另存为）
  3. 退出拦截：关窗/加载/新建 三个触发口全hook
易错点：pushH链路中dirty死循环（加载后先pushH再markClean）、保存失败不能markClean、
  加载新文件也要拦截（不只是关闭）。
"""
import re
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

DIRTY_FLAG_TEMPLATE = """
// 脏标系统
let _dirty = false;
function markDirty() { _dirty = true; updateDirtyUI(); }
function markClean() { _dirty = false; updateDirtyUI(); }
function updateDirtyUI() {
  document.title = document.title.replace(/ •$/, '') + (_dirty ? ' •' : '');
}
window.addEventListener('beforeunload', e => {
  if (_dirty) { e.preventDefault(); e.returnValue = ''; }
});
"""

EASY_ERRORS = [
    "pushH链路死循环：加载→pushH→markDirty→但加载完应是clean——正确顺序：pushH→记路径→markClean（在pushH之后）",
    "保存失败仍markClean：用户以为存了，关窗就没了——保存失败必须保持脏态",
    "只hook关闭忘了加载：加载另一个项目=丢弃当前未保存内容——加载/新建都要拦截",
    "危险按钮是默认焦点：按Enter就丢失——Enter应该是取消",
]

DIRTY_UI_SPEC = [
    "可视化脏标必须在用户视线主轴上（如statusbar左侧圆点+文字）",
    "灰色=空项目，绿色=已是最新，橙色脉动=未保存改动（1.4s呼吸）",
    "窗口标题加'•'标记，切到别的窗口扫一眼标题栏也能知道",
]

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    if not any(kw in task for kw in ["编辑器", "保存", "编辑", "笔记", "文档",
                                      "undo", "撤销", "脏标", "dirty"]):
        return ctx

    ctx.setdefault("_inject_js", []).append(DIRTY_FLAG_TEMPLATE)
    ctx.setdefault("_design_principles", []).extend([
        "脏标：pushHistory()末尾追加markDirty()，覆盖所有路径",
        "保存成功→markClean；保存失败→保持脏态",
        "三个触发口全hook：关闭按钮、加载另一个项目、新建项目",
        "危险按钮文字必须写'丢失'或'放弃'，不要写'OK'/'继续'",
        "危险按钮永远不能是默认焦点——Enter应该是取消",
        "确认框文案：取消按钮放左、危险按钮放右并加红色",
    ])
    ctx.setdefault("_easy_errors", []).extend(EASY_ERRORS)
    ctx.setdefault("_dirty_ui_spec", []).extend(DIRTY_UI_SPEC)
    return ctx

node = Node(id="560", name="不可逆保险",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["编辑器", "保存", "编辑", "笔记", "文档", "撤销", "undo"]},
    execute=execute, refs=["330"],
    metadata={"source": "Skills/不可逆信息丢失保险", "category": "safety"})
