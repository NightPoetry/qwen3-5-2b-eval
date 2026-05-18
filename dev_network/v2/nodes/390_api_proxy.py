"""知识节点：API代理/路由架构——请求转发、负载均衡、错误重试。"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

API_RULES = [
    "代理必须透传原始请求头（特别是Content-Type和Authorization）",
    "超时要分层：连接超时(5s) < 读超时(30s) < 总超时(60s)",
    "重试只对幂等请求(GET/PUT)，不对非幂等(POST)自动重试",
    "错误响应不要吞掉——透传上游的status code和body",
    "日志记录：请求时间+上游响应时间+总耗时，用于定位瓶颈",
    "健康检查：定期ping上游，不健康的自动摘除",
]

def execute(ctx: dict) -> dict:
    ctx.setdefault("_domain_rules", []).extend(API_RULES)
    return ctx

node = Node(id="390", name="API代理模式",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["代理", "proxy", "API", "路由", "转发", "负载均衡", "gateway"]},
    execute=execute, refs=["Y20"],
    metadata={"source": "API代理路由架构师", "category": "domain_network"})
