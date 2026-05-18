"""知识节点：Tauri桌面应用诊断 — 图标/API变更/崩溃诊断/序列化陷阱。

适用场景：任务涉及桌面应用、Tauri、Rust+前端集成。
融合：tauri-desktop-app
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

TAURI_KNOWLEDGE = """你是Tauri桌面应用专家。根据以下知识诊断任务中的问题。

## 图标与资源
- PNG bit_depth=16会导致Icon::from_rgba校验失败（解码后RGBA数据量翻倍）。native GUI框架只接受8-bit RGBA
- macOS sips只报告尺寸不报告bit depth。检测bit depth须读PNG IHDR chunk第25字节
- sips -z对已经是目标尺寸的图片是no-op不触发resample，须先resize到不同尺寸再resize回来强制8-bit输出
- 设计工具导出图标可能默认16-bit color，app场景永远用8-bit

## Tauri v2 API变更
- v2的JS invoke路径从window.__TAURI__.invoke()改为window.__TAURI__.core.invoke()
- 调用不存在的invoke()抛TypeError被catch静默吞掉——前端零报错，数据请求静默失败
- import路径也改了：v1是from '@tauri-apps/api/tauri'，v2是from '@tauri-apps/api/core'
- withGlobalTauri:true只管注入对象，不管路径对不对

## 崩溃诊断
- macOS crash report(.ips，~/Library/Logs/DiagnosticReports/)是JSON格式，Rust release不strip符号
- Rust panic特征：exception.type=EXC_CRASH，signal=SIGABRT，栈中有panic_with_hook
- panic_cannot_unwind意味着panic在extern "C"函数内（FFI边界），往下一帧是实际位置
- 在did_finish_launching崩溃=启动初始化失败，常见于图标/资源/窗口创建

## 序列化陷阱
- serde_json::from_str::<HashMap<String,String>>()遇到非字符串值反序列化失败，配合unwrap_or_default()静默返回空HashMap
- 应使用HashMap<String, serde_json::Value>接受任意JSON值

## 构建
- Builder::run()返回Result；build()+App::run()不返回Result但允许中间初始化
- OnceLock<AppHandle>可安全跨线程共享AppHandle
"""


def execute(ctx: dict) -> dict:
    """检查生成的代码是否涉及Tauri场景，注入诊断规则。"""
    task = ctx.get("task", "")
    html = ctx.get("html", "")
    js = ctx.get("js", "")

    tauri_signals = ["tauri", "桌面", "desktop", "native", "electron", "wry"]
    if not any(s in (task + html + js).lower() for s in tauri_signals):
        return ctx

    warnings = []

    # 结构检查：HTML绝对路径
    abs_paths = re.findall(r'(?:src|href)=["\']/((?!/).+?)["\']', html)
    if abs_paths:
        warnings.append(f"HTML有绝对路径引用{abs_paths[:3]}——Tauri协议下会404，改为相对路径")

    # 结构检查：v1 API路径
    if "window.__TAURI__.invoke" in js and "core.invoke" not in js:
        warnings.append("检测到v1 API路径__TAURI__.invoke()——v2须改为__TAURI__.core.invoke()")

    if "from '@tauri-apps/api/tauri'" in js:
        warnings.append("检测到v1 import路径——v2须改为from '@tauri-apps/api/core'")

    # LLM语义诊断
    result = ask(
        TAURI_KNOWLEDGE +
        "\n分析以下任务涉及的Tauri风险点，给出具体建议（每条一行，不超过4条）。"
        "如果不涉及Tauri风险，回答'无Tauri风险'。",
        f"任务：{task[:400]}\nJS片段：{js[:300]}",
        max_tokens=250
    ).strip()

    if "无Tauri风险" not in result:
        warnings.append(result)

    if warnings:
        ctx.setdefault("_warnings", []).extend(warnings)

    return ctx


node = Node(
    id="170",
    name="Tauri诊断",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["tauri", "桌面", "desktop", "native", "wry",
                          "AppHandle", "invoke", "crash", "ips"]},
    execute=execute,
    refs=["171"],
    metadata={"source": "knowledge/tauri-desktop-app", "category": "platform"},
)
