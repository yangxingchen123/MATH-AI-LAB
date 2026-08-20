# MATH-AI-LAB 研究工作流、审稿与写作规范

**状态：** Candidate
**上位契约：** [博士级数学研究工作台总架构](2026-08-20-doctoral-research-workbench-design.md)
**对应版本：** v1.1、v1.7、v1.8

---

## 1. 目标

本规范定义从研究问题到可发布成果的人工可审计工作流，重点解决事实重复、负结果丢失、AI 草稿越权晋升和论文各产物不一致。

它不创建新的 Frozen Research Schema。第一阶段使用项目内 Markdown、manifest 和明确引用；只有真实使用证明稳定后，才另行讨论是否需要新 Schema。

`negative_results.md`、`governance.md` 与本节 **Research Record Grammar** 均为 **v1.1 项目级 Candidate Contract**，不是 Frozen Schema，也不是全局 P/K/A/M Registry。

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

生产 CLI 写入路径必须位于仓库 `07_项目/` 下；不得把 `_模板` 当作正式项目；拒绝 `..` 逃逸；解析后不得落到 `01_知识库/`、`11_学习证据/` 或其他 Source 根。测试允许 disposable repo root。

### 2.1 `research_dossier.md`（导航与摘要，不是事实源）

Dossier 只保留：

- 研究问题与范围摘要（人工 Source；工具不得覆盖）；
- 当前阶段和阻断项；
- 最重要的已审核发现导航；
- canonical 文件链接；
- documents / runs / artifacts / reviews 导航；
- Generated 区内由确定性规则派生的导航摘要与“下一步候选”。

Dossier **不是**事实源。不得复制完整 RESEARCH-RECORD。`reconcile` 只能替换：

```markdown
<!-- MATH-AI-LAB:RESEARCH-DOSSIER GENERATED BEGIN -->
...
<!-- MATH-AI-LAB:RESEARCH-DOSSIER GENERATED END -->
```

marker 缺失、嵌套、顺序错误或损坏时必须拒绝写入。

Generated “下一步候选”**仅**允许由下列确定性规则产生，不得推断研究方向、修改研究范围或生成学术结论：

1. 无 Evidence 的 Claim；
2. 未分类 / 缺稳定引用或 hash 的外部 Source；
3. 未处理的 Governance 外部处理阻断导航；
4. Active Assumption 缺少影响关系；
5. Dossier Generated 相对 canonical 为 stale。

### 2.2–2.6 事实源文件

| 文件 | 事实源角色 | 记录类型 |
| --- | --- | --- |
| `assumptions.md` | 假设 | `ASSUMPTION` (`ASM-####`) |
| `evidence.md` | Claim 与 Evidence **同文件分记录** | `CLAIM` (`CLM-####`) 与 `EVIDENCE` (`EVD-####`) |
| `decisions.md` | append-only 决策 | `DECISION` (`DEC-####`) |
| `negative_results.md` | 负结果 | `NEGATIVE_RESULT` (`NEG-####`) |
| `governance.md` | 项目治理 + AI Contribution | `GOVERNANCE`（每项目一条）+ `AI_CONTRIBUTION`（可多条） |

`evidence.md` 内 CLM 与 EVD 仅靠 RESEARCH-RECORD marker 分离。CLM 通过 `evidence_refs` 列出 EVD；EVD 通过 `claim_ref` 指向唯一 CLM，并用 `polarity` / `kind` 分类。创建 Claim 必须走授权操作 `add_claim`，不得要求用户只能手改正式文件。

### 2.7 承载目录

| 目录 | 后续版本 |
| --- | --- |
| `documents/` | v1.2 |
| `runs/` | v1.4 |
| `artifacts/` | v1.5 / v1.6 |
| `reviews/` | v1.7 |

---

## 3. Research Record Grammar（Candidate Contract）

### 3.1 边界（唯一切分依据）

每条记录必须使用成对 marker，**禁止**仅用 `##` 标题切块。正文内出现任意 Markdown 标题不得截断记录。

