"""
Tool state machine — v2

设计原则：
  - 模型永远不计算字符绝对位置
  - 普通文本：模型看行号，调 advance_past(to_line=N)
  - 无换行文本：模型复述末尾片段，调 advance_past(tail="...")
  - 多匹配消歧：工具返回候选+上下文，模型在同一 context 里识别后调 confirm_advance
"""

import bisect
import json


class ToolState:
    def __init__(self, text: str):
        self.text = text
        self.cursor: int = 0
        self.stack: list[str] = []
        self.records: list[dict] = []
        self.call_log: list[dict] = []
        self._pending_candidates: list[int] = []
        self._last_tail: str = ""
        self._window_end_line: int = 0  # 最近一次 read_next 展示的最后一行行号
        self._last_read_cursor: int = -1  # 上次 read_next 时的游标位置，用于检测重复读取
        self._analyzer = None  # 任务相关的行分析函数

        # 预计算行起始位置（_line_starts[i] = 第 i+1 行的第一个字符的绝对偏移）
        self._line_starts: list[int] = [0]
        for i, c in enumerate(text):
            if c == "\n":
                self._line_starts.append(i + 1)

    # ── 内部辅助 ──────────────────────────────────────────────────────────────

    def _char_to_line(self, pos: int) -> int:
        """返回 pos 所在行的行号（1-indexed）。"""
        return bisect.bisect_right(self._line_starts, pos)

    def _line_end_char(self, line_num: int) -> int:
        """返回第 line_num 行（1-indexed）末尾之后的字符偏移（即下一行起始）。"""
        idx = line_num  # _line_starts[line_num] 是第 line_num+1 行的起始
        if idx >= len(self._line_starts):
            return len(self.text)
        return self._line_starts[idx]

    def _total_lines(self) -> int:
        return len(self._line_starts)

    # ── 读取 ──────────────────────────────────────────────────────────────────

    def read_next(self, n_lines: int = 10) -> dict:
        if self.cursor >= len(self.text):
            return {"content_type": "end_of_document", "done": True}

        if self._last_read_cursor == self.cursor:
            return {
                "error": (
                    "游标未移动——你上次 read_next 读取的内容尚未推进。"
                    "必须先调用 advance_past(to_line=<advance_target>) 推进游标，"
                    "然后再调用 read_next()。"
                ),
            }
        self._last_read_cursor = self.cursor

        # 探测是否处于超长行（无换行文本）
        next_nl = self.text.find("\n", self.cursor)
        chars_to_nl = (next_nl - self.cursor) if next_nl != -1 else (len(self.text) - self.cursor)

        if chars_to_nl > 600:
            # 无换行模式：返回字符片段
            end = min(self.cursor + 400, len(self.text))
            content = self.text[self.cursor:end]
            return {
                "content_type": "char_segment",
                "content": content,
                "chars_remaining_in_doc": len(self.text) - end,
                "提示": (
                    "此内容无换行符。处理完毕后必须调用 advance_past(tail=<末尾片段>)，"
                    "tail 应为您本次处理完的最后 10~20 个字符的准确复述。"
                ),
            }

        # 正常行模式
        pos = self.cursor
        lines = []
        for _ in range(n_lines):
            if pos >= len(self.text):
                break
            nl = self.text.find("\n", pos)
            line_num = self._char_to_line(pos)
            if nl == -1:
                lines.append({"line": line_num, "content": self.text[pos:]})
                pos = len(self.text)
                break
            else:
                lines.append({"line": line_num, "content": self.text[pos:nl + 1].rstrip("\n")})
                pos = nl + 1

        last_line = lines[-1]["line"] if lines else self._char_to_line(self.cursor)
        self._window_end_line = last_line  # 记录本次展示的最大行号
        total = self._total_lines()
        remaining = total - last_line

        if self._analyzer:
            for entry in lines:
                analysis = self._analyzer(entry["content"])
                if analysis.get("is_target"):
                    entry["★目标"] = True
                    entry["item"] = analysis.get("item", "")
                    entry["category"] = analysis.get("category", "")

        result: dict = {
            "content_type": "lines",
            "lines": lines,
            "lines_remaining": remaining,
            "advance_target": last_line,
            "下一步": f"处理完上方内容后，必须调用 advance_past(to_line={last_line})。",
        }
        if remaining == 0:
            result["is_final_batch"] = True
            result["下一步"] = (
                f"这是最后一批内容。处理完毕后调用 advance_past(to_line={last_line})，"
                "然后立即调用 get_records() 汇总结果。"
            )
        return result

    # ── 游标推进 ──────────────────────────────────────────────────────────────

    def advance_past(self, tail: str = "", to_line: int = 0) -> dict:
        # 模式一：行号模式（普通文本）
        if to_line > 0:
            # 约束：不能推进到未读到的行
            if self._window_end_line > 0 and to_line > self._window_end_line:
                return {
                    "error": (
                        f"第 {to_line} 行超出了您上次读取的范围（最后读到第 {self._window_end_line} 行，"
                        f"文档共 {self._total_lines()} 行）。"
                        f"请先调用 read_next() 读取更多内容，然后推进到不超过第 {self._window_end_line} 行的位置。"
                    )
                }
            new_cursor = self._line_end_char(to_line)
            if new_cursor <= self.cursor:
                return {
                    "error": f"第 {to_line} 行已在当前游标之前，不得后退。请传入更大的行号。"
                }
            self.cursor = new_cursor
            done = self.cursor >= len(self.text)
            result: dict = {
                "advanced": True,
                "current_line": self._char_to_line(self.cursor),
                "lines_remaining": self._total_lines() - self._char_to_line(self.cursor),
                "done": done,
            }
            if done:
                result["必须执行"] = "文档已读完，立即调用 get_records() 汇总结果后停止。"
            else:
                total = self._total_lines()
                pct = round(self.cursor / max(len(self.text), 1) * 100)
                result["下一步"] = (
                    f"【严禁停止】文档仅读完 {pct}%，还剩 {result['lines_remaining']} 行未读。"
                    "必须立即调用 read_next() 继续，不得输出任何文字。"
                )
            return result

        # 模式二：末尾片段模式（无换行文本）
        if not tail:
            return {"error": "必须提供 to_line（行号）或 tail（末尾片段）之一。"}

        self._last_tail = tail
        occurrences: list[int] = []
        pos = self.cursor
        while True:
            idx = self.text.find(tail, pos)
            if idx == -1:
                break
            occurrences.append(idx)
            pos = idx + 1

        if not occurrences:
            return {
                "error": "未找到指定的末尾片段，请检查是否准确复述了文本内容。",
                "tip": "可尝试截取更短或更独特的末尾片段重试。",
            }

        if len(occurrences) == 1:
            new_cursor = occurrences[0] + len(tail)
            self.cursor = new_cursor
            done = new_cursor >= len(self.text)
            result = {
                "advanced": True,
                "current_line": self._char_to_line(new_cursor),
                "done": done,
            }
            if done:
                result["必须执行"] = "文档已读完，立即调用 get_records() 汇总结果后停止。"
            else:
                pct = round(new_cursor / max(len(self.text), 1) * 100)
                result["下一步"] = (
                    f"【严禁停止】文档仅读完 {pct}%。"
                    "必须立即调用 read_next() 继续，不得输出任何文字。"
                )
            return result

        # 多匹配：返回候选供消歧
        self._pending_candidates = occurrences
        candidates = []
        for i, occ in enumerate(occurrences[:5]):
            before = max(0, occ - 40)
            after = min(len(self.text), occ + len(tail) + 40)
            candidates.append({
                "candidate_index": i,
                "line": self._char_to_line(occ),
                "context": self.text[before:after],
            })
        return {
            "multiple_matches": True,
            "count": len(occurrences),
            "candidates": candidates,
            "必须执行": (
                f"找到 {len(occurrences)} 处相同片段。请查看上方各候选的 context，"
                "结合您刚才读取的内容判断是哪一处，然后调用 confirm_advance(candidate_index=<编号>)。"
            ),
        }

    def confirm_advance(self, candidate_index: int) -> dict:
        if not self._pending_candidates:
            return {"error": "当前无待确认的候选，请先调用 advance_past。"}
        if candidate_index < 0 or candidate_index >= len(self._pending_candidates):
            return {
                "error": f"candidate_index 超出范围，有效值为 0 ~ {len(self._pending_candidates) - 1}。"
            }

        occ = self._pending_candidates[candidate_index]
        new_cursor = occ + len(self._last_tail)
        self.cursor = new_cursor
        self._pending_candidates = []
        done = new_cursor >= len(self.text)
        result: dict = {
            "advanced": True,
            "current_line": self._char_to_line(new_cursor),
            "done": done,
        }
        if done:
            result["必须执行"] = "文档已读完，立即调用 get_records() 汇总结果后停止。"
        return result

    # ── 嵌套栈 ────────────────────────────────────────────────────────────────

    def push(self, token: str) -> dict:
        self.stack.append(str(token))
        return {"pushed": token, "depth": len(self.stack)}

    def pop(self) -> dict:
        if not self.stack:
            return {"error": "栈为空，没有可弹出的元素。", "depth": 0}
        token = self.stack.pop()
        return {"popped": token, "depth": len(self.stack)}

    def get_depth(self) -> dict:
        return {
            "depth": len(self.stack),
            "stack_top": self.stack[-1] if self.stack else None,
        }

    def peek_stack(self) -> dict:
        return {
            "top": self.stack[-1] if self.stack else None,
            "depth": len(self.stack),
        }

    # ── 行分析（认知卸载）──────────────────────────────────────────────────────

    def analyze_line(self, content: str) -> dict:
        if not self._analyzer:
            return {"error": "未配置分析器。"}
        return self._analyzer(content)

    # ── 记录 ──────────────────────────────────────────────────────────────────

    def record(self, item: str, category: str) -> dict:
        entry = {"item": str(item), "category": str(category)}
        self.records.append(entry)
        return {"recorded": len(self.records), "entry": entry}

    def get_records(self) -> dict:
        return {"records": self.records, "count": len(self.records)}

    # ── 统计 ──────────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        return {
            "total_calls": len(self.call_log),
            "cursor": self.cursor,
            "total_length": len(self.text),
            "coverage_pct": round(self.cursor / max(len(self.text), 1) * 100, 1),
            "stack_depth": len(self.stack),
            "records_count": len(self.records),
        }


