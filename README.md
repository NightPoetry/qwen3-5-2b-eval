# Qwen3.5 2B 能力测试

本项目通过一系列脚本评估 Qwen3.5 2B 在以下维度的能力：长上下文检索、推理链效果、Function Calling 触发率及工具描述质量。

完整测试报告见 [`report/README.md`](report/README.md) 和 [`report/index.html`](report/index.html)。

---

## 环境准备

**依赖：**
```bash
pip install requests
```

**模型服务：** 使用 [LM Studio](https://lmstudio.ai/) 加载 `qwen3.5-2b`，并在 `Local Server` 标签页启动服务（默认端口 `1234`）。

---

## 配置

所有脚本通过环境变量 `LM_STUDIO_URL` 指定 API 地址，**默认值为本机 `localhost:1234`**，本机运行无需任何配置。

| 场景 | 操作 |
|---|---|
| LM Studio 与脚本在同一台机器 | 无需设置，直接运行 |
| LM Studio 在局域网另一台机器 | 设置 `LM_STUDIO_URL` 环境变量（见下方示例） |

**Linux / macOS：**
```bash
export LM_STUDIO_URL="http://<服务器IP>:1234/v1/chat/completions"
```

**Windows PowerShell：**
```powershell
$env:LM_STUDIO_URL = "http://<服务器IP>:1234/v1/chat/completions"
```

> 如需持久化，可将 `export` 语句写入 `~/.zshrc` 或 `~/.bashrc`。

---

## 运行实验

```bash
# 实验一：大海捞针（长上下文检索）
python needle_in_haystack.py

# 实验二：推理检索（规则隐藏在长文本中）
python reasoning_retrieval.py

# 实验三A：高级长上下文推理
python advanced_test.py

# 实验三B：Function Calling 多轮闭环
python function_call_loop.py

# 实验四：工具描述质量对比
python tool_description_test.py
```

---

## 文件结构

```
├── needle_in_haystack.py      — 实验一：大海捞针
├── reasoning_retrieval.py     — 实验二：推理检索
├── advanced_test.py           — 实验三A：复杂推理
├── function_call_loop.py      — 实验三B：Function Calling 闭环
├── tool_description_test.py   — 实验四：工具描述质量对比
└── report/
    ├── README.md              — 详细实验说明与结果
    ├── index.html             — 可视化 HTML 报告
    ├── data/
    │   └── new_results.json   — 实验四完整原始数据
    └── scripts/
        └── full_test.py       — 实验四完整版（800次 API 调用）
```
