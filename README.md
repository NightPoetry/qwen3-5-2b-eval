# Qwen3.5 2B 能力评估与可执行知识网络

本项目包含两个相互关联的研究方向：

1. **能力评估**：通过标准化实验评估 Qwen3.5 2B 的基础能力（长上下文、推理、Function Calling、工具描述）
2. **可执行知识网络**：验证"小模型 + 工具增强"的核心论点——通过 164 个可执行节点组成的知识网络，让 2B 模型完成远超其裸能力的任务

**核心论点**：传统知识图谱是被动数据（存储事实，等待查询），可执行知识网络是主动程序（每个节点 = 一个带触发条件的工具，自动激活、自动链式执行）。

---

## 硬件环境

| 项目 | 配置 |
|------|------|
| 开发机 | MacBook Pro (M4 Max, 48GB) |
| 推理服务 | LM Studio，本地部署 |
| 模型 | Qwen3.5-2B (Q4_K_M 量化) |
| API | OpenAI 兼容接口，端口 1234 |

## 快速开始

```bash
pip install requests flask

# 启动 LM Studio 并加载 qwen3.5-2b，开启 Local Server (端口 1234)

# 运行知识网络 Web 界面
cd dev_network/v2/web
python app.py
# 浏览器打开 http://localhost:5001/graph 查看 3D 可视化
```

如果 LM Studio 在另一台机器上：
```bash
export LLM_API_URL="http://<IP>:1234/v1/chat/completions"
```

---

## 项目结构

```
├── README.md
├── LICENSE
│
├── exp1_capability_eval/             — 实验一~四：基础能力评估
│   ├── needle_in_haystack.py         — 大海捞针（长上下文检索）
│   ├── reasoning_retrieval.py        — 推理检索
│   ├── advanced_test.py              — 复杂推理
│   ├── function_call_loop.py         — Function Calling 闭环
│   ├── tool_description_test.py      — 工具描述质量对比
│   └── report/                       — 可视化报告 + 原始数据
│
├── exp2_complex_extraction/          — 实验五：复杂信息提取（工具增强）
│   ├── runner.py                     — 27-case 批量测试器
│   └── test_*.py                     — 各策略对比测试
│
├── exp3_27b/                         — 实验六：27B 模型对比（已暂停）
│
└── dev_network/                      — 可执行知识网络
    ├── v1/                           — v1 原型（已归档）
    ├── v2/                           — v2 正式版
    │   ├── engine.py                 — 执行引擎（栈展开 + 三级光标续入）
    │   ├── llm.py                    — LLM 调用（隔离对话，环境变量配置）
    │   ├── nodes/                    — 164 个可执行节点
    │   ├── web/                      — Flask 后端 + Three.js 3D 可视化
    │   ├── scripts/                  — 测试与运行脚本
    │   └── _archive/                 — 历史备份
    └── 交接文档/                      — 开发过程记录
```

---

## 知识网络架构

### 执行模型

```
用户输入 → 000(入口) → 域路由(A00/B00/C00/D00) → 专业节点链 → 输出(Y10/Y20/Y30/Y40)
                                    ↑                                      |
                                    └──── 光标续入（三级：工作节点→域→全局）────┘
```

### 节点统计

| 类别 | 数量 | 说明 |
|------|------|------|
| 核心管线 | 10 | 交互设计→代码生成→验证 |
| 质量精炼 | 21 | CSS/JS/HTML 检查 + 交互规则 |
| 推理认知 | 12 | 结构主义方法 + 词义消歧 + 事实校准 |
| 安全监控 | 12 | 风险分级 + 不可逆检测 + 资源预算 |
| 元方法论 | 18 | 超参消除 + 自举学习 + 双轨思考 |
| 技能 | 6 | 蒸馏 + 翻译 + UI 设计 |
| 对话 | 11 | 闲聊 + 情感 + 记忆检索 |
| 角色 | 9 | UI 设计师 / 嵌入式工程师 / 翻译官 等 |
| 设计模式 | 8 | AI 架构 / 渲染管线 / 工具 UX |
| 通用原则 | 14 | 理论纯净性 / 最优路径 / 防御布局 |
| 扩展领域 | 22 | 游戏引擎 / 视频编辑 / Git 工作流 |
| 自蒸馏管线 | 13 | 知识获取→分类→脱敏→代码合成→质量门 |
| 基础设施 | 8 | 入口 + 域路由 + 输出锚点 |
| **总计** | **164** | |

### 关键设计原则

1. **2B 单线程**：每个 LLM 调用只问一个简单问题
2. **LLM 判断，不用正则**：语义决策必须由模型做，正则仅用于代码格式解析
3. **触发宁严勿宽**：误触发（注入噪声）比漏触发（没帮上忙）更糟
4. **可执行 > 被动知识**：每个节点 = trigger + execute + refs，不是存储事实的文档

### 对话连贯性

引擎实现三级续入机制：
1. **工作节点续入**：从上轮非输出节点的邻接匹配（keyword 优先于 regex）
2. **域续入**：上轮在推理域，这轮默认从推理域继续
3. **全局回退**：前两级失败，回到入口节点（话题切换）

关键事实（`_reasoning`、`_design_guidance` 等）跨轮持久化在 session 中。

### 记忆检索

880 节点实现 bigram 字符级检索 + 指针缓存 + 概括记忆 + 渐进降级，不依赖 embedding 模型。

---

## 实验复现

### 能力评估实验（实验一~四）

```bash
cd exp1_capability_eval
python needle_in_haystack.py
python reasoning_retrieval.py
python advanced_test.py
python function_call_loop.py
python tool_description_test.py
```

### 复杂提取实验（实验五）

```bash
cd exp2_complex_extraction
python runner.py          # 27-case 全量测试
python test_single_line.py  # 单策略对比
```

### 知识网络 Web 界面

```bash
cd dev_network/v2/web
python app.py
# http://localhost:5001       — 聊天界面
# http://localhost:5001/graph — 3D 知识图谱可视化
```

---

## 许可

MIT License. 详见 [LICENSE](LICENSE)。