# ── 工具分发 ──────────────────────────────────────────────────────────────────

_DISPATCH = {
    "read_next":       lambda s, a: s.read_next(int(a.get("n_lines", 10))),
    "advance_past":    lambda s, a: s.advance_past(a.get("tail", ""), int(a.get("to_line", 0))),
    "confirm_advance": lambda s, a: s.confirm_advance(int(a["candidate_index"])),
    "push":            lambda s, a: s.push(a["token"]),
    "pop":             lambda s, a: s.pop(),
    "get_depth":       lambda s, a: s.get_depth(),
    "peek_stack":      lambda s, a: s.peek_stack(),
    "record":          lambda s, a: s.record(a["item"], a.get("category", "")),
    "get_records":     lambda s, a: s.get_records(),
    "analyze_line":    lambda s, a: s.analyze_line(a["content"]),
}


# ── 任务分析器（判断工具的内部逻辑）──────────────────────────────────────────

def analyzer_python_top_level(content: str) -> dict:
    """判断一行代码是否为顶级函数定义。"""
    if not content.startswith("def "):
        return {"is_target": False, "reason": "不是 def 定义"}
    rest = content[4:]
    paren = rest.find("(")
    if paren <= 0:
        return {"is_target": False, "reason": "def 后没有找到函数名"}
    name = rest[:paren].strip()
    return {
        "is_target": True,
        "item": name,
        "category": "function",
        "action": f"这是顶级函数 '{name}'，请调用 record(item='{name}', category='function')。",
    }


