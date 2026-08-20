# MATH-AI-LAB 博士级数学研究工作台：总架构契约

**设计日期：** 2026-08-20
**文档状态：** Candidate，等待仓库级人工审核
**设计类型：** Umbrella Architecture / Stable Contract
**实施状态：** 未开始
**替代文档：** 本版替代同路径的单体设计初稿；能力范围不缩减

---

## 1. 本文只决定什么

本文是博士级工作台的总架构契约，负责固定：

1. 不可削减的能力范围；
2. Foundation Core 与研究能力的边界；
3. 跨模块信任、来源、状态和验收协议；
4. 版本顺序与关闭条件；
5. 专项规范之间的权威关系。

本文**不是** Frozen Schema authority，不声明任何未实现能力已经可用，也不授权生产代码修改。权威优先级保持为：

1. `元数据规范.md`：Frozen Knowledge / Problem / Attempt / Method Schema；
2. `项目规则.md` 与 `AGENTS.md`：项目治理和高频执行规则；
3. `09_长期记忆/项目进度.md`：实现后的动态 Phase、能力状态和测试基线；
4. 本文：升级总架构；
5. 本文链接的专项规范：子系统设计细节。

发生冲突时修订下游设计，不得反向修改 Frozen Schema。本文批准后，仍须逐版本编写实施计划、执行 TDD、验证并人工审核。

---

## 2. 当前基线与第一阻塞

MATH-AI-LAB 已有 Foundation 能力包括：Problem 中心化、Attempt 与 AI Solution 分离、Canonical Solution、Knowledge / Problem / Attempt / Method 对象、学习与 Error Evidence 边界、Validator、Indexer、Workspace、Atomic Mutation、Normal Operation、LaTeX 原子发布和 Verification Contract。未 Frozen 的 Error Mode 等对象仍保持 Candidate/Pilot 边界，不因升级设计被伪装为正式 Schema。

设计评审时的可复现实测基线为 `615 passed, 3 failed`。三个失败均与测试中硬编码 `C:\MATH-AI-LAB` 有关。因此：

- 第一个实施版本固定为 **v1.0.1 Foundation Portability Closure**；
- 远程 Core、完整测试及新增跨平台回归未变绿前，不得宣称跨平台关闭；
- 此基线属于设计时快照，实施后的最新事实只写入 `09_长期记忆/项目进度.md`。

---

## 3. 不可削减的能力全集

后续可以替换引擎、调整顺序、加强门槛，但不得静默删除下列能力：

| # | 能力 | 最终研究价值 |
| ---: | --- | --- |
| 1 | 研究问题与项目管理 | 固定问题、边界、里程碑和决策 |
| 2 | PDF 与多格式文档读取 | 获取原始研究资料 |
| 3 | MinerU 文档解析 | 将复杂 PDF 转为可处理 Markdown 和结构化派生物 |
| 4 | 内容精选与原页复核 | 从长文档中提取可追溯研究材料 |
| 5 | 文献检索、版本识别、引用与比较 | 建立可靠文献上下文 |
| 6 | Claim–Evidence 证据链 | 让主张可核查、可反驳 |
| 7 | 数学推理、反例、一般化和条件检查 | 保持数学严谨性 |
| 8 | 多类型数学建模 | 将研究问题转为可验证模型 |
| 9 | 可复现计算实验 | 保存环境、输入、参数、代码和结果 |
| 10 | 负结果与研究决策记录 | 防止重复失败并保留研究演化 |
| 11 | 完整制图和出版级图表 | 使结果可解释、可重建、可发表 |
| 12 | Lean / Mathlib 形式化 | 为适合的命题提供机器检查证明 |
| 13 | 严格审稿、反驳和复核 | 主动发现论证、模型和引用缺陷 |
| 14 | LaTeX、论文与正式成果发布 | 生成一致、可审计的研究成果 |
| 15 | 知识图谱与跨项目复用 | 沉淀审核后的研究知识 |
| 16 | 全文检索、混合检索和可引用 RAG | 在规模增长后保持可检索性 |
| 17 | 受控多角色 / 多 Agent 协作 | 在审计边界内增强批判与并行研究 |
| 18 | 长期研究记忆和能力成长证据 | 保留项目与研究者的发展轨迹 |

功能属于最终产品范围，不等于每个任务强制调用。运行时只启用适合当前任务且已达到相应成熟度的能力。

---

## 4. 不可突破的架构原则

### 4.1 能力稳定，引擎可替换

**能力**描述用户能够完成的研究工作；**引擎**是 MinerU、Plotly、Lean、求解器或模型供应商等实现手段。二者不得混同。

