# Ragas 适配核查：暂不进入模型小批

结论：**Ragas 的现成 `FactualCorrectness` 不直接适配当前两组删除比较**。
保留其命题拆分与双向蕴含思路，不安装依赖、不运行模型小批，也不把更换框架当作
裁判已经改善。此次为文档和源码静态核查，没有运行时兼容性或中文准确率实测。

## 核查对象

GitHub latest-release 接口本次返回 `v0.4.3`，发布于 2026-01-13；tag 对应提交
`4ecab384fda829ca50bec3f07cc49589d756e172`。以下源码结论针对该版本的 collections API，
不混用 legacy API 或未发布 main 的行为。中文与重试文档属于另行注明的当前文档，
不能替代对实际安装依赖版本的验证。本次未安装任何版本。

## 能力与缺口

| 要求 | 源码观察 | 适配判断 |
| --- | --- | --- |
| A/B 双向比较 | `f1`、`recall` 模式均执行 response→reference 和 reference→response 两路命题拆分与蕴含；`precision` 仅执行前一路 | 有双向计算，但不能把 reference 当标准答案，也不能把双向总分当偏好 |
| 使用当前问题和已有上下文 | `ascore(response, reference)` 没有 `user_input` 或对话上下文参数；拆分只看单份文本，蕴含只看另一份文本 | 缺少本任务的关键输入 |
| 区分空泛补充与机制解释 | 默认要求拆成可独立验证的命题，再判断是否能从另一段直接推出 | 不包含解释作用、任务必要性或双方共有缺陷的判断目标 |
| 输出差异及证据，不给总分 | 内部 NLI 生成 statement/reason/verdict，但公开 `ascore()` 只返回四舍五入后的 `MetricResult(value=...)` | 中间信息未随标准结果返回；提取与验证方法以下划线命名，不是独立的稳定公共诊断接口 |
| 允许不确定 | 默认 NLI 只有 0/1；示例将矛盾与未提供支持都判 0 | 不能直接表达我们要求的不确定及差异类别 |
| 中文支持 | 有提示语言适配机制；默认翻译 few-shot 示例，完整指令翻译需另开选项 | 可适配，不等于中文对话解释质量已验证；所查文档与检索未找到对应有效性证据 |
| 保留现有隔离调用 | collections 检查 LLM 为 `InstructorBaseRagasLLM`；默认路径是 SDK/Instructor | 现有 Pi `invoke` 函数不能直接传入；需要另写并验证适配层 |

默认 `atomicity="low"`、`coverage="low"` 会在示例中主动省略某些细节。
改成 high/high 可以改变拆分粒度与覆盖要求，但不会自动补上“这句话是否帮助理解”的
判断目标。当前字段说明也不能保证因果链在拆分后仍完整保留。

这解释了两组材料的适配风险：

- P01：若“个人选择有作用”被提取为独立命题，B 不包含它可能被记作未覆盖；这并不
  回答用户指出的“它没有说明作用是什么”。
- P02：机制句的主张可能被检测为 A 独有，但能否推出相同结论不等于 B 已解释清楚
  从水汽积聚到净蒸发减慢的联系。

以上是输入和目标契约的分析，不是预测到的模型分数或实际失败结果。两组人工标签
保留在 [反馈记录](deletion-pilot-1-feedback.json)，不用于推导任何未运行的模型结果。

## 调用次数：静态推导，不冒充实测

成功且两侧都产生非空命题时：

| 操作 | 逻辑 `agenerate` 次数 |
| --- | ---: |
| 一组 `precision` | 2：拆分一侧＋向另一侧验证 |
| 一组 `f1` 或 `recall` | 4：两侧各拆分一次、各验证一次 |
| 两组各做一次双向计算 | 8 |
| 默认适配两个提示的 few-shot 示例 | 额外 5：拆分提示四组示例＋NLI 一组示例 |
| 同时适配两段指令 | 在上述适配之外再加 2 |

这些是源码路径上的逻辑请求数，不是底层 HTTP 实测次数。空命题会跳过对应验证；
异常会中断；缓存和多层重试也会改变实际请求。语言适配是额外准备成本，不应藏在
“两组测试”里，且译后提示需要固定、复查，不能每次临时生成。