def analyzer_html_heading(content: str) -> dict:
    """判断一行是否包含 HTML 标题标签。"""
    import re
    m = re.match(r'<h([1-6])[^>]*>(.*?)</h\1>', content.strip(), re.IGNORECASE)
    if not m:
        return {"is_target": False, "reason": "不是标题标签"}
    level = f"h{m.group(1)}"
    text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
    return {
        "is_target": True,
        "item": text,
        "category": level,
        "action": f"这是 {level} 标题 '{text}'，请调用 record(item='{text}', category='{level}')。",
    }


def analyzer_minified_def(content: str) -> dict:
    """判断字符片段中是否包含函数定义。"""
    import re
    names = re.findall(r'def\s+(\w+)\s*\(', content)
    if not names:
        return {"is_target": False, "reason": "未发现函数定义"}
    return {
        "is_target": True,
        "items": [{"item": n, "category": "function"} for n in names],
        "action": f"发现函数：{names}，请对每个调用 record()。",
    }


ANALYZERS = {
    "python_functions": analyzer_python_top_level,
    "html_headings": analyzer_html_heading,
    "minified_python": analyzer_minified_def,
}


def execute_tool(state: ToolState, name: str, args: dict) -> str:
    handler = _DISPATCH.get(name)
    if handler is None:
        result = {"error": f"未知工具：{name}"}
    else:
        try:
            result = handler(state, args)
        except (KeyError, TypeError, ValueError) as e:
            result = {"error": str(e)}
    state.call_log.append({"tool": name, "args": args, "result": result})
    return json.dumps(result, ensure_ascii=False)


# ── 工具 Schema（中文 CN-STRONG）─────────────────────────────────────────────

