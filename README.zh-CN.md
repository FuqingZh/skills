# FuqingZh/skills

[English](README.md) | 简体中文

面向 Codex、Grok Build 和 Pi 的可移植工程技能与全局代理指令。
具体工作遵循所在仓库的契约和上游标准；calibration 提供跨项目的判断与安全边界。
仓库原名为 `FuqingZh/calibration`，`calibration` 技能名及其私有配置命名空间不变。

## 快速开始

通过工具管理器安装 [skills CLI](https://github.com/vercel-labs/skills)，
例如在 mise 中声明 `"npm:skills" = "latest"`。然后安装四个第一方技能：

```bash
skills add FuqingZh/skills -g -a codex pi grok -y
```

全局指令安装器需要 Linux/WSL 上的 Bash 和 GNU 工具；
尚未验证 macOS 和原生 Windows 的安装。
全局指令须从可信 checkout 单独、显式安装：

```bash
git clone https://github.com/FuqingZh/skills.git
cd skills
./install.sh --agent all --dry-run
./install.sh --agent all
```

已有安装请先阅读[旧安装迁移](#旧安装迁移)。只选择实际使用的客户端；
`-a codex pi` 中的名称用空格分隔。
Codex 和 Pi 直接发现 `~/.agents/skills`，Grok 使用发现链接。
其他扫描共享目录的客户端也可能看到这些技能，客户端选择不构成隔离边界。

## 包含的技能

| 技能 | 用途 | 调用方式 |
| --- | --- | --- |
| [calibration](skills/calibration/SKILL.md) | 工程判断与参考资料路由 | 相关时使用 |
| [writing-code-docs](skills/writing-code-docs/SKILL.md) | 公共 API 与维护者文档 | 相关时使用 |
| [closeout](skills/closeout/SKILL.md) | 对话回顾与未完成事项梳理 | 仅显式调用 |
| [retrospect](skills/retrospect/SKILL.md) | 从证据提炼可复用经验 | 仅显式调用 |

曾经修改过的 `teach`、`grilling` 副本已[归档](thirdparty/archive/README.md)，
保留来源、许可证和历史评估；个人学习数据不在迁移范围内。
如需使用未经修改的上游 grilling，单独安装：

```bash
skills add mattpocock/skills --skill grilling -g -a codex pi grok -y
```

这会跟随 Matt 的默认分支，接受上游的交互与调用策略，
包括按依赖前沿分批提问和对子代理的假设；不包含 calibration 以前的补丁。

## 技能维护与版本

使用上游的 `skills list -g`、`skills update -g` 和 `skills remove` 管理技能。
执行破坏性操作前先阅读当前版本的命令帮助。重复 add 可能覆盖本地编辑，
remove 可能删除同名共享内容。setup 负责接入原生全局锁，恢复和更新仍显式执行；
本仓库不维护第二套锁文件。

已验证的 skills CLI 1.7.6 使用 `FuqingZh/skills#<tag-or-full-sha>` 固定来源。
update 跟随已记录的 ref；切换发行版或回滚需要对目标 ref 显式执行 add。
CLI 版本与技能来源版本分别管理。全局指令只在从选定 checkout
重新运行 `install.sh` 时更新。
参见[发布规则](docs/releases.md)与[变更记录](CHANGELOG.md)；
计划中的 `v1.0.0` tag 尚未发布。

## 全局指令

可执行入口为 `./install.sh`，也可运行 `bash install.sh`。
支持四个选项：`--agent`、`--dry-run`、`--force`、`--help`（或 `-h`）。
默认客户端是 Codex，不需要额外的包或全局 CLI 包装器。

高级布局和隔离测试通过绝对路径环境变量指定目录：

| 客户端 | Home 环境变量 | 未设置或为空时的默认值 |
| --- | --- | --- |
| Codex | `CODEX_HOME` | `~/.codex` |
| Grok Build | `CALIBRATION_GROK_HOME` | `~/.grok` |
| Pi | `PI_CODING_AGENT_DIR` | `~/.pi/agent` |

`CALIBRATION_GROK_HOME` 只配置本仓库脚本，不配置 Grok 或 skills CLI。
例如：`CODEX_HOME=/absolute/test-home ./install.sh --dry-run`。

安装器管理各目标 `AGENTS.md` 中由 `<!-- FuqingZh/skills:begin -->` 与
`<!-- FuqingZh/skills:end -->` 包围的区块，保留有效区块以外的文字。
它先预检所有目标，对需要修改的已有文件始终创建备份，并支持重复执行。
Dry-run 不写入。文件不存在时创建新区块；Pi 和 Grok 的无标记普通文件追加区块。
已有的无标记 Codex 普通文件需要显式 force 和核验备份后才能替换。
符号链接目标、目录、错误或重复标记、不安全或重叠的目标目录都会被拒绝。

有效的旧 `calibration:begin/end` 区块无需 force 即可备份并迁移。
混用命名空间或首尾标记不匹配时，即使 force 也会在写入前失败；
dry-run 会指出计划中的标记迁移。

模板会把私有主机规则指针渲染为绝对路径：
`$XDG_CONFIG_HOME/calibration/AGENTS.md` 或
`$HOME/.config/calibration/AGENTS.md`，但不会创建该私有文件。
Pi 和 Grok 的指令中，`$calibration` 调用写法会渲染为 `calibration`。
客户端能发现资源，不代表模型一定遵循其中的指令。

## 旧安装迁移

旧技能链接和无标记 Codex 文件的处理见[迁移指南](docs/migrations/skills-cli.md)。
清理是独立迁移操作，正常安装不会删除技能；已移除的选项会明确报错。

## 开发与验证

使用 Python 3.12+ 和 PDM 安装锁定的验证环境：

```bash
pdm sync --clean
pdm lock --check
pdm run check
```

完整检查包含 Ruff、Pyright、rumdl、Markdown 链接、ShellCheck、pytest 和技能验证。
仓库自有 Python 工具要求 100% 行覆盖率。
Ruff 使用显式稳定规则集 `E`、`F`、`I`、`UP`、`B`、`SIM`、`RUF`，不启用预览规则。
安装器的局部修改可先运行：

```bash
pdm run lint-shell
pdm run test tests/test_install.py
pdm run validate-skills
```

安装器测试使用隔离配置目录。按变更影响选择验证范围；
[AGENTS.md](AGENTS.md) 规定贡献与验证要求。

## 文档与支持

- [文档索引](docs/README.md)：现行决策、评估结果、迁移历史和实施计划。
- [工程原则](skills/calibration/references/principles.md)与
  [技能路由](skills/calibration/SKILL.md)：按任务选择参考资料。
- [skills CLI 分发决策](docs/decisions/2026-11-08-skills-cli-distribution.md)：
  当前所有权、全局指令安装与标记迁移。
- [早期多客户端安装](docs/decisions/2026-09-24-multi-client-skill-installation.md)：
  历史安装与原生资源发现证据。
- [Issues](https://github.com/FuqingZh/skills/issues)：问题与改进建议。
  报告安装问题时，请附客户端版本、命令及脱敏后的相关输出。

行为提示和评估只支持其记录条件内的结论。技能可被发现、静态检查通过，
均不代表各客户端行为相同，也不代表模型性能得到普遍提升。
