"""知识节点：Fix模式步骤模板——从60+个双轨调试记录提炼的通用修复流程。

确认现象→建立因果链→并行排除→定位根因→验证假设→设计方案→并行修复→清理验证

来源：GLM-5(9fix) + Sonnet4.6(8fix) + Opus4.6(11fix) + Haiku4.5(1exec)
覆盖领域：嵌入式(ESP32)、游戏引擎(ECS)、Web服务(HTTP/WS)、桌面应用(Tauri)、CI/CD
每步标注actor(系统/模型)和可并行性。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

FIX_STEPS = [
    {"id": "F01", "name": "确认现象", "order": 0, "actor": "model",
     "action": "用一句话描述观察到的异常现象（不猜原因）"},
    {"id": "F02", "name": "建立因果链", "order": 1, "actor": "model",
     "action": "什么改了？改之前正常吗？改了什么导致异常？"},
    {"id": "F03", "name": "并行排除", "order": 2, "actor": "system",
     "action": "对每个可能原因独立检查：编译产物/缓存/配置/环境",
     "parallel": True},
    {"id": "F04", "name": "定位根因", "order": 3, "actor": "model",
     "action": "从排除结果中推断根因，用一句话表述"},
    {"id": "F05", "name": "验证根因", "order": 4, "actor": "system",
     "action": "添加日志/断点验证推断是否正确"},
    {"id": "F06", "name": "设计方案", "order": 5, "actor": "model",
     "action": "列2-3个修复方案，选最小改动的，说明选择原因"},
    {"id": "F07", "name": "实施修复", "order": 6, "actor": "system",
     "action": "按方案修改代码", "parallel": True},
    {"id": "F08", "name": "清理验证", "order": 7, "actor": "system",
     "action": "移除调试代码→编译→测试→确认修复"},
]

# 从4个模型×29个fix记录提炼的高频根因模式
ROOT_CAUSE_PATTERNS = [
    "API不做预期处理(如URL解码)——查阅底层框架源码确认行为",
    "初始化时序错误——createData在initialize之前执行=写入静默失败",
    "静默失败——Float32Array(0)写入不报错但数据丢失；undefined比较永远false",
    "引用错误——info.bounceThreshold但类型定义中无此字段=undefined",
    "死代码——重连分支在if-else中永远不被执行(静态分配对象永不为null)",
    "Token/凭证过期——未解析expires_in、未记录获取时间、无刷新机制",
    "嵌入式内存碎片——重复new/delete导致连续块不足=SSL握手失败",
    "配置路径硬编码——卷改名/迁移后所有引用链断裂",
    "权限问题——macOS .app包内目录只读=PermissionError",
    "缓存不一致——浏览器缓存旧产物、编译产物未更新",
]

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    ctx["_fix_steps"] = FIX_STEPS
    ctx["_root_cause_patterns"] = ROOT_CAUSE_PATTERNS
    ctx.setdefault("_design_principles", []).extend([
        "思考轨先于执行轨——先分析再操作，避免盲目修改",
        "并行排除比串行快——同order的检查可以并行",
        "根因确认前不要开始修复——否则可能修错方向",
        "根因确认用粗体标记——这是修复的转折点",
        "选方案说明原因——不是随便选的，选最小改动+最大覆盖的",
        "惰性初始化守卫模式：if(!this._initialized) this.initialize()",
        "静态分配消除碎片——嵌入式场景中一次分配运行时永不释放",
        "影响范围评估——grep所有调用点分类受影响vs不受影响",
        "就地操作零额外内存——如URL解码src/dst双指针，decoded总<=原始长度",
        "调试日志最后必须清理——不留在生产代码中",
        "物理防抖多轮迭代——第一轮修引用错误、第二轮加容忍量、第三轮加冷却",
    ])
    return ctx

node = Node(id="600", name="Fix模式模板",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["修复", "bug", "fix", "错误", "回归", "regression", "坏了",
                          "断线", "崩溃", "crash", "失败", "broken"]},
    execute=execute, refs=["420"],
    metadata={"source": "Agent/GLM-5×9+Sonnet4.6×8+Opus4.6×11+Haiku4.5×1=29fix", "category": "methodology"})