```text
<!-- MATH-AI-LAB:RESEARCH-RECORD type=<TYPE> ref=<REF> BEGIN -->
<metadata lines>
<body>
<!-- MATH-AI-LAB:RESEARCH-RECORD type=<TYPE> ref=<REF> END -->
```

规则：

- `TYPE` ∈ `ASSUMPTION | CLAIM | EVIDENCE | DECISION | NEGATIVE_RESULT | GOVERNANCE | AI_CONTRIBUTION`；
- `REF`：ASM/CLM/EVD/DEC/NEG 使用 `PREFIX-####`；`GOVERNANCE` 固定 `GOV-0001`；`AI_CONTRIBUTION` 使用 `AIC-####`；
- BEGIN 与 END 的 `type`/`ref` 必须完全一致；
- 同一文件内同类型 ref 唯一；不同类型不得共用同一字符串；
- metadata：每行 `- key: value`（key 小写蛇形）；未知必填键 → 校验失败；
- 第一个不以 `- ` 开头且非空的行起为 body（允许 body 内含 `##`）；
- 省略可选键 = 该键不存在；空字符串 value 非法（应省略或给显式枚举）；
- Unicode：NFC；fixture 与比较默认 **LF** 字节；append-only 对 Decision 记录做 **byte-for-byte** 比较（不做空白折叠）；
- 其他比较（duplicate fixture）可在规范化后再比，但规范必须写明所用规范化。

### 3.2 必填 / 可选键与枚举

| TYPE | 必填键 | 可选键 | 枚举 |
| --- | --- | --- | --- |
| ASSUMPTION | `status`, `scope`, `rationale`, `falsifiable_when` | `impacts`, `supersedes`, `superseded_by`, `reviewed` | `status`: `ACTIVE`/`SUPERSEDED`/`RETIRED` |
| CLAIM | `status` | `evidence_refs`（逗号分隔 EVD） | `status`: `OPEN`/`SUPPORTED`/`CONTESTED`/`WITHDRAWN` |
| EVIDENCE | `claim_ref`, `polarity`, `kind` | `source_citation`, `source_sha256` | `polarity`: `SUPPORT`/`OPPOSE`/`LIMIT`；`kind`: `QUOTE`/`PARAPHRASE`/`INFERENCE`/`COMPUTATION` |
| DECISION | `date`, `question`, `options`, `choice`, `basis`, `cost`, `reversible`, `revisit_when` | `opposes`, `evidence_refs`, `supersedes` | `reversible`: `true`/`false`；`date`: `YYYY-MM-DD` |
| NEGATIVE_RESULT | `status`, `failed_route`, `failure_evidence_refs`, `impact`, `retry_when` | `related_claims`, `related_decisions` | `status`: `OPEN`/`CLOSED` |
| GOVERNANCE | `project_data_level`, `external_processing_authorized` | `license_status`, `notes` | `project_data_level`: `PUBLIC`/`PERSONAL`/`RESTRICTED`；`external_processing_authorized`: `true`/`false` |
| AI_CONTRIBUTION | `date`, `role`, `summary`, `human_review` | `tools` | `human_review`: `PENDING`/`ACCEPTED`/`REJECTED` |

外部 Source：若 `kind` 为 `QUOTE`/`PARAPHRASE`，必须具备 `source_citation` 或 `source_sha256` 至少一个。

### 3.3 合法 / 非法示例

**合法 ASSUMPTION**

```markdown
<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0001 BEGIN -->
- status: ACTIVE
- scope: HT 情景港口吞吐
- rationale: 公开统计摘要
- falsifiable_when: 港口官方数据与假设冲突
- impacts: CLM-0001

港口日吞吐上界为已知公开值。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0001 END -->
```

**非法 ASSUMPTION（缺 `falsifiable_when`）**

```markdown
<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0002 BEGIN -->
- status: ACTIVE
- scope: x
- rationale: y

正文
<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0002 END -->
```

**合法 CLAIM + EVIDENCE（同文件）**

