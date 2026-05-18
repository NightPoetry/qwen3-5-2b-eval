"""知识节点：自循环调试基础设施——可观测/可操控/可模拟/可对比。

四支柱：
  1. 可观测：结构化日志远程读取（不是console.log）
  2. 可操控：API等价UI操作（eval端点/状态注入）
  3. 可模拟：外部依赖mock（同协议、可切换）
  4. 可对比：量化前后（时间分布、结构化测试结果）

当生成的代码涉及API调用/外部依赖时注入调试模式。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

DEBUG_TEMPLATE = """
// 调试基础设施（开发模式自动启用）
const DEBUG = location.hostname === 'localhost';
const _log = [];
const dlog = (tag, msg, data) => {
  const entry = {t: Date.now(), tag, msg, data};
  _log.push(entry);
  if (_log.length > 2000) _log.shift();
  if (DEBUG) console.log(`[${tag}]`, msg, data || '');
};
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    js = ctx.get("js", "")
    if not any(kw in task + js for kw in ["fetch", "API", "调试", "debug", "服务"]):
        return ctx

    ctx.setdefault("_inject_js", []).append(DEBUG_TEMPLATE)
    ctx.setdefault("_design_principles", []).append(
        "调试四支柱：可观测+可操控+可模拟+可对比"
    )
    return ctx

node = Node(id="480", name="调试基础设施",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["调试", "debug", "API", "服务", "fetch", "后端"]},
    execute=execute, refs=["450"],
    metadata={"source": "knowledge/self-loop-debugging", "category": "quality"})