def make_tool_schemas(include_stack: bool = True, include_record: bool = True,
                      include_analyze: bool = False) -> list[dict]:
    schemas = [
        {
            "type": "function",
            "function": {
                "name": "read_next",
                "description": (
                    "【每轮循环必须首先调用】从当前游标位置读取下一批内容（每批 5 行），无需指定起始位置。"
                    "普通文本返回带行号的行列表，可直接用行号调用 advance_past(to_line=N)。"
                    "无换行文本返回字符片段，需用 advance_past(tail=<末尾片段>) 推进。"
                    "读取后必须按任务规则处理内容，然后必须调用 advance_past，"
                    "否则游标不移动，下次仍读同一位置。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "n_lines": {
                            "type": "integer",
                            "description": "读取行数，默认 5，通常无需修改。",
                        }
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "advance_past",
                "description": (
                    "【处理完每段内容后必须立即调用】推进游标到已安全处理的位置。\n"
                    "用法一（普通文本，有行号）：传入 to_line=<行号>，推进到该行末尾。"
                    "行号直接从 read_next 返回的 lines 列表中读取，不得自行计算。\n"
                    "用法二（无换行文本，字符片段）：传入 tail=<末尾片段>，工具自动定位。"
                    "tail 必须是您本次处理完的最后 10~20 个字符的准确复述，不得修改或缩减。"
                    "若 tail 有多处匹配，将返回候选列表，必须随即调用 confirm_advance 确认。\n"
                    "严禁跳过此步骤。返回 done=true 时必须立即调用 get_records()。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to_line": {
                            "type": "integer",
                            "description": "普通文本模式：本次处理完的最后一行行号（从 read_next 结果读取）。与 tail 二选一。",
                        },
                        "tail": {
                            "type": "string",
                            "description": "无换行文本模式：本次处理完的末尾 10~20 个字符的准确复述。与 to_line 二选一。",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "confirm_advance",
                "description": (
                    "【当 advance_past 返回多个候选匹配时必须调用】从候选列表中选择正确位置。"
                    "对照每个候选的 context 字段与您刚才读取的内容，确认哪一处是您处理到的位置，"
                    "填入对应的 candidate_index。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "candidate_index": {
                            "type": "integer",
                            "description": "正确候选的编号，从 advance_past 返回的 candidates 列表中读取。",
                        }
                    },
                    "required": ["candidate_index"],
                },
            },
        },
    ]

    if include_stack:
        schemas += [
            {
                "type": "function",
                "function": {
                    "name": "push",
                    "description": (
                        "【遇到开括号或开标签时必须立即调用】将其压入嵌套栈。"
                        "适用于 { ( [ 以及 HTML 开标签（如 <div>）。"
                        "返回压入后的当前嵌套深度，depth=0 表示顶级作用域。"
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "token": {
                                "type": "string",
                                "description": "压入的开括号或开标签，例如 '{' 或 '<section>'。",
                            }
                        },
                        "required": ["token"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "pop",
                    "description": (
                        "【遇到闭括号或闭标签时必须立即调用】弹出嵌套栈顶元素。"
                        "适用于 } ) ] 以及 HTML 闭标签（如 </div>）。"
                        "返回被弹出的 token 和弹出后的深度。栈为空时返回错误，不得忽略。"
                    ),
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_depth",
                    "description": (
                        "查询当前嵌套深度和栈顶元素。depth=0 表示顶级作用域。"
                        "判断某个 def 是否为顶级函数前，必须先确认 depth=0。"
                    ),
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "peek_stack",
                    "description": "查看嵌套栈顶元素但不弹出，用于确认当前所在语法结构。",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
        ]

    if include_record:
        schemas += [
            {
                "type": "function",
                "function": {
                    "name": "record",
                    "description": (
                        "【发现符合任务要求的条目时必须立即调用】将条目持久化保存到结果列表。"
                        "严禁在文字回复中描述发现，所有发现必须通过此工具记录，否则最终结果将丢失。"
                        "严禁记录未实际读到的内容。"
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item": {
                                "type": "string",
                                "description": "发现的条目内容，如函数名或标题文字。",
                            },
                            "category": {
                                "type": "string",
                                "description": "条目类型，如 'function'、'h1'、'h2' 等。",
                            },
                        },
                        "required": ["item", "category"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_records",
                    "description": (
                        "【advance_past 或 confirm_advance 返回 done=true 后必须立即调用】"
                        "获取所有已记录的发现，作为最终答案输出。调用后停止所有操作。"
                    ),
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
        ]

    if include_analyze:
        schemas.append({
            "type": "function",
            "function": {
                "name": "analyze_line",
                "description": (
                    "【对可疑行调用】将一行内容交给分析器判断是否符合任务要求。"
                    "返回 is_target=true 时，按 action 字段的指示调用 record()。"
                    "返回 is_target=false 时，跳过该行。"
                    "对 read_next 返回的每一行都应调用此工具。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "要分析的行内容（从 read_next 返回的 lines 中读取）。",
                        }
                    },
                    "required": ["content"],
                },
            },
        })

    return schemas
