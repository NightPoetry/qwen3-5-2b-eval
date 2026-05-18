"""知识节点：Develop模式步骤模板——从60+个双轨开发记录提炼的通用开发流程。

需求分析→现状调研→方案设计（可并行多方案）→选择方案→并行实现→编译验证→文档

来源：GLM-5(2dev) + Sonnet4.6(7dev) + Opus4.6(11dev) = 20个开发双轨记录
覆盖领域：游戏引擎系统设计、动态内存管理、数据迁移、翻译流水线、调试基础设施

关键发现——迭代设计演进模式（光照系统8轮案例）：
  轮1-2: 多概念分离（API表面积大）
  轮3: 用户要求统一表达→LightCurve四元组（参数化）
  轮5: 用户指出局限→通用内核I(next)=model(I,material)（函数化）
  轮6: 用户三连纠正→与FX系统对齐（架构一致性）
  轮7-8: 收敛为4 Kind最终版

设计演进规律：多概念→统一表达→参数化→函数化→架构对齐→收敛
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

DEVELOP_STEPS = [
    {"id": "D01", "name": "需求分析", "order": 0, "actor": "model",
     "action": "用户想要什么？核心诉求是什么？"},
    {"id": "D02", "name": "现状调研", "order": 1, "actor": "system",
     "action": "搜索现有代码/系统中相关实现，数量化（几个文件/几个函数）"},
    {"id": "D03", "name": "方案设计", "order": 2, "actor": "model",
     "action": "设计2-3个方案，标注优劣。可并行设计多方案", "parallel": True},
    {"id": "D04", "name": "选择方案", "order": 3, "actor": "model",
     "action": "选最小改动+最大收益的方案，说明选择原因"},
    {"id": "D05", "name": "并行实现", "order": 4, "actor": "system",
     "action": "按方案实现，可拆多个子任务并行", "parallel": True},
    {"id": "D06", "name": "编译验证", "order": 5, "actor": "system",
     "action": "编译→打包→运行→验证功能正确"},
    {"id": "D07", "name": "文档更新", "order": 6, "actor": "system",
     "action": "更新相关文档和README"},
]

DEVELOP_INSIGHTS = [
    "用户反馈驱动架构演进——每轮反馈都可能是关键转折",
    "社交判断给AI做而非硬编码——LLM天然擅长模糊决策",
    "事件驱动优于轮询——状态变化触发点可枚举时下次时间是确定性的",
    "用户行为>用户声明——行为比口头声明更真实(+/-20%漂移学习)",
    "趋势判断防反复横跳——缩容/扩容需要冷却期+趋势统计(60帧滑动窗口)",
    "设计从多概念开始→用户要求统一→参数化→函数化→架构对齐→收敛",
    "统一表达诉求=用一个结构表达所有行为——降低API表面积",
    "自创概念违反架构对齐原则——与已有系统的API模式保持一致",
    "归属判断标准=谁驱动了变化——按因果关系归属，不按直觉归属",
    "JS单线程→不需要版本号/分块迁移——同步拷贝足够快(100K约0.05ms)",
    "只有2/15系统使用TypedArray——改造前先调研影响范围",
    "引用链比文件移动本身复杂——配置路径是主要风险点",
    "无bind mount的容器=数据永久丢失——必须立即导出，优先级最高",
    "卷改名=全局路径重构——改名前必须完成依赖图扫描",
    "交互调试五原则：可自视+可远操+可感知+可全知+可封印",
]

def execute(ctx: dict) -> dict:
    ctx["_develop_steps"] = DEVELOP_STEPS
    ctx.setdefault("_design_principles", []).extend(DEVELOP_INSIGHTS)
    return ctx

node = Node(id="610", name="Develop模式模板",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["开发", "新功能", "新建", "创建", "develop", "实现", "设计",
                          "架构", "重构", "迁移"]},
    execute=execute, refs=["340"],
    metadata={"source": "Agent/GLM-5×2+Sonnet4.6×7+Opus4.6×11=20develop", "category": "methodology"})
