# MATH-AI-LAB 研究工作流、审稿与写作规范

**状态：** Candidate
**上位契约：** [博士级数学研究工作台总架构](2026-08-20-doctoral-research-workbench-design.md)
**对应版本：** v1.1、v1.7、v1.8

---

## 1. 目标

本规范定义从研究问题到可发布成果的人工可审计工作流，重点解决事实重复、负结果丢失、AI 草稿越权晋升和论文各产物不一致。

它不创建新的 Frozen Research Schema。第一阶段使用项目内 Markdown、manifest 和明确引用；只有真实使用证明稳定后，才另行讨论是否需要新 Schema。

`negative_results.md` 与 `governance.md` 是 **v1.1 项目级 Candidate Contract**，不是 Frozen Schema，也不是全局 P/K/A/M Registry。

---

## 2. 项目目录与单一事实源

```text
07_项目/<项目>/
├── research_dossier.md
├── assumptions.md
├── evidence.md
├── decisions.md
├── negative_results.md
├── governance.md
├── documents/
├── runs/
├── artifacts/
└── reviews/
```

项目身份由目录路径 `07_项目/<项目>/` 标识。v1.1 **不**新增全局 Research Project ID，也 **不**创建第二套 Problem / Attempt / Method / Knowledge Registry。

### 2.1 `research_dossier.md`（导航与摘要，不是事实源）

Dossier 只保留：

- 研究问题与范围摘要（人工 Source；工具不得覆盖）；
- 当前阶段和阻断项；
- 最重要的已审核发现导航；
- canonical assumptions / evidence / decisions / negative_results / governance 的链接；
- 模型、实验、Figure、Lean、review 和成果导航；
- 当前贡献、局限和下一步候选（Generated 区可派生，人工结论除外）。

Dossier **不是**事实源。不得复制完整假设、证据、决策、负结果或治理 canonical block。自动生成摘要必须能重建；人工摘要与 canonical 事实冲突时，以 canonical 文件为准并修正 Dossier。

Generated 区域必须使用唯一成对 marker：

```markdown
<!-- MATH-AI-LAB:RESEARCH-DOSSIER GENERATED BEGIN -->
...
<!-- MATH-AI-LAB:RESEARCH-DOSSIER GENERATED END -->
```

`reconcile` 只能替换 marker 内部。marker 缺失、嵌套、顺序错误或损坏时必须拒绝写入。

### 2.2 `assumptions.md`（假设事实源）

每条假设记录项目内 ref、正文、范围、来源/理由、可证伪条件、状态、影响的 Claim/Model 和审查记录。假设变化不删除历史版本，应记录替代关系及影响分析。

### 2.3 `evidence.md`（Claim–Evidence 事实源）

每个核心 Claim 记录支持、反对、限制、Source Anchor、运行或证明 Evidence，以及 `QUOTE / PARAPHRASE / INFERENCE / COMPUTATION` 分类。不得用 Dossier 中的叙述替代 Evidence。

Evidence 关系极性使用：`SUPPORT` / `OPPOSE` / `LIMIT`。

### 2.4 `decisions.md`（append-only 决策事实源）

决策记录 append-only，至少包括：日期、问题、可选方案、选择、依据、反对意见、代价、可逆性、触发重新评估的条件和关联 Evidence。错误决策通过追加 superseding entry 修正，禁止覆盖历史。

### 2.5 `negative_results.md`（负结果事实源；Candidate Contract）

负结果是项目级 canonical Source，不是 Generated。每条负结果至少包括：项目内 `NEG-####` ref、失败路线描述、失败 Evidence、对 Claim/Model/Decision 的影响、重试条件与当前状态。负结果不等于垃圾输出；只有明确无研究价值且不属于审计记录的临时缓存，才按治理策略清理。

### 2.6 `governance.md`（治理事实源；Candidate Contract）

治理记录是项目级 canonical Source，至少包括：项目数据等级（`PUBLIC` / `PERSONAL` / `RESTRICTED`）、外部数据与文档许可状态、外部处理授权、AI Contribution Log。Personal/Restricted 数据缺少明确授权时，必须阻断外部处理；该阻断可在 Dossier Generated 区导航，但授权事实只存在于 `governance.md`。

