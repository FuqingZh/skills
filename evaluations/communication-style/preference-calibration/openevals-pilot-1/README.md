# OpenEvals helpfulness 两组开发小批

当前已在第一组后停止：目标诊断局部命中，但新增缺陷判断的必要性依据不足。
P02 未执行；详见 [结果与限制](results.md)。下列冻结命令用于留存，不是重跑授权。

组件：OpenEvals 提交 `5753dc75d40c2be75ffd38eb6d63bb966cbcc4e3` 的
`RAG_HELPFULNESS_PROMPT` 和 `create_llm_as_judge(output_schema=...)`。
上游提示逐字保留在 `upstream-helpfulness.txt`，MIT 许可另存；本地中文指令只规定
诊断输出格式、逐字引用和不确定状态，不提供人类标签或两例的期待结论。

输入来自 [原始开发题包](../deletion-pilot-1.json)；
[人工反馈](../deletion-pilot-1-feedback.json) 只用于执行后的未盲审阅。
A/B 分别接受同一问题与准则的检查，没有参考答案、总分或自动偏好。
本轮检验具体诊断是否覆盖已知差异，不构成独立验证。

## 冻结与停止

- `protocol.json`：最多两组、四次调用；先 P01-A/B，再由作者核查具体诊断。
- 仅当第一组无结构、执行或实质语义失败，才记录 `review-P01.json` 并进入 P02。
- 一份输出结构失败即停止剩余调用；一组实质误判即停止下一组。禁止重试、修补、
  换序补跑、改提示追分或保留组扩量。
- `manifest.json` 固定脚本、提示、schema、协议、题包及复用的 transport。
  每次执行还需保留冻结提交；冻结后不修改这些文件。
- `results/<case>/*.started.json` 在调用前独占创建，输出及失败随后独占留存。
  目录或记录已存在时拒绝重新执行。

## 接入与验收

包安装在仓库忽略的 `.venv/openevals-probe-5753dc7/env`，未修改项目依赖或全局安装。
安装日志另存于该目录；49 个分发包的实际版本保存在 `preflight.json`。

适配层只把 OpenEvals 的 SDK 形状请求交给已有 `run.py` 的隔离 Pi 调用，不实现新的
评分算法。schema 以文本约束发送，输出再由 OpenEvals 严格 JSON 解析与本地精确字段、
枚举、非空理由和原文引用校验；不是提供方强制 JSON Schema。

每次 Pi 调用使用独立临时 agent 目录，关闭 agent/provider 重试、compaction、cache
warming 和遥测，并固定 SSE。目录只链接既有 auth/models 以使用现有授权，不复制或
记录凭证；不修改全局设置。沿用 no-tools、no-extensions、no-mcp、no-skills、
no-context-files、no-session 等隔离选项。只留存可见最终文本和 usage，不留存 thinking。

OpenEvals 进程禁用 LangSmith tracing，并拦截 socket connect/connect_ex/DNS；Pi 的独立
子进程负责模型请求。进程内拦截不是全系统网络审计。实际 provider HTTP 次数没有
独立服务端计数，只报告可见调用数及重试设置；执行错误未返回用量时成本保持未知。

`preflight.json` 记录八个合成用例：正常发现、空发现、非法 JSON、错误字段、越界引用、
非法类别、空理由、调用失败。各用例假客户端仅一次调用，失败文本保持原样；独占写入
拒绝覆盖；实际加载的上游提示与保存文本相同。无模型调用，执行结束无进程内网络尝试。
隔离 `pi --version` 返回 1.5.0。此前未隔离的 `pi --help` 在 20 秒后超时，不作为通过证据。

只选择本脚本的 Ruff、格式、显式 Pyright、无模型预检以及局部 Markdown/Git 空白检查。
LSP 对脚本未确认 clean，显式 Pyright 为零错误。另一个历史冻结实验 fixture 的
`xlsx_export.py` 类型诊断在本轮按越界问题延后，未修改、抑制或排除它。

## 命令

以下命令只服务这次冻结实验；原始调用记录一旦存在不得重跑。

```bash
PROBE=evaluations/communication-style/preference-calibration/openevals-pilot-1
PY=.venv/openevals-probe-5753dc7/env/bin/python
"$PY" "$PROBE/probe.py" preflight
"$PY" "$PROBE/probe.py" freeze
# 先提交冻结文件；以下两条不能合并为自动连续执行。
"$PY" "$PROBE/probe.py" P01
# 仅在审阅 P01 并保存允许继续的记录之后：
"$PY" "$PROBE/probe.py" P02
```
