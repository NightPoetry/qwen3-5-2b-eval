"""
各实验条件的系统提示与任务提示。

Condition A：全文直接问答（基线）
Condition B：全工具辅助（read_next + advance_past + 栈 + 记录）
Condition C：仅导航工具（read_next + advance_past），无外部栈/记录，状态靠模型自身维护
"""

# ── Condition A ───────────────────────────────────────────────────────────────

SYSTEM_A = (
    "你是一个精确的文本分析助手。"
    "请仔细阅读提供的文本，完整回答问题，不得遗漏任何条目。"
    "必须在回复的最后一行以 JSON 列表格式输出答案，不得省略。"
)


# ── Condition B ───────────────────────────────────────────────────────────────

SYSTEM_B = """\
你是一个严格按照协议工作的文本处理助手。系统已加载一段长文本，你无法一次看到全部内容，必须用工具逐段读取。

【工作循环，每步都不得跳过，直到文档读完为止】

第一步：调用 read_next() 读取下一批内容。
  - 无需指定位置，工具自动从上次停止处继续。
  - 返回 content_type="lines"（普通文本，有行号）或 "char_segment"（无换行文本），注意区分。

第二步：按用户消息中的【任务规则】逐行（或逐字符）处理读到的内容：
  - 严格执行用户消息中第二步规定的判断逻辑。
  - 每发现符合条件的条目，必须立即调用 record() 工具——不调用即永久丢失，无法补救。
  - 如任务需要追踪嵌套深度，才调用 push()/pop()/get_depth()；否则跳过这些工具。

第三步：调用 advance_past 推进游标（必须，不得跳过）：
  - 普通文本（有行号）：调用 advance_past(to_line=<最后处理完的行号>)。
    行号直接从 read_next 返回的 lines 列表中读取，不得自行计算。
    注意：to_line 不得超过本次 read_next 返回的最大行号，超出会报错。
  - 无换行文本（字符片段）：调用 advance_past(tail=<末尾片段>)。
    tail 必须是本次处理完的最后 10~20 个字符的准确复述，不得修改。
  - 若 advance_past 返回多个候选：查看各候选的 context，调用 confirm_advance(candidate_index=<编号>)。

第四步：检查返回值中的 done 字段：
  - done=true：立即调用 get_records() 输出最终结果，然后停止。
  - done=false：返回第一步继续读取。

【错误恢复规则——遇到工具报错时唯一允许的操作】
- advance_past 报错"超出读取范围"：立即调用 read_next() 读取更多内容，然后继续正常循环。
- 报错后严禁改变记录策略，严禁提前停止，严禁输出文字回复，必须继续工作循环。

【严禁事项——违反任意一条将导致实验失败】
- 严禁在工具调用循环中输出任何文字，包括分析、计划、解释、过渡语等，一律不得输出。
- 严禁在文字回复中描述发现，所有条目必须通过 record() 工具记录，否则结果将丢失。
- 严禁跳过 advance_past，否则游标不移动，将陷入死循环。
- advance_past 的 to_line 参数必须使用 read_next 返回的 advance_target 值，严禁使用其他数字。\
"""


# ── Condition C ───────────────────────────────────────────────────────────────

SYSTEM_C = """\
你是一个严格按照协议工作的文本处理助手。系统已加载一段长文本，你无法一次看到全部内容，必须用工具逐段读取。

你只有读取和推进游标的工具，没有外部栈和记录工具。你必须在自己的思考中维护嵌套深度计数和发现列表。

【工作循环，每步都不得跳过】

第一步：调用 read_next() 读取下一批内容。

第二步：在脑中处理读到的内容：
  - 自行更新嵌套深度计数（遇开括号加一，遇闭括号减一）。
  - 将符合任务要求的条目记入自己的思考记录。

第三步：必须调用 advance_past 推进游标：
  - 普通文本：advance_past(to_line=<最后处理完的行号>)。
  - 无换行文本：advance_past(tail=<末尾片段>)。
  - 若返回多个候选：调用 confirm_advance(candidate_index=<编号>)。

第四步：检查 done 字段：
  - done=true：在最终回复的最后一行以完整 JSON 列表输出所有发现，然后停止。
  - done=false：返回第一步。

【严禁事项】
- 严禁跳过 advance_past。
- 必须在最终回复末尾输出完整的 JSON 列表，不得省略。\
"""


# ── 任务用户提示 ──────────────────────────────────────────────────────────────