## 重试、失败留存与依赖边界

- Ragas 的 Instructor 适配器将附加参数传给结构化输出调用；它的源码没有独立关闭
  SDK 与 Instructor 两层重试。
- OpenAI SDK 文档说明默认对部分失败重试两次；`max_retries=0` 可关闭 SDK 重试。
- 当前 Instructor 文档将整数 `max_retries` 定义为首次提取之后的校验重试次数，
  并说明解析或校验失败可触发带错误信息的重新请求。该层也需单独关闭。
- Ragas 的 `pyproject.toml` 未固定 Instructor 版本，OpenAI 仅有下界。因此单独固定
  Ragas 版本不足以证明整个调用栈的一次尝试行为。若将来采用，需要固定传递依赖，
  通过不调用模型的假客户端检验计数和失败留存，再考虑付费调用。
- Instructor hooks 观察到的是提取尝试，不一定包含 SDK 内部 HTTP 重试。不能用
  上层计数宣称完整调用次数，也不能把未测量记成零。
- `ascore()` 的数值结果本身不构成可见原始输出和失败尝试的完整留存。接入现有研究
  还需独立留存边界；不能默认框架已经满足本仓库协议。

另一个静态校验边界：该版本的 verdict 声明为 `int`，0/1 仅写在描述中；汇总使用
`bool(stmt.verdict)`。所读方法也没有核对返回项是否与输入命题逐项对应。这说明其
结构契约与当前 fail-closed 要求不同；本次没有测试这些情况的实际触发率。

## 决策与后续范围

停止在适配核查阶段，不开展 Ragas 的两组模型小批，不为接入它增加定制裁判和适配
框架。它可以成为将来独立的命题支持检查工具，但不能作为当前解释价值诊断的现成
替代。该决定不评价 Ragas 在其原定事实正确性任务上的整体质量。

若继续选择其他组件，先要求其接口能接收共同请求与上下文，并能保留逐项判断和
不确定状态；不能只因有相似度或覆盖率便投入付费测试。当前尚未选择替代组件。

本次仅验证这份记录和实施计划的局部 Markdown 与 Git 空白，不运行全仓测试。
没有修改原始题包、标签、裁判冻结文件或运行时段落；未冻结的 v5 草稿仍暂停。

## 来源

- [v0.4.3 release](https://github.com/vibrantlabsai/ragas/releases/tag/v0.4.3)
- [指标实现：双向路径、公开返回值、默认参数](https://github.com/vibrantlabsai/ragas/blob/4ecab384fda829ca50bec3f07cc49589d756e172/src/ragas/metrics/collections/factual_correctness/metric.py)
- [命题与 NLI 提示、输出字段、四组示例翻译](https://github.com/vibrantlabsai/ragas/blob/4ecab384fda829ca50bec3f07cc49589d756e172/src/ragas/metrics/collections/factual_correctness/util.py)
- [通用提示翻译](https://github.com/vibrantlabsai/ragas/blob/4ecab384fda829ca50bec3f07cc49589d756e172/src/ragas/prompt/metrics/base_prompt.py)
- [collections 接口类型检查](https://github.com/vibrantlabsai/ragas/blob/4ecab384fda829ca50bec3f07cc49589d756e172/src/ragas/metrics/collections/base.py)
- [LLM 封装与参数传递](https://github.com/vibrantlabsai/ragas/blob/4ecab384fda829ca50bec3f07cc49589d756e172/src/ragas/llms/base.py)
- [Instructor 适配器](https://github.com/vibrantlabsai/ragas/blob/4ecab384fda829ca50bec3f07cc49589d756e172/src/ragas/llms/adapters/instructor.py)
- [依赖声明](https://github.com/vibrantlabsai/ragas/blob/4ecab384fda829ca50bec3f07cc49589d756e172/pyproject.toml)
- [语言适配文档](https://docs.ragas.io/en/latest/howtos/customizations/metrics/metrics_language_adaptation/)
- [Ragas 超时与重试文档](https://docs.ragas.io/en/latest/howtos/customizations/run_config/)
- [Instructor 重试及实际调用计数边界](https://python.useinstructor.com/concepts/retrying/)
- [OpenAI SDK 重试](https://github.com/openai/openai-python#retries)