- 更换或淘汰引擎不得删除能力；
- 每个外部引擎必须有适配器、固定版本、许可记录、健康检查和失败回退；
- `SUPERSEDED_ENGINE` 只用于引擎，不用于能力；
- 规格正文不得因某个工具当前不可用而降低最终能力目标。

### 4.2 Frozen Core 与研究 Sidecar 隔离

```text
交互模式
AUTO / REVIEW / STUDY / RESEARCH
          |
          v
Foundation Core
Problem / Attempt / Solution / Knowledge / Method
          |
          v
研究能力层
Document / Evidence / Model / Experiment / Figure / Lean / Review
          |
          v
外部引擎 Sidecar
MinerU / Solver / Plot Engine / Lean / Search / Model Provider
          |
          v
验证与成果层
Provenance / Gate / Markdown / JSON / Code / Data / LaTeX / PDF
```

- 重型依赖不进入根 `requirements.txt`；
- Core CI 不下载 OCR 模型、求解器全集、Lean 工具链或向量数据库；
- 第一阶段使用显式 CLI、文件或 HTTP 适配器，不建立全局动态 Capability Registry；
- Sidecar 失败不得破坏 Source、已审核结果、已发布 PDF 或普通数学回答。

### 4.3 四级信任分离

| 信任级 | 定义 | 允许动作 |
| --- | --- | --- |
| `SOURCE` | 原始论文、教材、数据、题目 | 作为依据，仍需判断适用性 |
| `DERIVED` | OCR、解析、程序输出、AI 草稿 | 仅候选，不得直接晋升 |
| `REVIEWED` | 已回查原文、验证模型或检查证明 | 可进入研究档案 |
| `FORMAL` | 已获明确授权并正式发布 | 可进入正式知识和成果 |

`Derived → Reviewed` 必须留下审查证据；`Reviewed → Formal Knowledge` 必须复用既有授权语义，用户明确说出 `开始知识沉淀` 后才进入 Knowledge authoring。

### 4.4 研究严谨性

- 数值结果只能用于探索、验证或反例，不能自动替代严格证明；
- `lake build` 通过不等于形式命题与自然语言命题语义一致；
- 研究记录必须同时保存支持证据、反对证据、适用边界、失败实验和可证伪条件；
- 引用、转述与推断必须显式区分；
- AI 生成内容默认是 Candidate，作者对最终成果负责。

---

## 5. 跨模块协议

### 5.1 Provenance Envelope

Provenance Envelope 是**派生成果协议**，不是 Frozen Source Schema。每个可复用派生成果至少携带：

```yaml
provenance_version: "1"
artifact_id: "project-local stable id"
artifact_type: "document_chunk | evidence | run | figure | lean_build | review"
producer:
  name: "adapter or tool"
  version: "exact version"
created_at: "RFC 3339 UTC"
upstream:
  - ref: "path, URI, object ID or run ID"
    sha256: "64 lowercase hex characters"
parameters_sha256: "64 lowercase hex characters or null"
environment_ref: "manifest path or null"
trust_level: "DERIVED | REVIEWED | FORMAL"
review_ref: "review evidence path or null"
```

约束：

- 上游内容、参数或环境改变时，不得沿用旧 provenance；
- 缺失关键 hash 的成果不得标为 `REVIEWED`；
- 外部来源必须同时记录 URI、访问时间、版本和许可/使用边界；
- 各子系统可以扩展字段，但不得改变上述字段语义。

### 5.2 长任务状态

文档解析、求解、仿真、渲染、Lean 构建、索引和多角色任务统一使用：

```text
QUEUED → RUNNING → SUCCEEDED
                 → PARTIAL
                 → FAILED
                 → CANCELLED
```

- `PARTIAL` 必须列出成功与缺失产物；
- `FAILED` 保留诊断和日志，不覆盖上一次成功产物；
- 重试生成新 run，不改写历史 run；
- 只有 `SUCCEEDED` 且通过专项 Gate 的输出才可成为 Reviewed 候选。

长任务状态只描述执行过程，不能替代能力调用结果。每次调用还必须独立报告：`requested`、`available`、`executed`、`candidate_generated`、`gate_passed`、`human_reviewed`、`formal_published`、`fallback_used`。因此“引擎可用”不等于“结果已审核”，“执行成功”也不等于“已正式发布”。

实施时可复用既有 `LayerStatus` 等稳定语义，但不得把文档、模型、Lean 等领域状态强行塞入 Normal Operation `OperationResult`，也不得建立重复的通用状态框架。