```markdown
<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0001 BEGIN -->
- status: OPEN
- evidence_refs: EVD-0001

Split-flow 可降低峰值拥堵。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0001 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0001 BEGIN -->
- claim_ref: CLM-0001
- polarity: SUPPORT
- kind: INFERENCE
- source_citation: project-note:2026-08-20

在既有约束叙述下，分流可降低单港峰值。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0001 END -->
```

**非法 EVIDENCE（缺 polarity）** — BEGIN/END 齐全但 metadata 缺键，Validator FAIL。

**合法 DECISION / NEG / GOVERNANCE / AI_CONTRIBUTION** — 必须含上表必填键；Decision 历史只追加；Governance 模板默认：

```markdown
<!-- MATH-AI-LAB:RESEARCH-RECORD type=GOVERNANCE ref=GOV-0001 BEGIN -->
- project_data_level: PERSONAL
- external_processing_authorized: false
- license_status: not_applicable_local_only
- notes: 默认最小化外部处理；升级 PUBLIC/授权前保持本地研究

项目默认按 PERSONAL 处理，未授权外部处理。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=GOVERNANCE ref=GOV-0001 END -->
```

默认 `PERSONAL` + `external_processing_authorized: false` 的理由：新项目在许可与数据边界确认前采用最小暴露；该状态 **合法**，不得因此使整个 `validate_project` 失败。

**合法 AI_CONTRIBUTION**

```markdown
<!-- MATH-AI-LAB:RESEARCH-RECORD type=AI_CONTRIBUTION ref=AIC-0001 BEGIN -->
- date: 2026-08-20
- role: drafting-assistant
- summary: 起草 assumption 候选
- human_review: PENDING
- tools: cursor-agent

待人工审核后写入正式结论。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=AI_CONTRIBUTION ref=AIC-0001 END -->
```

AI Contribution 在 v1.1 通过 `update_governance` candidate（可含 GOVERNANCE 与/或 AI_CONTRIBUTION 记录集，但 **每个 candidate 文件仍只含一条 record**；多条需多次操作）写入；无独立远程上传。人工审核权限保留在人类。

---

## 4. 项目内局部引用

```text
ASM-0001  CLM-0001  EVD-0001  DEC-0001  NEG-0001  GOV-0001  AIC-0001
```

只在单项目内唯一；不创建全局 Registry；不改变 P/K/A/M；不与 Attempt ID 混用；非 Frozen。

---

## 5. 研究状态（导航，非 Schema）

```text
FRAMING → EVIDENCE_GATHERING → MODELING_OR_PROVING
        → VALIDATION → REVIEW → WRITING → RELEASED
```

---

## 6. 四级自动化与授权写入

```text
A1 init
A2 atomic candidate ops
A3 check / status / doctor / reconcile / assess_external_processing
A4 dossier-smoke CI（含 append-only PR guard）
```

### 6.1 init

| 目标状态 | 结果 |
| --- | --- |
| 不存在 | 完整 scaffold 一次性落地 → `WRITTEN` |
| 已是完整合法 scaffold | 不覆盖 → `NO_OP` |
| 存在但不完整或冲突 | `REJECTED`，**零文件变化**（不得静默半补齐） |

### 6.2 candidate 操作（每次恰好一条 record）

`add_assumption` · `supersede_assumption` · `add_claim` · `add_evidence` · `append_decision` · `record_negative_result` · `update_governance`

规则：ref 已存在且规范化后内容相同 → `NO_OP`；ref 已存在且内容不同 → `REJECTED`；不自动分配 ref；candidate 不得是正在替换的 official 路径；parse/post-validate 失败 → official **byte-for-byte** 不变。

CLI 对应：`add-assumption`、`supersede-assumption`、`add-claim`、`add-evidence`、`append-decision`、`record-negative-result`、`update-governance`、`reconcile`、`init`；只读：`check`、`status`、`doctor`、`check-append-only`。

### 6.3 Governance 与外部处理

