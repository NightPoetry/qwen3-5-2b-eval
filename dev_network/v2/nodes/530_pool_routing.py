"""知识节点：池优先路由——多供应商多账号跨池降级。

数据模型：models表 + model_pool_bindings表(多对多+优先级) + model_aliases表。
决策链：别名解析→按priority遍历绑定→跳过unavailable→取健康账号→跨池重试。
探测：从真实流量学习(成功→available, 404→unavailable)，不额外发探测请求。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

ROUTING_RULES = [
    "一个模型可绑定多个池，priority控制路由优先级",
    "probe_status是软提示不是硬禁止——所有available都失败后仍尝试unavailable",
    "未注册模型不直接拒绝——透传到所有池尝试（新模型可能刚上线）",
    "失败重试链：同池其他账号→同模型其他池→相似模型→兜底模型",
    "内存缓存+DB持久化：热路径零DB查询，CRUD后刷新缓存",
    "路由决策在proxy函数内部做——不要在入口就构造upstreamConfig",
]

def execute(ctx: dict) -> dict:
    ctx.setdefault("_domain_rules", []).extend(ROUTING_RULES)
    return ctx

node = Node(id="530", name="池优先路由",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["路由", "多池", "降级", "供应商", "负载均衡", "中转", "代理网关"]},
    execute=execute, refs=["390"],
    metadata={"source": "API代理路由架构师", "category": "domain_network"})