### 2.7 承载目录（后续版本接口，v1.1 只建空导航）

| 目录 | 职责 | 后续版本 |
| --- | --- | --- |
| `documents/` | PDF、MinerU 与文献导航 | v1.2 |
| `runs/` | 模型、实验、解析与检索 run 导航 | v1.4 |
| `artifacts/` | Figure、Lean、LaTeX 与补充材料导航 | v1.5 / v1.6 |
| `reviews/` | 审查、作者回复、处置与复核 Evidence | v1.7 |

v1.1 可创建这些空目录作为项目 scaffold，但不得实现 MinerU、求解器、制图、Lean、RAG 或 Multi-Agent。

---

## 3. 项目内局部引用

v1.1 使用项目内局部 ref：

```text
ASM-0001
CLM-0001
EVD-0001
DEC-0001
NEG-0001
```

规则：

- 只在单个项目目录内部唯一；
- 同类型 ref 不得重复；
- 不同类型 ref 不得错误复用同一编号语义（格式前缀绑定类型）；
- 不创建全局 Registry；
- 不改变现有 P / K / A / M ID；
- 不与 Attempt ID 混用；
- 不声称为 Frozen Schema 字段；
- 目录路径是 v1.1 项目身份。

---

## 4. 研究状态不是对象 Schema

项目级研究态势可使用：

```text
FRAMING → EVIDENCE_GATHERING → MODELING_OR_PROVING
        → VALIDATION → REVIEW → WRITING → RELEASED
```

这是导航状态，不得与 Problem YAML `status`、目录 workflow、Attempt outcome、run status 或能力成熟度混同。状态变化只汇总真实 Source，不自动触发 Frozen 对象 lifecycle。

---

## 5. 四级自动化

```text
A1 初始化项目
A2 原子记录与替代
A3 校验、派生、freshness 与 reconcile
A4 dossier-smoke CI
```

| 级别 | 允许 | 禁止 |
| --- | --- | --- |
| A1 | `init` 创建模板文件与空目录；已存在则 no-overwrite / NO_OP | 覆盖已有正式内容；写入 `01_知识库/` |
| A2 | candidate → parse → validate → temp → validate → atomic replace | 长参数塞入复杂研究内容；失败后改写正式文件 |
| A3 | `check` / `status` / `doctor` / `reconcile`；只替换 Generated marker 内部 | 覆盖研究问题、范围、核心贡献、最终结论、人工审查结论、发布授权 |
| A4 | 隔离 CI 跑 research_project 测试与 disposable acceptance | 安装 MinerU/Lean/求解器/向量库；写入 production Source |

人工保留权：

- 研究问题和范围确认；
- 证据真实性审核；
- 结论确认；
- 审查缺陷处置；
- 正式发布；
- Knowledge 晋升；
- 数据远程处理授权。

自动化可以创建、检查、连接、派生、汇总和回滚，但不得代替上述研究判断。

---

## 6. 研究循环

```text
界定问题
→ 建立假设与可证伪条件
→ 收集支持和反对证据
→ 推理 / 建模 / 形式化
→ 设计验证与反例
→ 记录失败和决策
→ 严格审稿
→ 修订或推翻
→ 写作与成果一致性检查
→ 授权发布 / 知识沉淀
```

每轮必须明确“当前结论会被什么证据推翻”。没有反对证据搜索或边界分析的“完成”不满足博士级标准。

---

## 7. 负结果与失败路线

必须保留：

- 未找到证明及失败的关键步骤；
- 被反例推翻的猜想；
- 不可行、不可识别或数值不稳定的模型；
- 不优于基线的结果；
- 无法复现的实验；
- 相互冲突的文献；
- 被拒绝的设计方案及理由；
- 超出数据、许可证或伦理边界而终止的路线。

负结果写入 `negative_results.md`，并通过局部 ref 与 Claim / Decision / Assumption 关联。不得只写在聊天或 Generated 摘要中。

---

## 8. 严格审稿角色

v1.7 可以由同一 AI 按角色顺序执行；角色分离是检查清单分离，不等于已启用多 Agent。

