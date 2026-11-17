# 第二批组件评审：首次调用执行故障，已停止

人工标注已齐，本批已进入组件判断，不再等待新的确认。沿用第一批冻结在 `88e4947`
的 OpenEvals helpfulness 提示、schema、格式指令、模型与隔离 transport，仅换入
P03/P04 材料；本批执行文件冻结在 `cbd913e`。上限四次调用，每份一次。

## 实际结果

首份 P03-A 在一次 Pi 调用后返回：

```text
Model identity or completion status mismatch
```

该记录没有可用于评审的最终文本、诊断或 usage。P03-B、P04-A/B 均未调用；没有重试、
修补、替换组件或修改提示。第二批目前没有有效诊断，也没有可计算的偏好一致性结果。

这属于执行契约失败，不能解释为组件语义判断错误或某份候选回答更差。旧 transport
同时比较 model、provider、stopReason 与预期 `gpt-6-sol`、`openai`、`stop`，任一不符
都记录同一错误；随后仅保存异常文字，没有保留实际三字段。因此本次不能定位为
模型路由错误、额度耗尽、服务端异常或其他终止原因，也不能靠现有记录恢复评审。

- Pi 评审调用尝试：1；provider HTTP 请求次数未知。
- 调用耗时：3.004 秒，不含准备和检查。
- tokens 与费用：未知，不能填零。
- [失败原始记录](results/P03/A.json) 与 [调用前占位](results/P03/A.started.json) 保留。
- [停止审阅](review-P03.json) 归类为 execution_contract_failure，阻止后续 P04。
- 记录 SHA256：`b2d74f32930c31a3b40a73c3d318c00a46be3c514f9d3312afb8d812b9a1c071`。

## 执行与局部验证

复用第一批已验收的评价函数、逐字引用校验、独占写入和临时 agent 配置。新控制器
只负责绑定第二批材料、顺序、占位及停止。反馈文件仅用于摘要绑定，不进入请求。
模型只接收共同问题、单份回答、原 helpfulness 提示与原格式指令。

执行前的无模型检查确认：Pi 为原来的 1.5.0，依赖版本与原预检一致，原评审文件和
第二批 source hashes 均符合冻结记录。没有新安装或全局设置修改。只对新控制器
执行定向 Ruff、格式、Pyright 以及三个离线测试；测试覆盖成功/失败停止、禁止重跑、
输入标签隔离和 P04 审阅门。全部通过。LSP 没有报告新发现但未确认 clean；显式
Pyright 为零错误。

失败后仅离线核查：输入逐字匹配冻结材料和提示；仅一份 started 记录；没有后续
调用或派生诊断；失败记录及原冻结文件未变。未运行全仓测试。

## 后续边界

下一项需要解决的是安全记录失败时实际的完成元数据，保留 model/provider/stopReason
和必要的脱敏错误信息，同时继续排除 hidden thinking、凭证和原始敏感日志。
这不是改变评审标准的理由；本轮没有修改已冻结 transport 或擅自再试一次。
未来若修复日志并重新试验，需要单独保留新协议、授权和尝试记录，不能覆盖本次失败。

材料与人工标注：
[原题](../deletion-pilot-2.json)、[偏好反馈](../deletion-pilot-2-feedback.json)、
[共有解释的补充判断](../deletion-pilot-2-feedback-supplement-1.json)。
P04 共有解释的“合适”标签保留，没有被作者最初的共有缺陷假设替代。

## 失败日志修复：已离线验证，尚未重试

新增 [diagnostic_transport.py](diagnostic_transport.py)，作为新执行入口显式选用的
适配器。原 runner、协议、manifest 和失败记录均不修改；原入口也不会暗中改变行为。
新入口可在自己的 pilot namespace 中绑定：

```python
base["live"].__globals__["CORE"]["invoke"] = diagnostics["invoke"]
```

绑定本身不发起调用。适配器复用冻结 runner 的进程隔离、终止回收和全部原校验，
仅为失败结果增加 `failure_metadata`：预期与实际的 model/provider/stopReason、
不匹配字段、完成消息数量、错误文本中的 HTTP 状态码和固定错误线索。元数据最多
保留四份完成消息，错误文本最多扫描 8192 字符，不原样保存；非标识符形状、过长
或具有已知凭证前缀的身份字段会被遮盖。成功结果保持原样。

错误线索只是模式匹配，不等于已确认原因。thinking、失败回答正文、原始错误文本、
stderr 和任意附加字段均不进入新增诊断。非零退出或超时仍沿用原有 stderr 隐藏规则，
明确标注没有完成元数据。修复无法恢复旧调用中已经丢失的字段。

局部验证：18 个新增 transport 用例及 3 个第二批控制器用例通过；Ruff、格式和显式
Pyright 通过。还用实际安装的 OpenEvals 完成一次模拟进程的 evaluate/live/save 链路
检查，确认新增元数据会写入失败记录，且仍拒绝该结果。模拟错误包含 HTTP 429 和
usage limit，**这只是测试夹具，不是旧失败的诊断**。真实 Pi/模型调用为零，网络守卫
记录为零。LSP 未确认 clean，以显式 Pyright 结果为类型检查证据。修复摘要见
[transport-repair.json](transport-repair.json)。

用户随后授权的恢复评审已完成，结果单独保存在
[openevals-pilot-2-recovery-1](../openevals-pilot-2-recovery-1/README.md)。
原失败及本页的历史停止记录不变；恢复成功不解释旧失败原因。
