"""
v2 执行引擎 — 节点图栈展开执行器。

写死的只有这个文件（引擎本身）。
所有业务逻辑通过节点定义文件注入。

执行模型：
  1. 从入口节点开始
  2. 检查触发条件（trigger）
  3. 满足 → 执行节点代码（execute）
  4. 执行产出 context 更新
  5. 检查邻接节点（refs）的触发条件
  6. 满足的邻接 → 压入执行栈
  7. 栈顶弹出，重复2-6
  8. 栈空 → 结束

栈展开 = 深度优先。环由 visited 集合自然阻止。
节点执行顺序由栈决定（后进先出 = 深度优先遍历）。
"""

import json
import re
import importlib.util
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Node:
    """一个可执行节点 = 一个 tool。"""
    id: str
    name: str
    trigger: dict
    execute: Callable  # fn(context) -> context
    refs: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class ExecutionFrame:
    """栈帧：记录节点执行的上下文。"""
    node_id: str
    depth: int
    reason: str  # 为什么被激活（"entry" / "ref from xxx"）


class Engine:
    """
    节点图执行引擎。

    唯一写死的东西：栈展开逻辑 + 触发检查 + context传递。
    所有节点通过 register() 或 load_from_dir() 注入。
    """

    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.trace: list[dict] = []  # 执行轨迹

    def register(self, node: Node):
        """注册一个节点。"""
        self.nodes[node.id] = node

    def load_from_dir(self, path: Path):
        """从目录加载所有节点定义（.py文件，每个文件 export 一个 node）。"""
        for f in sorted(path.glob("*.py")):
            if f.name.startswith("_"):
                continue
            spec = importlib.util.spec_from_file_location(f.stem, f)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "node"):
                self.register(mod.node)

    def check_trigger(self, node: Node, context: dict) -> bool:
        """检查节点触发条件是否满足。"""
        trigger = node.trigger
        unless = trigger.get("unless")
        if unless and unless in context:
            return False
        t = trigger.get("type", "")

        if t == "always":
            return True
        elif t == "entry":
            return context.get("_entry") == node.id
        elif t == "regex":
            target = context.get(trigger.get("target", "_input"), "")
            pattern = trigger.get("pattern", "")
            return bool(re.search(pattern, str(target)))
        elif t == "keyword":
            target = context.get(trigger.get("target", "_input"), "")
            keywords = trigger.get("keywords", [])
            return any(kw in str(target) for kw in keywords)
        elif t == "key_exists":
            return trigger.get("key", "") in context
        elif t == "condition":
            # 用 eval 执行简单条件表达式（context中的值）
            expr = trigger.get("expr", "False")
            try:
                return bool(eval(expr, {"__builtins__": {}}, context))
            except Exception:
                return False
        return False

    def run(self, entry_id: str, context: dict = None) -> dict:
        """
        从入口节点开始执行。支持三级续入。

        续入策略（按优先级）：
        1. 工作节点续入：从 _cursor 中非输出节点的邻接尝试
        2. 域续入：从 _active_domain 域路由重新进入
        3. 全局入口：回退到 entry_id（话题切换）

        执行结束后写入：
        - _cursor：本轮激活的非输出工作节点（最多3个）
        - _active_domain：本轮经过的域路由ID
        """
        context = context or {}
        context["_entry"] = entry_id

        cursor = context.pop("_cursor", [])
        active_domain = context.pop("_active_domain", None)
        context.pop("_domain_routed", None)
        resumed = False
        resume_reason = "entry"

        if cursor:
            work_nodes = [c for c in cursor if not c.startswith("Y")]
            keyword_match = None
            fallback_match = None
            for cursor_id in work_nodes:
                cursor_node = self.nodes.get(cursor_id)
                if not cursor_node:
                    continue
                for ref_id in cursor_node.refs:
                    if ref_id.startswith("Y"):
                        continue
                    ref_node = self.nodes.get(ref_id)
                    if not ref_node or not self.check_trigger(ref_node, context):
                        continue
                    t = ref_node.trigger.get("type", "")
                    if t == "always":
                        continue
                    if t in ("keyword", "key_exists", "condition") and not keyword_match:
                        keyword_match = (ref_id, cursor_id)
                    elif t == "regex" and not fallback_match:
                        fallback_match = (ref_id, cursor_id)
            best = keyword_match or fallback_match
            if best:
                entry_id, from_id = best
                resumed = True
                resume_reason = f"resume from {from_id}"

        if not resumed and active_domain:
            domain_node = self.nodes.get(active_domain)
            if domain_node and self.check_trigger(domain_node, context):
                entry_id = active_domain
                resumed = True
                resume_reason = f"domain resume {active_domain}"

        stack: list[ExecutionFrame] = [
            ExecutionFrame(
                node_id=entry_id, depth=0,
                reason=resume_reason
            )
        ]
        visited: set[str] = set()
        self.trace = []

        while stack:
            frame = stack.pop()

            if frame.node_id in visited:
                continue
            visited.add(frame.node_id)

            node = self.nodes.get(frame.node_id)
            if not node:
                continue

            if not self.check_trigger(node, context):
                visited.discard(frame.node_id)
                continue

            self.trace.append({
                "node": node.id,
                "name": node.name,
                "depth": frame.depth,
                "reason": frame.reason,
            })

            try:
                context = node.execute(context)
            except Exception as e:
                context["_errors"] = context.get("_errors", [])
                context["_errors"].append({"node": node.id, "error": str(e)})
                self.trace[-1]["error"] = str(e)
                continue

            if node.metadata.get("category") == "domain":
                context["_active_domain"] = node.id

            active_refs = node.refs
            route_filter = context.get("_eng_refs")
            if route_filter and node.metadata.get("category") == "domain":
                active_refs = [r for r in node.refs if r in route_filter]
                context.pop("_eng_refs", None)

            for ref_id in reversed(active_refs):
                if ref_id not in visited:
                    ref_node = self.nodes.get(ref_id)
                    if ref_node and self.check_trigger(ref_node, context):
                        stack.append(ExecutionFrame(
                            node_id=ref_id,
                            depth=frame.depth + 1,
                            reason=f"ref from {node.id}",
                        ))

        if self.trace:
            work = [t["node"] for t in self.trace if not t["node"].startswith("Y")]
            context["_cursor"] = work[-3:] if work else [self.trace[-1]["node"]]

        return context

    def print_trace(self):
        """打印执行轨迹。"""
        for t in self.trace:
            indent = "  " * t["depth"]
            err = f" [ERROR: {t['error']}]" if "error" in t else ""
            print(f"{indent}[{t['node']}] {t['name']} ({t['reason']}){err}")
