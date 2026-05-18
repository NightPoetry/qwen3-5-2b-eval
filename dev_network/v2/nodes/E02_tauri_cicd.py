"""知识节点：Tauri跨平台CI/CD——GitHub Actions打包/常见CI错误。

融合：GitHub Actions CI常见错误 + 跨平台打包方案 + Tauri插件集成
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

CICD_KNOWLEDGE = """你是Tauri CI/CD专家。根据以下知识诊断打包和部署问题。

## Tauri三平台打包方案
- 推送tag(v*)触发workflow，strategy.matrix三平台并行构建
- macOS: --target universal-apple-darwin + rustup target add aarch64+x86_64
- Linux: ubuntu-22.04 + libwebkit2gtk-4.1-dev等依赖
- Windows: --bundles nsis（避免WiX对非ASCII productName的缺陷）
- permissions: contents:write（否则创建Release报权限不足）

## CI常见错误速查
| 关键词 | 原因 | 修复 |
|-------|------|------|
| dtolnay下载失败 | GitHub API不稳定 | 删除该步骤，Runner预装Rust |
| tauriScript双build | Action自动追加build | tauriScript填npx @tauri-apps/cli |
| Node.js 20废弃 | 版本过旧 | setup-node用node-version:24 |
| 找不到.ico | tauri.conf.json未引用图标 | bundle.icon数组补齐所有格式 |
| Resource not accessible | GITHUB_TOKEN只读 | 加permissions:contents:write |
| WiX light.exe失败 | 非ASCII路径缺陷 | 改用--bundles nsis |
| cargo tauri找不到 | Android job未装CLI | cargo install tauri-cli --version "^2" |

## 插件集成四步法
1. Cargo.toml添加Rust依赖 2. lib.rs调用.plugin(init())
3. npm install前端包 4. capabilities添加权限
缺一步都会出不同的错误（找不到module/plugin not found/not allowed）

## 权限配置
- capabilities/default.json中remote.urls匹配开发URL(http://localhost:*)
- local:true用于生产模式
- 触发错误法发现可用权限：填一个不存在的权限名→cargo build报错列出所有可用

## Tauri v2 API变更
- invoke路径从__TAURI__.invoke()改为__TAURI__.core.invoke()
- import从'@tauri-apps/api/tauri'改为'@tauri-apps/api/core'
- infoPlist不接受inline object→写独立plist文件+路径引用
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        CICD_KNOWLEDGE +
        "\n分析以下任务涉及的Tauri CI/CD问题，给出具体建议（每条一行，不超过4条）。"
        "如果不涉及此类问题，回答'无CI/CD问题'。",
        f"任务：{task[:500]}",
        max_tokens=250
    ).strip()
    if "无CI/CD问题" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx

node = Node(id="E02", name="Tauri CI/CD",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["CI", "CD", "GitHub Actions", "workflow", "打包",
                          "build", "release", "跨平台", "universal",
                          "tauri-action", "bundle", "插件集成", "plugin",
                          "capabilities", "权限配置"]},
    execute=execute, refs=["170"],
    metadata={"source": "Guild/开发工具与工作流/Tauri开发指南+GitHub Actions", "category": "domain_dev_tools"})
