"""
27B 实验配置。
"""

API_URL    = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "qwen3.6-27b"

# 并发工作线程数（27B 服务器算力强，可开大）
MAX_WORKERS = 8

# 单次请求超时（秒）
REQUEST_TIMEOUT = 300

# 最大输出 token 数（27B 带 thinking 模式，需要比 2B 大得多）
MAX_TOKENS = 8192

# 工具调用循环最大轮数（27B 文档更长，需要更多轮）
MAX_ROUNDS = 150

# 对话历史滑动窗口（保留最近 N 轮，防止 context 溢出；0=保留全部）
HISTORY_WINDOW = 20
