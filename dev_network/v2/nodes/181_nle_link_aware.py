"""知识节点：NLE绑定感知操作 — split/delete/drag必须link-aware。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


LINK_OPERATIONS = """
// 绑定感知操作模板
function splitClip(clip, splitTime) {
  const leftDur = splitTime - clip.startTime;
  const rightStart = splitTime;
  const rightSourceIn = clip.sourceIn + leftDur;

  const left = {...clip, duration: leftDur, sourceOut: clip.sourceIn + leftDur};
  const right = {
    ...clip,
    id: Date.now(),
    startTime: rightStart,
    duration: clip.duration - leftDur,
    sourceIn: rightSourceIn,
    linkId: crypto.randomUUID(), // 右半获得新linkId
  };
  return [left, right];
}

function rippleDelete(clips, deletedClip) {
  return clips
    .filter(c => c.id !== deletedClip.id)
    .map(c => {
      if (c.trackId === deletedClip.trackId && c.startTime > deletedClip.startTime) {
        return {...c, startTime: c.startTime - deletedClip.duration};
      }
      return c;
    });
}

function dragWithPartners(mainClip, dx, allClips) {
  const partners = allClips.filter(c => c.linkId === mainClip.linkId && c.id !== mainClip.id);
  mainClip.startTime += dx;
  partners.forEach(p => { p.startTime += dx; });
}
"""


def execute(ctx: dict) -> dict:
    """注入link-aware操作模板。"""
    ctx.setdefault("_inject_js", []).append(LINK_OPERATIONS)
    ctx.setdefault("_style_fixes", []).append("注入NLE绑定感知操作模板")
    return ctx


node = Node(
    id="181",
    name="NLE绑定操作",
    trigger={"type": "key_exists", "key": "contract"},
    execute=execute,
    refs=["Y20"],
    metadata={"source": "视频时间轴编辑器工程师", "category": "domain_nle"},
)
