"""知识节点：NLE时间空间映射 — timeline-time vs source-time。

适用场景：涉及视频/音频/时间轴/播放的应用。
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


TIME_MAPPING_TEMPLATE = """
// 时间空间映射（NLE核心）
// timeline-time: 用户在轨道上看到的时间
// source-time: 媒体文件内部的时间
// 映射: srcTime = clip.sourceIn + (tlTime - clip.startTime)
// 反映射: tlTime = clip.startTime + (srcTime - clip.sourceIn)

const Clip = {
  startTime: 0,    // timeline上的左边缘
  duration: 0,     // timeline上占多长
  sourceIn: 0,     // source的起点
  sourceOut: 0,    // source的终点
  linkId: null,    // 绑定组ID（持久化字段，不可推断）
};

function tlToSource(clip, tlTime) {
  return clip.sourceIn + (tlTime - clip.startTime);
}

function sourceToTl(clip, srcTime) {
  return clip.startTime + (srcTime - clip.sourceIn);
}
"""


def execute(ctx: dict) -> dict:
    """当任务涉及时间轴/视频时，注入时间映射模型到契约。"""
    task = ctx.get("task", "")

    # 注入数据模型
    contract = ctx.get("contract", {})
    contract["data"] = {
        "storage_key": "timeline_clips",
        "format": "[{id, startTime, duration, sourceIn, sourceOut, linkId, trackId}]",
    }
    contract.setdefault("interaction_patterns", []).extend([
        "Split操作：左半保留原linkId，右半获得新linkId",
        "Ripple Delete：删除后右侧所有clip左移被删总时长",
        "播放时必须做timeline→source时间映射",
        "video.currentTime是source时间，不是timeline时间",
    ])
    ctx["contract"] = contract

    # 注入时间映射工具代码
    ctx.setdefault("_inject_js", []).append(TIME_MAPPING_TEMPLATE)

    return ctx


node = Node(
    id="180",
    name="NLE时间映射",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["时间轴", "视频编辑", "播放", "timeline", "NLE", "剪辑"]},
    execute=execute,
    refs=["181"],
    metadata={"source": "视频时间轴编辑器工程师", "category": "domain_nle"},
)
