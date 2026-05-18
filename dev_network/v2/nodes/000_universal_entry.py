"""
万能入口节点 — 连接所有节点，触发条件自己筛选。

用户只给一句话。这个节点什么都不做，只负责把context传递出去。
所有其他节点通过自己的trigger决定是否激活。
网络就是路由器。不需要外面有人选路径。
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def execute(ctx: dict) -> dict:
    ctx.setdefault("task", "")
    return ctx


# refs连接所有顶层节点——触发条件自己筛选
node = Node(
    id="000",
    name="万能入口",
    trigger={"type": "entry"},
    execute=execute,
    refs=[
        "B00",   # 工程域（最高优先——技术关键词先匹配）
        "C00",   # 推理域
        "D00",   # 创作域
        "A00",   # 对话域
        "890",   # 兜底对话（当所有域路由都不匹配时最后的安全网）
    ],
)
