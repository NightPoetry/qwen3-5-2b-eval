"""知识节点：NLE导出渲染管线——ffmpeg filter_complex/时间门控overlay/音频混合。

融合：多clip导出渲染管线设计指南（去敏化：移除项目名）
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

EXPORT_KNOWLEDGE = """你是视频编辑导出管线专家。根据以下知识指导NLE导出设计。

## 核心原则：一次ffmpeg多输入
- 不要每个clip单独跑ffmpeg再concat——冷启动开销叠加，编码参数不一致会裂
- 一次ffmpeg、N个-i输入、一个filter_complex时间对齐+透明合成+混音+一次编码

## Plan Schema：扁平化
- 不带track概念——video和audio各自拍平成N条记录
- 每条只携带ffmpeg渲染需要的字段：input_path/clip_start/clip_dur/src_in/src_out/draw_x/y/w/h
- track顺序由数组z-order决定，音频mix时track边界无意义

## filter_complex关键四件事
1. setpts=PTS-STARTPTS+CLIPSTART/TB — 时间偏移到目标位置
2. enable='between(t,a,b)' — overlay时间门控，范围外露出底层
3. eof_action=pass — 单条clip EOF不断链（默认repeat会冻帧）
4. color=...:d=DUR — 背景持续到整条时间轴时长

## 省略enable的陷阱
- trim出来的帧没有"过期"概念，setpts后仍被overlay读取显示
- 必须用enable显式声明可见时间窗口

## 音频adelay+amix
- adelay=CLIPSTART_MS:all=1 — all=1必须显式写否则多声道只delay第一声道
- amix:normalize=0必须显式 — normalize=1(默认)按输入数量除总音量越混越轻
- 单clip用anull比amix=inputs=1更省

## 多边形遮罩per-clip切片
- mask基于输出画布坐标——对每条clip须crop到局部dw:dh范围
- 用crop不用scale——scale会把形状压缩变形

## 进度回报
- ffmpeg -progress pipe:1 → out_time_us字段 → 百分比=out_time_us/(duration*1e6)
- 不要把stderr重定向进stdout——会和progress输出混乱
- 失败时把stderr末尾8行截回前端作为错误信息

## 自检方法
- fixture：用ffmpeg lavfi生成最小测试video/audio
- 直调invoke跳过file picker dialog
- ffprobe验证输出的codec/分辨率/时长/audio sample rate
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        EXPORT_KNOWLEDGE +
        "\n分析以下任务涉及的视频导出管线问题，给出建议（每条一行，不超过4条）。"
        "如果不涉及导出管线，回答'无相关问题'。",
        f"任务：{task[:500]}",
        max_tokens=250
    ).strip()
    if "无相关问题" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx

node = Node(id="E21", name="NLE导出管线",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["导出", "export", "ffmpeg", "filter_complex",
                          "渲染", "render", "编码", "encode", "overlay",
                          "amix", "adelay", "concat", "视频编辑"]},
    execute=execute, refs=["E20"],
    metadata={"source": "Guild/视频剪辑交互设计/多clip导出渲染管线", "category": "domain_nle"})