| 角色 | 核心问题 | 典型阻断缺陷 |
| --- | --- | --- |
| Proof Reviewer | 量词、条件、逻辑、边界、反例是否正确 | 证明跳步、条件缺失、循环论证 |
| Evidence Reviewer | Claim 是否被来源准确支持 | 错引、版本错、推断冒充原文 |
| Model Reviewer | 假设、单位、求解、敏感性是否合理 | 单位错、不可识别、错误最优性解释 |
| Reproducibility Reviewer | 第三方能否重建结果 | 无锁定环境、缺数据 hash、手工步骤 |
| Formalization Reviewer | Lean statement 是否等价 | 弱化命题、遗漏假设、虚假 axiom |
| Editor | 论文、图、表、引用和贡献是否一致 | 数字漂移、过度声称、图文矛盾 |

每个 review 产出：审查范围、使用版本、发现、严重度、Evidence、要求动作、作者回复、处置状态和复核结论。v1.1 仅预留 `reviews/` 目录，不实现六类 reviewer 引擎。

---

## 9. 缺陷严重度与门禁

| 严重度 | 定义 | 发布动作 |
| --- | --- | --- |
| `BLOCKER` | 结论错误、数据/隐私违规、伪造证据或不可恢复成果 | 立即阻断 |
| `MAJOR` | 可能改变核心结论或复现性 | 修复并复核后才可发布 |
| `MINOR` | 不改变核心结论但影响清晰度/完整性 | 记录并在发布前处理或获明确接受 |
| `NOTE` | 改进建议 | 不阻断，保留决策 |

AI 不能自行把 `BLOCKER/MAJOR` 降级。作者回复不能替代 reviewer 复核。

---

## 10. 写作与成果一致性

正式写作必须建立以下连接：

| 论文元素 | 必须回到 |
| --- | --- |
| 核心主张 | Reviewed Claim–Evidence |
| 公式/定理 | 推导、来源或 Lean artifact |
| 数值 | 不可变 run、指标定义和输出 hash |
| 图 | Figure manifest、Claim、run、代码和数据 |
| 表 | 生成脚本/数据、单位和统计定义 |
| 引用 | 已核对的文献身份和版本 |
| 方法 | 代码版本、配置、假设和适用范围 |
| 补充材料 | 与主文版本和 commit 一致 |
| PDF | P9 build 记录和发布 hash |

禁止手工把结果数字复制到多处后独立维护。能够生成的表格和指标应从同一 Reviewed artifact 生成；无法自动生成时执行逐项 consistency review。v1.1 不改变 P9 / ElegantBook / Normal Operation 发布语义。

---

## 11. 学术写作要求

- 摘要和结论只包含正文已支持的结果；
- “首次”“显著”“证明”“最优”等强词必须满足相应 Evidence；
- 相关工作不只列举，还比较问题、假设、方法、数据、理论、实验和结果；
- 方法写到独立研究者可复现的程度；
- 限制和负结果不得藏在内部记录而从论文删除；
- 统计结果报告效应量、不确定性和样本量，不只报告显著性；
- 图表和表格在正文中解释其研究含义，而不是只描述视觉现象；
- AI 辅助范围按治理规范披露，最终作者承担正确性和署名责任。

---

## 12. 知识晋升协议

研究项目的 Reviewed 内容不自动等于 Formal Knowledge。唯一允许路线是：

```text
DERIVED research material
→ 原文/模型/证明复核
→ REVIEWED project evidence
→ 人工确认可复用性与边界
→ 用户明确说“开始知识沉淀”
→ 按现有 Knowledge authoring / validator / indexer 工作流
→ FORMAL Knowledge
```

“审核通过”只表示内容审核通过，不授权 Knowledge creation、正式归档、LaTeX/PDF 发布或大规模长期记忆修改。任何晋升继续服从 `AGENTS.md` 的权限语义。

### 12.1 知识图谱与跨项目复用

跨项目复用优先连接已有 P/K/M ID、Reviewed Evidence ref、代码 run、Figure 和 Lean artifact，不创建第二套身份。关系视图由已验证 Source 派生，可重建且不得人工编辑。

