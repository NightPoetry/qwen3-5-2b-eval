# Qwen3.5 2B 能力测试报告

## 环境配置

| 项目 | 配置 |
|---|---|
| 模型 | qwen3.5-2b |
| 运行平台 | LM Studio 0.4.12 Build1 |
| 温度 | 0.1（默认配置） |
| API 格式 | OpenAI-compatible |
| API 端点 | 由环境变量 `LM_STUDIO_URL` 指定（默认 `http://localhost:1234/v1/chat/completions`） |
| Python 依赖 | `requests`（标准库 urllib 有 Expect 头兼容问题） |
| 测试日期 | 2026-05-16 |

---

## 快速开始

### 安装依赖

```bash
pip install requests
```

### 配置 LM Studio 地址

所有脚本通过环境变量 `LM_STUDIO_URL` 读取 API 端点，默认值为 `http://localhost:1234/v1/chat/completions`。

**本机运行（LM Studio 在同一台机器）：**
```bash
# 使用默认值，无需额外设置
python scripts/needle_in_haystack.py
```

**远程服务器（LM Studio 在另一台机器）：**
```bash
# Linux / macOS
export LM_STUDIO_URL="http://<服务器IP>:1234/v1/chat/completions"
python scripts/needle_in_haystack.py

# Windows PowerShell
$env:LM_STUDIO_URL="http://<服务器IP>:1234/v1/chat/completions"
python scripts\needle_in_haystack.py
```

> LM Studio 默认监听端口为 `1234`，确保防火墙已放行该端口，且 LM Studio 已加载 `qwen3.5-2b` 模型。

---

## 实验一：大海捞针

**脚本：** `scripts/needle_in_haystack.py`

**目标：** 将隐藏词 `BLUEBERRY` 放在约 2000 词填充文本的不同位置，测试模型能否找到。

**配置：**
- 填充词数：~2000
- 测试位置：10% / 25% / 50% / 75% / 90%
- 推理模式：`/no_think`（关闭推理链）
- max_tokens：50

**结果：** 5/5（100%）

**运行：**
```bash
python scripts/needle_in_haystack.py
```

**注意事项：**
- 使用 `requests` 库而非 `urllib`，后者发送 `Expect: 100-continue` 头，导致 LM Studio 返回 502 Bad Gateway。

---

## 实验二：长上下文推理检索

**脚本：** `scripts/reasoning_retrieval.py`

**目标：** 在文中定义规则（如"文中唯一质数"），模型需推理出哪个词满足条件。规则与答案词位于不同位置。

**配置：**
- 填充词数：~2000
- 测试 5 个场景，规则与答案分布在 10%~90% 不同位置
- 对比：关闭推理链（`/no_think`）vs 开启推理链（step-by-step CoT）
- max_tokens：2048（推理链版本）

**结果：**

| 模式 | 得分 |
|---|---|
| 无推理链 | 2/5（40%） |
| 推理链（step-by-step） | 5/5（100%） |

**关键发现：**
- Qwen3.5 2B 的推理内联在 `content` 字段，`reasoning_content` 始终为空，`reasoning_tokens=0`
- 这是 in-context chain-of-thought，非原生 thinking token
- 推理链需要 `max_tokens` 至少 1024，建议 2048

**运行：**
```bash
python scripts/reasoning_retrieval.py
```

---

## 实验三：高级测试（复杂推理 + Function Calling 闭环）

**脚本：** `scripts/advanced_test.py` / `scripts/function_call_loop.py`

**目标：**
1. 更难的长上下文问题识别（多跳推理、干扰陷阱、嵌套规则、矛盾覆盖）
2. Function Calling 完整多轮闭环

**配置：**
- 填充词数：~2000
- 工具定义：3 个工具（天气、预报、汇率）
- tool_choice：auto
- 并行工具调用：是

**结果：** 7/7（100%）

**Function Calling 闭环流程：**
```
用户提问 → 模型分析 → 并行调用 2 个工具 → 代码执行工具 → 返回结果 → 模型综合回答
```

**运行：**
```bash
python scripts/function_call_loop.py
```

---

## 实验四：工具描述质量对比

**脚本：** `scripts/tool_description_test.py`

**目标：** 相同的 20 道数学题，用 4 种不同工具描述风格，测试模型是否调用工具而非自行计算。

**配置：**
- 题目数量：20 题，分 4 类（A直接算、B一步题、C多步题、D公式题）
- 描述风格：EN-STRONG / CN-WEAK / CN-STRONG / CN-PATCHED
- temperature：0.1，max_tokens：256

**工具描述对比：**

```
EN-STRONG:
  "REQUIRED: You MUST call this tool for ANY arithmetic computation..."

CN-WEAK:
  "一个计算器，可以用来计算数学表达式。"

CN-STRONG:
  "【必须调用】遇到任何数值计算时，必须调用此工具，不得自行心算或推导..."

CN-PATCHED（CN-STRONG + 文字题补丁）:
  在 CN-STRONG 基础上追加：
  "对于需要先理解题意再列算式的文字题，请先在脑中列出算式，
   然后将完整算式作为 expression 传入本工具..."
```

**结果：**

| 风格 | 全部 | A类 | B类 | C类 | D类 |
|---|---|---|---|---|---|
| EN-STRONG | 60% | 100% | 80% | 40% | 20% |
| CN-WEAK | 35% | 80% | 40% | 0% | 20% |
| CN-STRONG | 95% | 100% | 100% | 80% | 100% |
| CN-PATCHED | 95% | 100% | 100% | **100%** | 80% |

**运行：**
```bash
python scripts/tool_description_test.py
```

---

## 核心结论

1. **中文描述触发率显著更高**：相同强度下，中文 95% vs 英文 60%（+58%）
2. **推理链效果极佳**：step-by-step CoT 使复杂推理从 40% → 100%
3. **工具描述 = 模型行为说明书**：描述越精确，行为越可预期
4. **文字题补丁有效**：补充"先列式再调用"说明，C类题从 80% → 100%

---

## 文件结构

```
report/
├── index.html          — 可视化 HTML 报告页面
├── README.md           — 本文件（实验说明）
├── data/
│   └── results.json    — 所有实验原始数据
└── scripts/
    ├── needle_in_haystack.py   — 实验一
    ├── reasoning_retrieval.py  — 实验二
    ├── function_call_loop.py   — 实验三（闭环）
    └── tool_description_test.py — 实验四
```
