"""知识节点：WebAudio音效系统 — 操作反馈音效合成。

适用场景：交互中需要音效反馈（编辑器、工具类应用）。
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


WEBAUDIO_TEMPLATE = """
// WebAudio音效系统（合成，0字节，即调即出）
const SFX = (() => {
  let ctx = null;
  function getCtx() {
    if (!ctx) ctx = new AudioContext();
    return ctx;
  }

  function _p(freq, dur, type='sine') {
    const c = getCtx();
    const o = c.createOscillator();
    const g = c.createGain();
    o.type = type;
    o.frequency.value = freq;
    g.gain.value = 0.3;
    g.gain.exponentialRampToValueAtTime(0.001, c.currentTime + dur);
    o.connect(g).connect(c.destination);
    o.start(); o.stop(c.currentTime + dur);
  }

  return {
    tap: () => _p(800, 0.05),           // 点击确认
    add: () => _p(600, 0.08, 'sine'),   // 创建/添加
    del: () => _p(300, 0.1, 'triangle'),// 删除
    err: () => _p(220, 0.15, 'sawtooth'),// 错误
    snap: () => _p(1200, 0.03),         // 吸附
    drop: () => _p(400, 0.06),          // 放下
  };
})();
"""


def execute(ctx: dict) -> dict:
    """当任务涉及编辑器/工具类应用时，注入音效系统。"""
    task = ctx.get("task", "")
    interactions = ctx.get("interactions", "")

    sfx_keywords = ["编辑器", "工具", "拖拽", "音效", "NLE", "IDE"]
    if not any(kw in task + interactions for kw in sfx_keywords):
        return ctx

    ctx.setdefault("_inject_js", []).append(WEBAUDIO_TEMPLATE)
    ctx.setdefault("_style_fixes", []).append("注入WebAudio音效系统")
    return ctx


node = Node(
    id="220",
    name="音效系统",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["编辑器", "工具", "拖拽", "音效", "NLE"]},
    execute=execute,
    refs=[],
    metadata={"source": "GUI前端集成验证/WebAudio", "category": "interaction"},
)
