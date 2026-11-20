# FuqingZh/skills

[English](README.md) | 简体中文

提供工程判断、代码文档、平实表达和深入分析技能。共享指令安装器支持 Codex、
Grok Build、Pi 和 Antigravity CLI。

## 包含的技能

| 技能 | 用途 | 调用方式 |
| --- | --- | --- |
| [calibration](skills/calibration/SKILL.md) | 工程判断与参考资料路由 | 相关时使用 |
| [writing-code-docs](skills/writing-code-docs/SKILL.md) | 公共 API 与维护者文档 | 相关时使用 |
| [plainspoken](skills/plainspoken/SKILL.md) | 平实直述，保留有用的解释与细节 | 实质性自然语言回答 |
| [dissect](skills/dissect/SKILL.md) | 基于证据解释机制、推演行动与后果 | 深入分析 |
| [closeout](skills/closeout/SKILL.md) | 对话回顾与未完成事项梳理 | 仅显式调用 |
| [retrospect](skills/retrospect/SKILL.md) | 从证据提炼可复用经验 | 仅显式调用 |

## 快速开始

### 安装技能

通过工具管理器安装 [skills CLI](https://github.com/vercel-labs/skills)，再运行以下命令。
只选择实际使用的客户端；示例选择 Codex、Pi 和 Grok Build。

```bash
skills add FuqingZh/skills -g -a codex pi grok -y
```

已有安装请先阅读[迁移指南](docs/migrations/v2.md)，并在覆盖前检查本地技能修改。

### 全局指令

安装技能后，从可信 checkout 单独安装共享路由指令。
此安装器需要 Linux/WSL 上的 Bash 和 GNU 工具；尚未验证 macOS 和原生 Windows 的安装。

```bash
git clone https://github.com/FuqingZh/skills.git
cd skills
./install.sh --agent all --dry-run
./install.sh --agent all
```

先检查预览结果，再执行安装。`install.sh` 只管理共享指令区块。仅更新 Antigravity CLI 时，
运行 `./install.sh --agent agy`；它管理 `~/.gemini/AGENTS.md`，
不安装技能。客户端选择、自定义目录和备份行为见[安装参考](docs/installation.md)。

已有 mise 时，可以改用带补全的任务入口。先确认此 checkout 的 [`mise.toml`](mise.toml)
内容可信，然后在仓库根目录运行：

```sh
mise trust ./mise.toml
mise run install agy --dry-run
```

信任配置后，mise 才会启用这个任务；启用 mise 的 shell 补全后，按 Tab 可选客户端和选项。
如果不想信任 mise 配置，仍可直接运行 `./install.sh`。

## 进一步阅读

- [安装参考](docs/installation.md)：客户端发现、安装器选项与安全边界。
- [升级到 v2](docs/migrations/v2.md) · [旧安装迁移](docs/migrations/skills-cli.md)。
- [版本与发布](docs/releases.md) · [变更记录](CHANGELOG.md)。
- [开发与验证](AGENTS.md#validation)。
- [测试结果汇总](docs/testing/20261117-v2.0-release-evidence-summary.md)：材料精简、人评结果与未验证范围。
- [文档索引](docs/README.md)：现行指导与历史记录。
- [问题反馈](https://github.com/FuqingZh/skills/issues)：请附客户端版本、命令及脱敏后的相关输出。
