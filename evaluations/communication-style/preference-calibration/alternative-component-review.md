# 删除诊断替代组件核查

结论：保留 **OpenEvals 的 `RAG_HELPFULNESS_PROMPT` 与公开自定义输出接口**作为下一步
候选；未采用、未安装、未运行模型，也未冻结小批协议。没有找到经过本次所需中文
解释价值验证的现成裁判。此结论来自接口、提示词及调用路径核查，不是模型效果结果。

## 范围与版本

- DeepEval：GitHub latest-release 返回 `python-v4.2.4`，tag 对应提交
  `da9b2c969f8a15e8aa4ef67c372157ce060cd63e`。
- OpenEvals：main 本次解析为 `5753dc75d40c2be75ffd38eb6d63bb966cbcc4e3`，其 Python
  包声明版本为 `0.2.2`。核查对象是该源码提交；未证明某个已发布 wheel 与之相同。
- 初筛还查看了 Ragas 自定义离散评价与 TruLens 的 RAG triad 说明；本轮没有对它们
  进行完整源码审计，不据此宣称它们整体不可用。避免继续扩展框架清单。

搜索摘要曾声称 OpenEvals 有 `create_pairwise_llm_as_judge`。该 Python 路径返回 404，
所查固定提交的 README 和包目录没有相应入口；本记录仅采用源码确认的
`create_llm_as_judge` / `create_async_llm_as_judge`。检索摘要不作为 API 证据。

## 候选取舍

| 候选 | 已确认能力 | 对本任务的限制 | 处理 |
| --- | --- | --- | --- |
| DeepEval Answer Relevancy | 输入问题和答复；保留 statements、verdicts、reason、verbose logs | 判断现有语句是否相关，不检查缺失机制；`borderline` 表示模糊或辅助相关信息，并计为通过 | 不作为两组删除的主要诊断器 |
| DeepEval GEval / ConversationalGEval | 可指定准则与步骤；后者读取对话 turns | 返回整体 score/reason，任务准则仍需自行提供；没有现成逐项删除诊断结构 | 本轮不优先接入 |
| OpenEvals `CONCISENESS_PROMPT` | 无需参考答案；接收 inputs、outputs | 明确惩罚 hedging，并要求未明确请求时不解释，和当前保留合理限定及解释的原则冲突 | 不采用该提示词 |
| OpenEvals `RAG_HELPFULNESS_PROMPT` | 无需参考答案；检查问题需要、必要信息、详略、缺失与无用内容，并要求具体优缺点 | 默认仍是总体布尔分数和理由；没有专用机制关系结构或中文有效性证据 | 保留为有限候选 |

DeepEval 的相关性检查只要求对 `no` 或 `borderline` 提供逐项理由。对“相关但没有说明
作用”的 P01 末句，相关性本身不能决定是否值得保留；对 P02，B 留下的语句均相关也
不能证明解释完整。这是目标契约的限制，未运行模型来断言它一定误判。

## 为什么保留 helpfulness 提示

固定版本的原文明确要求：

- “Provide accurate and necessary information”
- “Be appropriately detailed for the query's scope”
- 识别 “Any critical missing information” 与 “Any extraneous or unhelpful content”
- “Identify specific strengths and weaknesses in the response”

这些要求允许判断“相关内容是否有用”和“删后是否缺少所需解释”，更接近两组人工
反馈。提示名包含 RAG，但实际占位符仅为 `inputs` 和 `outputs`，不强制标准答案或
检索文档。共同问题与已有上下文可以放在 inputs 中；不得把 A 或 B 填成另一方的
参考答案，也不得加入人的偏好标签、点评或期待结论。

局限仍然明确：它是一般性有用性提示，没有经过核验的中文解释作用模型。原样调用
会返回总体布尔评价；`create_llm_as_judge(output_schema=...)` 可改为只返回诊断结构，
包括逐项发现及显式不确定状态。**该输出契约属于需要冻结和验证的本地适配**，不能
称为完全开箱即用，也不能因此宣称框架解决了语义判断。

最小用途可以是 A/B 各自按同一问题、上下文和准则接受检查，再对照具体发现。
这保留双方平等地位，允许看见共有缺陷；它尚不是已验证的自动成对差异提取器。
将 A/B 一起送入通用提示并要求成对诊断，会进一步改变任务，不在本轮默认为已适配。

## 调用、失败与数据边界

### OpenEvals 的直接 SDK 路径

固定源码的普通成功路径每次评价仅调用一次 `chat.completions.create`，随后直接
`json.loads`；没有先生成评价步骤或额外总结理由。两组的 A/B 各检查一次共 **4 次
逻辑请求**，这是静态路径计数，尚未成为批准预算或实际 HTTP 测量。模型 SDK 重试、
拒绝、超时与失败中断均需另外核查；不从此推断所有 LangChain 路径也只有一次请求。