- `validate_project`：结构、语法、关系、Generated 边界；**不**因 `RESTRICTED`/`PERSONAL` + 未授权而整体 FAIL。
- `assess_external_processing`：返回 `ALLOWED` 或 `BLOCKED`；未授权时阻断外部处理能力；本地只读与允许的本地研究仍可进行。
- 缺 `project_data_level` → `validate_project` FAIL。
- 外部 asset 缺许可状态 → 该 asset 不得进入正式外部处理。
- v1.1 **无**真实远程上传代码。

人工保留权：问题与范围、证据真实性、结论、审查处置、正式发布、Knowledge 晋升、远程处理授权。

---

## 7. 研究循环与负结果

（同前：界定问题 → 假设 → 证据 → 推理/建模 → 验证 → 记录失败与决策 → 审稿 → 写作 → 授权发布。）

负结果写入 `negative_results.md`，不得只存在于聊天或 Generated。

---

## 8–12. 审稿、缺陷、写作、知识晋升、权限

v1.7 六类 reviewer 与严重度门禁保持不变；v1.1 只预留 `reviews/`。

知识晋升仍需用户明确说「开始知识沉淀」。Source mutation：

```text
candidate → parse → validate_project → temporary write → validate_project → atomic replace
```

领域结果类型（不得复用 Normal Operation 对象）：

- `ResearchProjectOperationResult`
- `ResearchProjectValidationResult`
- `ResearchProjectStatusResult`
- `ExternalProcessingAssessment`

---

## 13. 后续版本接口

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

---

## 14. v1.1 / v1.7 / v1.8 Gate

### v1.1（与 capability roadmap 指标名完全一致）

```yaml
gate_id: "v1.1/research-project-dossier"
baseline: "tag v1.0.1-foundation-portability-verified @ 140d01b011ac3b68f3177b9dabcb33b796a6b298; pytest 620 passed; verification core PASS; workspace CURRENT / 0 ERROR / 0 WARNING"
metric:
  - project_scaffold_completeness_rate
  - duplicate_fixture_detection_rate
  - append_only_fixture_detection_rate
  - decision_history_overwrite_count
  - failed_write_byte_stability_rate
  - unauthorized_knowledge_create_count
  - attempt_pollution_count
  - dossier_generated_boundary_violation_count
  - unauthorized_external_processing_block_rate
threshold:
  project_scaffold_completeness_rate: "100%"
  duplicate_fixture_detection_rate: "100%"
  append_only_fixture_detection_rate: "100%"
  decision_history_overwrite_count: 0
  failed_write_byte_stability_rate: "100%"
  unauthorized_knowledge_create_count: 0
  attempt_pollution_count: 0
  dossier_generated_boundary_violation_count: 0
  unauthorized_external_processing_block_rate: "100%"
fixture:
  ref: "07_项目/_模板/研究项目_v1.1 + tests/research_project/fixtures + tests/research_project/fixtures/SHA256SUMS"
  sha256: "each fixture file hash listed in SHA256SUMS; integrity test enforces exact match"
evidence:
  - "pytest tests/research_project"
  - ".github/workflows/dossier-smoke.yml including check-append-only --all"
  - "optional reviewed ASEAN pilot under 07_项目/ after human authorization"
failure_action: "BLOCK v1.1 closure and tagging; keep failing tests; do not weaken thresholds; do not install Sidecar deps to force a pass"
```

指标释义：

- `append_only_fixture_detection_rate=100%`：修改/删除/重排/插入/空白变化等固定违规 fixture 全部被发现；
- `decision_history_overwrite_count=0`：真实候选版本未覆写历史 Decision；
- `unauthorized_external_processing_block_rate=100%`：未授权外部处理请求全部 BLOCKED（**不是**项目 validate 失败率）；
- `duplicate_fixture_detection_rate` 仅覆盖固定 fixture（重复 ref、完全重复 block、Dossier 完整复制），不声称覆盖一切自然语言改写。

### v1.7 / v1.8

保持原强制 Gate（六类 reviewer；P9 唯一 PDF；Knowledge 需「开始知识沉淀」）。