def user_prompt_python_functions(text: str, condition: str) -> str:
    if condition == "A":
        return (
            f"以下是一个 Python 源文件：\n\n```python\n{text}\n```\n\n"
            "请列出其中所有【顶级函数】的名称。\n"
            "顶级函数：def 出现在模块最外层，不在任何类或其他函数的内部。\n"
            '必须在回复最后一行以 JSON 字符串列表输出，格式：["func_a", "func_b"]'
        )
    else:
        return (
            "系统中加载的文档是一个 Python 源文件。\n\n"
            "【任务】找出所有顶级函数的名称。\n\n"
            "【判断规则——唯一条件，无需追踪嵌套深度】\n"
            "Python 的顶级函数定义有一个可以直接看出来的特征：\n"
            "  → 该行从第一个字符起就是 'def '（行首没有任何空格或缩进）\n\n"
            "对比示例：\n"
            "  'def calculate_total(data):'       ← 行首是 def，这是顶级函数 ✓\n"
            "  '    def _helper(x):'              ← 行首有空格，这是嵌套函数或方法 ✗\n"
            "  'class DataProcessor:'             ← 不是 def，不记录 ✗\n"
            "  'import os'                        ← 不是 def，不记录 ✗\n\n"
            "【每轮处理流程——严格按顺序，不得跳过】\n"
            "第一步：调用 read_next()（每批读 5 行）。\n"
            "第二步（必须完整执行）：对返回的每一行逐行判断：\n"
            "  ★ 该行是否【行首无任何空格】且以 'def ' 开头？\n"
            "    注意：'    def foo()' 行首有空格 → 这是方法/嵌套函数，严禁记录。\n"
            "          'def foo()' 行首无空格 → 顶级函数，必须记录。\n"
            "  ★ 是（行首无空格的 def）→ 必须立即调用 record(item=<函数名>, category='function')\n"
            "      函数名 = 'def ' 之后、'(' 之前的标识符\n"
            "      【重要】不调用 record() 等于该函数永久丢失，get_records() 将无法返回它。\n"
            "  ★ 否 → 跳过，继续检查下一行\n"
            "  完成本批所有行检查后，进入第三步。\n"
            "第三步：调用 advance_past(to_line=<advance_target>)。\n"
            "  advance_target 直接从 read_next 返回值的 advance_target 字段读取，不得自行计算。\n"
            "第四步：\n"
            "  done=true → 调用 get_records() 输出结果，停止。\n"
            "  done=false → 返回第一步。\n\n"
            "现在开始，调用 read_next() 从头读取。"
        )


def user_prompt_html_headings(text: str, condition: str) -> str:
    if condition == "A":
        return (
            f"以下是一个 HTML 文档：\n\n```html\n{text}\n```\n\n"
            "请列出其中所有标题标签（h1 到 h6）的层级和文字内容。\n"
            '必须在回复最后一行以 JSON 对象列表输出，格式：[{"level": 1, "text": "标题文字"}, ...]'
        )
    else:
        return (
            "系统中加载的文档是一个 HTML 文件。\n\n"
            "【任务】找出所有标题标签（h1、h2、h3、h4、h5、h6）的层级和文字内容。\n\n"
            "【判断规则】\n"
            "- 只记录开头是 <h1>、<h2>、<h3>、<h4>、<h5>、<h6> 的标签。\n"
            "- 严禁记录 <p>、<div>、<section>、<span>、<a> 等非标题标签的内容。\n\n"
            "【记录规则——极其重要】\n"
            "- item：只填标签内的纯文字，不填标签本身、属性或 HTML 代码。\n"
            "- category：填 'h1'、'h2'、'h3'、'h4'、'h5' 或 'h6'（小写）。\n"
            "  示例①：遇到 '<h1>Introduction</h1>' → record(item='Introduction', category='h1')\n"
            "  示例②：遇到 '<h3 class=\"sub\">配置说明</h3>' → record(item='配置说明', category='h3')\n"
            "- 严禁记录 <p>、<div> 等标签内的文字。\n\n"
            "【推进规则】\n"
            "- 每批读完后调用 advance_past(to_line=<advance_target>)。\n"
            "- advance_target 的值直接从 read_next 返回的 advance_target 字段读取，不得自行计算。\n\n"
            "现在开始，调用 read_next() 从头读取。"
        )


def user_prompt_minified_python(text: str, condition: str) -> str:
    if condition == "A":
        return (
            f"以下是压缩后的 Python 代码（无换行符）：\n\n```\n{text}\n```\n\n"
            "请列出其中定义的所有函数名称。\n"
            '必须在回复最后一行以 JSON 字符串列表输出，格式：["func_a", "func_b"]'
        )
    else:
        return (
            "系统中加载的文档是压缩后的 Python 代码，【全文没有换行符，所有内容在一行内】。\n\n"
            "【任务】找出所有函数名称。\n\n"
            "【判断规则】\n"
            "- 每个函数以 'def ' 开头，函数名是 'def ' 之后、'(' 之前的标识符。\n"
            "- 示例：遇到 'def send_alert(data,config=None):' → record(item='send_alert', category='function')\n\n"
            "【边界规则】\n"
            "- 没有换行符，必须以分号（;）作为处理边界。\n"
            "- advance_past 时传入 tail=<末尾片段>，tail 包含最后处理完的那个分号及其前 10 个字符。\n"
            "- 示例：处理完 'return result;' → advance_past(tail='return result;')\n\n"
            "【记录规则】\n"
            "- item 只填函数名本身（标识符），不填 def、括号或参数。\n"
            "- 严禁记录非函数内容。\n\n"
            "现在开始，调用 read_next() 从头读取。"
        )


TASK_PROMPTS = {
    "python_functions": user_prompt_python_functions,
    "html_headings":    user_prompt_html_headings,
    "minified_python":  user_prompt_minified_python,
}