复用时必须带出原始适用条件、反例、数据范围、版本和 review Evidence；不得只复制结论。至少多个真实项目出现稳定查询需求后，才允许为 Research Question、Claim、Evidence、Paper 或 Source 提出候选 Schema；任何候选设计都不得反向修改现有 Frozen Schema。

---

## 13. 权限与 Source Mutation

未经明确授权，不得：

- 正式归档、创建 Knowledge 或修改 Frozen Schema；
- 覆盖正式成果；
- 删除原始资料、失败 Evidence 或历史决策；
- 让 review、RAG 或 Agent 直接修改正式 Source；
- 将外部服务输出直接写入 `01_知识库/` 或 `08_成果输出/`；
- 因生成摘要而改变 Problem / Attempt / Method 的身份或 lifecycle；
- 伪造用户 Attempt、研究证据、引用、负结果或决策反转。

所有候选修改先写隔离位置，通过 validator 后按：

```text
candidate → parse → validate → temporary write → validate → atomic replace
```

失败时正式文件必须 byte-for-byte 不变。重复执行返回 `NO_OP` 或明确冲突。

---

## 14. 后续版本接口（不得改变十二步顺序）

| 版本 | v1.1 承载位置 |
| --- | --- |
| v1.2 MinerU | `documents/` |
| v1.3 Literature Evidence | `evidence.md` |
| v1.4 Modeling | `runs/` |
| v1.5 Figure | `artifacts/` |
| v1.6 Lean | `artifacts/` |
| v1.7 Review | `reviews/` |
| v1.8 Writing/P9 | Dossier + P9 |
| v2.0 RAG | Reviewed canonical records |
| v2.1 Multi-Agent | Candidate-only 输出 |

v1.1 只建立控制平面与导航接口，不实现上表后续能力。

---

## 15. v1.1、v1.7、v1.8 Gate

### v1.1

```yaml
gate_id: "v1.1/research-project-dossier"
baseline: "tag v1.0.1-foundation-portability-verified @ 140d01b011ac3b68f3177b9dabcb33b796a6b298; pytest 620 passed; core PASS; workspace CURRENT"
metric:
  - "duplicate_fixture_detection_rate"
  - "decision_history_overwrite_count"
  - "unauthorized_knowledge_create_count"
  - "attempt_pollution_count"
  - "official_file_byte_stability_on_failed_write"
threshold:
  duplicate_fixture_detection_rate: "100% on fixed fixtures (duplicate refs, exact duplicated canonical blocks, dossier full-block copies)"
  decision_history_overwrite_count: 0
  unauthorized_knowledge_create_count: 0
  attempt_pollution_count: 0
  official_file_byte_stability_on_failed_write: "byte-for-byte unchanged"
fixture:
  ref: "tests/research_project fixtures + disposable acceptance project"
  sha256: "recorded per fixture file in plan / test assets"
evidence:
  - "pytest tests/research_project"
  - "dossier-smoke workflow"
  - "optional ASEAN pilot records under 07_项目/ after human review"
failure_action: "BLOCK v1.1 closure; no tag; keep failing tests; do not weaken thresholds"
```

“重复事实检出率 100%”只适用于：固定 fixture 中的重复 ref、规范化后完全重复的 canonical block、Dossier 对 canonical block 的完整复制、固定评测集定义的重复事实。不得声称能识别所有自然语言语义改写。

真实 Pilot 必须使用仓库已有资料或用户明确提供内容；材料不足时只允许 disposable fixture 或经授权的空 scaffold，最终报告 `FRAMEWORK PASS / REAL PILOT PENDING`，不得虚报 Pilot PASS。

### v1.7

- 六类 reviewer 均有固定缺陷 fixture；
- `BLOCKER/MAJOR` 检出率 `100%`；
- 未复核的 `BLOCKER/MAJOR` 进入发布候选次数 `0`；
- review、作者回复、处置和复核 provenance 完整率 `100%`。

### v1.8

- 核心主张、数字、图、表和引用 provenance 覆盖率 `100%`；
- 故意制造的数字/图文/版本漂移检出率 `100%`；
- 正式 PDF 均由 P9 发布，旁路发布次数 `0`；
- AI 贡献披露和作者责任记录完整率 `100%`；
- 未经 `开始知识沉淀` 授权创建 Knowledge 的次数 `0`。
