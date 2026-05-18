"""知识节点：双轨思考元方法——思考轨先于执行轨。

这是所有Agent训练数据的元结构（源自Agent/README.md双轨格式规范）：
  - 思考轨(T步骤)：分析/假设/推理/验证——每步一个简单问题
  - 执行轨(E步骤)：代码操作/编译/测试——每步一个确定性操作
  - order语义：正数从小到大顺序执行，负数从大到小，相同order可并行
  - 交叉引用：思考驱动执行，执行反馈思考（明确标注依赖关系）

双轨数据统计（60+文件，4个模型）：
  GLM-5:    9 fix + 2 develop = 11条（嵌入式+Web服务）
  Sonnet4.6: 8 fix + 7 develop = 15条（游戏引擎ECS）
  Opus4.6:  11 fix + 11 develop = 22条（桌面应用+系统维护+翻译）
  Haiku4.5:  1 execution = 1条（系统操作）
  总计：49条双轨记录

Fix/Develop模式切换触发规则：
  Fix: 已有功能出现bug——关键词：修复/错误/回归/断线/崩溃
  Develop: 新功能或增强——关键词：开发/新建/设计/重构
  切换触发：用户提出新需求→Fix转Develop；开发中发现bug→Develop转Fix

对应到2B编排系统：
  - T步骤 = 模型节点（问一个简单问题）
  - E步骤 = 系统节点（执行确定性操作）
  - order = refs中的触发顺序
  - 交叉引用 = 节点间的context传递
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    ctx.setdefault("_design_principles", []).extend([
        "思考先于执行——先T轨分析清楚再E轨动手",
        "相同order可并行——独立的排除/实现/检查同时进行",
        "根因确认用粗体标记——这是修复的转折点",
        "方案选择说明原因——不是随便选的",
        "调试日志最后必须清理——不留在生产代码中",
        "Fix模式8步(确认现象→因果链→并行排除→定位→验证→方案→修复→清理)",
        "Develop模式7步(需求→调研→方案设计→选择→并行实现→编译→文档)",
        "依赖标注确保执行顺序正确——T05依赖T02+T03，E04依赖T05",
        "模式切换灵活——用户可能混用Fix和Develop，需动态识别",
        "模型能力差异：大模型单次完成=小模型分步完成——2B必须拆原子步",
    ])
    return ctx

node = Node(id="630", name="双轨思考元方法",
    trigger={"type": "always"},
    execute=execute, refs=["Y30"],
    metadata={"source": "Agent/README+60+双轨记录+4模型switch.md", "category": "methodology"})