### 5.3 单一事实源

- `research_dossier.md` 只做人工可读摘要、导航和当前研究态势；
- 假设的权威记录是 `assumptions.md`；
- Claim–Evidence 的权威记录是 `evidence.md`；
- 研究决策的权威记录是 append-only `decisions.md`；
- Dossier 只能引用或汇总上述记录，不复制其完整事实；
- 动态能力状态只写 `09_长期记忆/项目进度.md`，设计规范不伪装成运行状态。

### 5.4 数据等级

所有源资料、数据集、派生物、索引和模型输入必须标记为 `PUBLIC`、`PERSONAL` 或 `RESTRICTED`，并遵守[数据治理与学术诚信规范](2026-08-20-doctoral-workbench-data-governance-design.md)。未识别等级时按更严格一级处理。

---

## 6. 专项规范地图

| 专项规范 | 唯一职责 |
| --- | --- |
| [能力成熟度与版本路线](2026-08-20-doctoral-workbench-capability-roadmap.md) | 能力状态、版本门槛、全局验收矩阵 |
| [文档智能与证据链](2026-08-20-doctoral-workbench-document-evidence-design.md) | PDF、MinerU、精选、原页锚点、文献证据 |
| [数学建模与可复现实验](2026-08-20-doctoral-workbench-modeling-reproducibility-design.md) | 模型家族、环境、运行清单、验证和失败语义 |
| [制图与研究成果](2026-08-20-doctoral-workbench-visualization-artifact-design.md) | 图表家族、生成协议、可访问性和出版 |
| [Lean 形式化](2026-08-20-doctoral-workbench-lean-formalization-design.md) | Lake 工程、语义对照、证明和 CI |
| [研究工作流、审稿与写作](2026-08-20-doctoral-workbench-research-workflow-design.md) | Dossier、决策、严格审稿、知识晋升和成果一致性 |
| [检索、RAG 与多角色协作](2026-08-20-doctoral-workbench-retrieval-collaboration-design.md) | 检索阶梯、评测、引用式 RAG、多 Agent 边界 |
| [数据治理与学术诚信](2026-08-20-doctoral-workbench-data-governance-design.md) | 数据分级、Git/大文件、许可、隐私、AI 贡献 |

专项规范不得缩小本总纲的能力范围。跨专项冲突以本总纲为准；专项内部细节以对应规范为准。

### 6.1 目标存储边界

| 路径 | 目标职责 |
| --- | --- |
| `03_参考资料/<资料或项目>/source/` | 原始资料引用或获准保存的 Source |
| `03_参考资料/<资料或项目>/derived/` | MinerU 等解析派生物与缓存 |
| `03_参考资料/<资料或项目>/reviewed/` | 完成原页核对的精选和审查证据 |
| `05_代码/<项目>/` | 项目隔离的模型、实验、数据 manifest 和图源 |
| `06_LEAN形式化/` | 单一 Lake 工程与形式化成果 |
| `07_项目/<项目>/` | Dossier、假设、证据、决策和审稿导航 |
| `04_LATEX/` / `08_成果输出/` | 既有 P9 source 与正式发布边界 |
| `tools/<capability-adapter>/` | 后续版本的显式适配器；不得提前建立通用 Agent Framework |

这些是目标职责，不授权本轮创建目录或生产模块。已有路径的真实职责继续以项目规则和 filesystem 为准。

---

## 7. 能力成熟度，不再用“有/无”二元判断

| 状态 | 严格含义 |
| --- | --- |
| `TARGET` | 已进入批准的最终范围，尚无生产能力 |
| `PILOT` | 在限定 fixture 或单个真实项目成功，不可默认推广 |
| `STABLE` | 契约固定、失败可控、回归测试稳定，允许受控使用 |
| `VERIFIED` | 已在至少两个不同类型真实项目复用，并满足专项关闭 Gate |
| `SUPERSEDED_ENGINE` | 某实现引擎已被版本化替代；能力本身仍存在 |

规则：

- 版本名称表示框架交付，不代表其中每个子能力均已 `VERIFIED`；
- 能力和引擎分开记录状态；
- 升级状态必须附 Gate Evidence；
- 降级或撤销状态必须保留原因、影响和恢复路径；
- 具体能力矩阵见[能力成熟度与版本路线](2026-08-20-doctoral-workbench-capability-roadmap.md)。

---

## 8. 版本路线与关闭逻辑