- 所读 `llm.py` 与 `utils.py` 没有自行重试、修补 JSON 或启用结果缓存的逻辑；这不能
  排除传入客户端、全局设置或下层 SDK 的行为。
- 直接 SDK 分支把 JSON Schema 发给提供方，但本地解析后不另做完整 schema 校验。
  因此“JSON 合法但字段缺失”仍需独立验收，不能只相信提供方的结构化输出承诺。
- 两个文件使用 LangSmith `traceable`，测试上下文还可记录反馈。官方文档支持
  `tracing_context(enabled=False)`；禁用追踪和无额外上传需要在隔离环境核实，不能
  依赖当前 shell 恰好没有 API key。未授权云端数据集或 tracing 上传。
- 自定义 schema 返回的是解析结果，不是含 usage、原始响应和异常的完整留存包。
  现有隔离调用与原始失败留存仍有适配工作；Pi `invoke` 不能直接当 SDK client 传入。
- 包依赖 LangChain、langchain-openai、LangSmith 等，采用源码包不是零依赖替换。
  尚未锁定传递依赖、确认模型/接口兼容性或进行无网络假客户端测试。

### DeepEval 的额外边界

Answer Relevancy 的普通 LLM 成功路径为拆分、逐项判断、总结理由三步；关闭
`include_reason` 可省去总结。该版本另有 system-one 路径，不把三步计数推广到所有
模式。GEval 可显式提供 evaluation_steps，避免模型先生成步骤；总调用数仍取决于
所选模型与评分分支，本轮未给出完整上界。

`metrics/utils/generation.py` 的 `trimAndLoadJson` 会截取 JSON、补缺失的右花括号，
并在解析失败后去除尾逗号再次解析。这是可见的自动输出修补，与本研究的原始失败
保留原则不符；不是声称每种 native-schema 路径都会经过这段逻辑。因此本轮不继续
为 DeepEval 审计全部 provider 重试或修改其解析实现。

## 中文证据及决策边界

所查官方文档、源码和定向检索没有提供这些候选对当前中文删除/解释诊断的准确率
或独立验证。可输入中文、可自定义准则、某个基准也名为 OpenEval，都不能补足此证据。
OpenEval 中文基准与 LangChain OpenEvals 是不同项目。

当前建议只保留一个后续方向：先确认 OpenEvals helpfulness 的最小输出适配及隔离
调用是否值得接入；若继续，先做无模型的格式、计数、失败留存和禁止追踪检查，再
另行冻结最多两组的小批。格式失败或实质误判均停止，不更换准则追分、不扩量。
若接入成本超过它减少的自建代码，就不迁移；不能把支持自定义 prompt 当作效果改善。

原始题包、反馈、历史失败和暂停的 v5 草稿均未改动。没有新安装、依赖变更、模型
评测或云端数据上传；本轮只检查本记录及计划的 Markdown 和 Git 空白。

## 来源

- [DeepEval release](https://github.com/confident-ai/deepeval/releases/tag/python-v4.2.4)
- [Answer Relevancy 实现](https://github.com/confident-ai/deepeval/blob/da9b2c969f8a15e8aa4ef67c372157ce060cd63e/deepeval/metrics/answer_relevancy/answer_relevancy.py)
- [DeepEval 默认提示](https://github.com/confident-ai/deepeval/blob/da9b2c969f8a15e8aa4ef67c372157ce060cd63e/deepeval/templates/metrics/templates.json)
- [ConversationalGEval 实现](https://github.com/confident-ai/deepeval/blob/da9b2c969f8a15e8aa4ef67c372157ce060cd63e/deepeval/metrics/conversational_g_eval/conversational_g_eval.py)
- [DeepEval JSON 解析](https://github.com/confident-ai/deepeval/blob/da9b2c969f8a15e8aa4ef67c372157ce060cd63e/deepeval/metrics/utils/generation.py)
- [OpenEvals helpfulness 提示](https://github.com/langchain-ai/openevals/blob/5753dc75d40c2be75ffd38eb6d63bb966cbcc4e3/python/openevals/prompts/rag/helpfulness.py)
- [OpenEvals conciseness 提示](https://github.com/langchain-ai/openevals/blob/5753dc75d40c2be75ffd38eb6d63bb966cbcc4e3/python/openevals/prompts/quality/conciseness.py)
- [OpenEvals 通用评价接口](https://github.com/langchain-ai/openevals/blob/5753dc75d40c2be75ffd38eb6d63bb966cbcc4e3/python/openevals/llm.py)
- [OpenEvals 包装与 tracing](https://github.com/langchain-ai/openevals/blob/5753dc75d40c2be75ffd38eb6d63bb966cbcc4e3/python/openevals/utils.py)
- [OpenEvals 依赖](https://github.com/langchain-ai/openevals/blob/5753dc75d40c2be75ffd38eb6d63bb966cbcc4e3/python/pyproject.toml)
- [LangSmith tracing 开关](https://docs.langchain.com/langsmith/trace-without-env-vars)