```text
v1.0.1  Foundation Portability Closure
v1.1    Research Project & Dossier
v1.2    Document Intelligence
v1.3    Literature Evidence
v1.4    Modeling & Reproducible Experiment Framework
v1.5    Figure & Visualization Framework
v1.6    Lean Formalization
v1.7    Critical Review
v1.8    Research Writing & Artifact Consistency
v2.0    Hybrid Retrieval & Cited RAG
v2.1    Controlled Multi-Agent Research
v2.2    Doctoral Research Workbench Closure
```

路线满足能力递增，不要求代码单调增加：

```text
Capability(v1.0.1) ⊆ Capability(v1.1) ⊆ ... ⊆ Capability(v2.2)
```

实现引擎可以被安全替换。v1.4 和 v1.5 分别关闭“建模框架”和“制图框架”，不虚报全部模型/图形家族已验证；v2.2 只有在覆盖矩阵满足强制状态后才能关闭。

---

## 9. 所有验收必须采用 Gate Template

任何版本或能力的验收至少包含：

| 字段 | 必填内容 |
| --- | --- |
| `Baseline` | 修改前可复现状态和已知失败 |
| `Metric` | 可计算或可判定的衡量项 |
| `Threshold` | 明确通过值，不使用“基本可用” |
| `Fixture` | 固定测试样例及 hash / 版本 |
| `Evidence` | 测试日志、manifest、review 或 artifact 路径 |
| `Failure Action` | 失败后的阻断、回滚或降级动作 |

无 Baseline、Threshold 或 Evidence 的“验收通过”无效。专项规范可以增加字段，不能减少字段。

---

## 10. 运行安全、健康检查与回滚

每个外部能力必须提供只读 `doctor` / health-check，至少报告：

- 适配器和引擎版本；
- 操作系统、Python / Lean 版本、CPU / GPU 要求；
- 许可证与数据等级限制；
- 缺失依赖和可用 fallback；
- 最小 fixture 是否通过；
- 最后一次成功验证的 Evidence。

生产写入必须遵守现有 Source Mutation 权限和 atomic replace 语义。外部任务失败时：

1. 不覆盖正式 Source 或上一次成功产物；
2. 保留日志、run manifest 和失败分类；
3. 将依赖能力降级为显式不可用或 fallback；
4. 不阻塞无关 Core 工作流；
5. 恢复后用新 run 重验，不篡改失败历史。

---

## 11. 总体验收定义

v2.2 只有在以下事实均有 Evidence 时才允许关闭：

1. 当前 Core 与完整测试在目标平台全绿；
2. 18 项能力均保留在范围内并达到路线规定的最低成熟度；
3. PDF 精选中的关键主张可定位到原页、版面区域和 source hash；
4. 文献证据明确区分引用、转述、推断及反对证据；
5. 模型、数据、参数、环境和实验可由独立运行重建；
6. 正式图表可回到代码、输入数据、run 和 Claim；
7. 适合的 Lean 命题无 `sorry` / `admit`，构建通过且完成语义对照；
8. 审稿能够阻断无证据主张、单位错误、数据泄漏和错误形式化；
9. 论文、代码、数据、图表、补充材料和发布 PDF 一致；
10. 检索 / RAG 的引用质量达到固定评测阈值；
11. 多角色输出保持 Candidate、全程可审计且优于单角色基线；
12. 数据、许可、作者责任和 AI 贡献满足治理规范；
13. 至少两个不同类型真实研究项目完成端到端复用；
14. 第二个项目证明能力可复用，而不是第一个项目的硬编码演示。

---

## 12. 明确拒绝的架构捷径

- 把 MinerU、求解器、Lean、绘图库和向量数据库塞入一个根环境；
- 复制 MinerU 源码进入仓库；
- 为研究对象立即修改 Frozen Schema 或创建重复 Registry；
- 把 Dossier、assumptions、evidence、decisions 同时当作事实源；
- 用“跑通一个样例”宣称整个模型或图形家族完成；
- 用 OCR 文本替代原页复核；
- 用数值实验替代证明，或用 Lean 编译替代语义审核；
- 让 RAG 生成无来源结论；
- 让 Agent 直接修改正式 Source；
- 因某个引擎不可用而删除对应能力；
- 在无测试、无迁移期时静默替换稳定引擎。

---

## 13. 决策与下一步

本优化版已经把“永久能力”和“阶段实现”分开，并将单体文档拆为可独立评审的专项规范。它仍只是一组 Candidate 设计，不是实施完成声明。

人工审核通过后，下一份工程文档只允许是：

> `v1.0.1 Foundation Portability Closure` 的详细 TDD 实施计划。

该计划获得批准前，不实施 MinerU、建模、制图、Lean、RAG 或多 Agent 生产模块。
