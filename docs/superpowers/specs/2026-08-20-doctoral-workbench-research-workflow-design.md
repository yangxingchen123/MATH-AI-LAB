# MATH-AI-LAB 研究工作流、审稿与写作规范

**状态：** Candidate
**上位契约：** [博士级数学研究工作台总架构](2026-08-20-doctoral-research-workbench-design.md)
**对应版本：** v1.1、v1.7、v1.8

---

## 1. 目标

本规范定义从研究问题到可发布成果的人工可审计工作流。它不创建 Frozen Research Schema。`negative_results.md`、`governance.md` 与 **Research Record Grammar** 均为 **v1.1 项目级 Candidate Contract**。

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

项目身份 = 目录路径。生产 CLI 写入必须在 `07_项目/` 下；排除把 `_模板` 当作正式项目；拒绝 `..` 逃逸与落入 `01_知识库/` / `11_学习证据/`。测试可用 disposable repo root。

### 2.1 Dossier（导航，非事实源）

人工区：研究问题、范围、人工结论。Generated 区仅：

```markdown
<!-- MATH-AI-LAB:RESEARCH-DOSSIER GENERATED BEGIN -->
...
<!-- MATH-AI-LAB:RESEARCH-DOSSIER GENERATED END -->
```

`render_generated_dossier` 是只依赖 canonical facts 的纯函数，可写入 canonical input fingerprint。`dossier_is_stale` 比较当前 Generated 与 expected render。**不得**把 “stale / RECONCILE_REQUIRED” 写入 expected Generated（否则 reconcile 后立刻再 stale）。`RECONCILE_REQUIRED` 只由 `status` / `doctor` / 操作结果报告。reconcile 成功后 `dossier_is_stale == false`；连续第二次 reconcile → `NO_OP`；人工区 byte-for-byte 不变。

Generated “下一步候选”仅允许确定性规则（不得推断研究方向或学术结论）：

1. 无 Evidence 的 Claim；
2. 未分类 / 缺稳定引用或 hash 的外部 Source；
3. Governance 外部处理预检为 BLOCKED 的导航提示；
4. Active Assumption 缺少影响关系。

（stale 提示是 operational status rule，不进入 expected Generated。）

### 2.2–2.6 事实源

| 文件 | 记录 |
| --- | --- |
| `assumptions.md` | `ASSUMPTION` |
| `evidence.md` | `CLAIM` + `EVIDENCE`（marker 分离） |
| `decisions.md` | `DECISION`（append-only） |
| `negative_results.md` | `NEGATIVE_RESULT` |
| `governance.md` | 单条 `GOVERNANCE`=`GOV-0001` + 多条 `AI_CONTRIBUTION` |

### 2.7 后续目录接口

`documents/`→v1.2 · `runs/`→v1.4 · `artifacts/`→v1.5/v1.6 · `reviews/`→v1.7

---

## 3. Research Record Grammar（Candidate Contract）

### 3.1 唯一语法

```text
<!-- MATH-AI-LAB:RESEARCH-RECORD type=<TYPE> ref=<REF> BEGIN -->
<metadata lines>
---
<body>
<!-- MATH-AI-LAB:RESEARCH-RECORD type=<TYPE> ref=<REF> END -->
```

规则：

- `---` **强制**分隔 metadata 与 body（不是 YAML Schema）；
- body 可含标题、列表、冒号及任意普通 Markdown；body 内 `##` / `- list` **不得**截断记录；
- 只许用成对 BEGIN/END 切分；orphan、nested、重复 BEGIN、缺 END、BEGIN/END 的 type/ref 不一致 → FAIL；
- metadata：`- key: value`；key 必须属于该 TYPE 的 required∪optional；未知 key、重复 key、空 value、非法 key 格式、缺必填 → FAIL；
- TYPE ↔ ref 前缀必须匹配；`GOVERNANCE` **只能** `GOV-0001`（`GOV-0002` 等一律拒绝）；
- Unicode NFC；fixture **LF**；Decision append-only 为 **byte-for-byte**（不做空白折叠）。

### 3.2 键与枚举

| TYPE | 必填 | 可选 | 枚举 |
| --- | --- | --- | --- |
| ASSUMPTION | status, scope, rationale, falsifiable_when | impacts, supersedes, superseded_by, reviewed | status: ACTIVE/SUPERSEDED/RETIRED |
| CLAIM | status | evidence_refs | status: OPEN/SUPPORTED/CONTESTED/WITHDRAWN |
| EVIDENCE | claim_ref, polarity, kind | source_citation, source_sha256 | polarity: SUPPORT/OPPOSE/LIMIT；kind: QUOTE/PARAPHRASE/INFERENCE/COMPUTATION |
| DECISION | date, question, options, choice, basis, cost, reversible, revisit_when | opposes, evidence_refs, supersedes | reversible: true/false；date: YYYY-MM-DD |
| NEGATIVE_RESULT | status, failed_route, failure_evidence_refs, impact, retry_when | related_claims, related_decisions | status: OPEN/CLOSED |
| GOVERNANCE | project_data_level, external_processing_authorized, license_status | notes | project_data_level: PUBLIC/PERSONAL/RESTRICTED；external_processing_authorized: true/false；license_status: UNKNOWN/LOCAL_ONLY/VERIFIED_FOR_EXTERNAL_PROCESSING |
| AI_CONTRIBUTION | date, role, summary, human_review | tools | human_review: PENDING/ACCEPTED/REJECTED |

QUOTE/PARAPHRASE 至少需要 `source_citation` 或 `source_sha256` 之一。

模板默认 GOVERNANCE：

```text
project_data_level: PERSONAL
external_processing_authorized: false
license_status: LOCAL_ONLY
```

理由：新项目在许可与边界确认前最小暴露；该状态合法，不得使 `validate_project` 失败。

### 3.3 示例（均含 `---`）

**合法 ASSUMPTION**

```markdown
<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0001 BEGIN -->
- status: ACTIVE
- scope: HT 情景港口吞吐
- rationale: 公开统计摘要
- falsifiable_when: 港口官方数据与假设冲突
- impacts: CLM-0001
---
港口日吞吐上界为已知公开值。

## 备注
- 可含列表与冒号: 如本行
<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0001 END -->
```

**非法 ASSUMPTION（缺 falsifiable_when）** — 有 BEGIN/END/`---` 但缺必填键 → FAIL。

**合法 CLAIM（新建，无 evidence_refs）**

```markdown
<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0001 BEGIN -->
- status: OPEN
---
Split-flow 可降低峰值拥堵。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0001 END -->
```

**合法 EVIDENCE**

```markdown
<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0001 BEGIN -->
- claim_ref: CLM-0001
- polarity: SUPPORT
- kind: INFERENCE
- source_citation: project-note:2026-08-20
---
在既有约束叙述下，分流可降低单港峰值。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0001 END -->
```

**合法 GOVERNANCE / AI_CONTRIBUTION / DECISION / NEG** — 同样强制 `---`；GOVERNANCE ref 必须为 `GOV-0001`。

---

## 4. Claim–Evidence 闭环（唯一方案）

1. `add_claim`：`evidence_refs` 必须省略或为空，不得引用尚不存在的 EVD。
2. `add_evidence` candidate 仅一条 EVD；`claim_ref` 必须指向已存在 CLM。
3. 同一次 `evidence.md` 原子替换：追加 EVD，并**确定性**更新该 CLM 的 `evidence_refs`（去重 + 稳定排序，例如按 EVD 编号升序）。
4. Validator：每个 EVD→存在的 CLM；每个 CLM 列出的 EVD 存在；EVD.`claim_ref` 与 CLM backlink 一致；每个 EVD 出现在其 CLM 的 `evidence_refs`。
5. `add_evidence` **不得**自动把 Claim `status` 改为 `SUPPORTED`/`CONTESTED`。
6. 任一步失败 → 整个 `evidence.md` byte-for-byte 不变。

---

## 5. 操作分类

### 5.1 Add-only

`add_assumption` · `add_claim` · `add_evidence` · `append_decision` · `record_negative_result` · `update_governance` 的 **AI_CONTRIBUTION** 分支

对目标 record：同 ref 且规范化内容相同 → `NO_OP`；同 ref 内容不同 → `REJECTED`；新 ref → 验证后 `WRITTEN`。

### 5.2 Controlled-transition

`supersede_assumption` · `update_governance` 的 **GOVERNANCE** 分支 · `reconcile_project`（仅 Generated 区）

### 5.3 `update_governance`

- candidate **每次恰好一条** Record（禁止“可同时含 GOVERNANCE 与 AIC”）；
- GOVERNANCE candidate 必须 `GOV-0001`：相同 → `NO_OP`；不同但合法 → **只替换** GOV-0001，**保留**全部 AIC → `WRITTEN`；
- AI_CONTRIBUTION candidate → 仅追加，遵守 add-only；
- 失败 → `governance.md` byte-for-byte 不变。

### 5.4 Atomic 写入（现有接口）

```python
tools.source_io.atomic.atomic_replace_text(official_path: Path, candidate_text: str)
```

流程：parse 单 record candidate → 内存构造完整 prospective 文件 → disposable validation tree → `validate_project` → `atomic_replace_text`。最终替换前不得修改 official。

`init_project`：sibling staging 目录 → 完整 scaffold 校验 → destination 仍不存在二次检查 → 非覆盖 rename/publish → race/conflict → `REJECTED` + staging cleanup；不完整/冲突 destination → 零变化。不存在 → `WRITTEN`；完整合法 → `NO_OP`。

领域结果类型（禁止复用 Normal Operation）：`ResearchProjectOperationResult` · `ResearchProjectValidationResult` · `ResearchProjectStatusResult` · `ExternalProcessingAssessment`。

---

## 6. ExternalProcessingAssessment = PROJECT_POLICY_PREFLIGHT

v1.1 **不是** asset/provider/upload 授权完成证明。即使 `ALLOWED`，仍只表示项目级预检；后续 Sidecar 必须再做 asset/provider/purpose/retention 检查。v1.1 **无**远程上传代码。

| 条件 | 结果 |
| --- | --- |
| Governance 缺失/非法 | BLOCKED |
| `external_processing_authorized: false` | BLOCKED |
| `RESTRICTED` | BLOCKED（v1.1） |
| `PERSONAL` | BLOCKED（v1.1，尚无 provider/purpose/retention contract） |
| `PUBLIC` + authorized true + `VERIFIED_FOR_EXTERNAL_PROCESSING` | project-level ALLOWED |
| `PUBLIC` + authorized true + `UNKNOWN`/`LOCAL_ONLY` | BLOCKED |

`validate_project` **不**因 PERSONAL/RESTRICTED+未授权而 FAIL。缺 `project_data_level` / 非法枚举 → validate FAIL。

---

## 7. Decision append-only（含 `--all`）

`check_append_only_all(repo_root, base_ref)`：

- 解析 `base_ref` 为 commit；无效/未 fetch → FAIL（不得静默跳过）；
- 发现 base 与 current 的 `07_项目/<project>/decisions.md`（**排除** `_模板`）；
- 检查路径并集；
- base 无、current 新增 → empty base，允许只追加；
- base 有、current 删除文件或整项目 → FAIL；
- 重命名致旧路径消失 → FAIL（不得当新项目）；
- 历史 record 的改/删/重排/前插/记录内空白变化 → FAIL；仅尾部追加合法；
- Git path = repo-relative POSIX；subprocess 用参数列表，禁止拼 shell。

---

## 8. 四级自动化与 Gate evaluator

A1 init · A2 atomic ops · A3 check/status/doctor/reconcile/assess_external_processing/gate · A4 dossier-smoke。

只读 Gate：

```text
python -m tools.research_project gate --format json
```

对九项 metric 输出 numerator/denominator/value/threshold/PASS|FAIL/evidence；任一不达标非零退出；确定性 JSON；不写 production Source。`dossier-smoke` 必须执行并保存 artifact。

### v1.1 Gate（与 roadmap 同名）

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
  ref: "07_项目/_模板/研究项目_v1.1 + tests/research_project/fixtures/** (excl. SHA256SUMS self) + SHA256SUMS manifest"
  sha256: "SHA256SUMS lists every fixture regular file except itself; integrity test enforces set equality + binary hashes; text fixtures LF-only"
evidence:
  - "pytest tests/research_project"
  - "python -m tools.research_project gate --format json"
  - ".github/workflows/dossier-smoke.yml Gate JSON artifact"
  - "optional reviewed ASEAN pilot after human authorization"
failure_action: "BLOCK v1.1 closure and tagging; keep failing tests; do not weaken thresholds"
```

`unauthorized_external_processing_block_rate` fixtures 必须与 §6 真值表一一对应。

---

## 9. Fixture SHA256SUMS

- 覆盖 `tests/research_project/fixtures/**` 下除 `SHA256SUMS` **自身外**的全部 regular files；
- 无重复路径、无绝对路径、无 `..`；listed set ≡ 实际 file set；
- binary SHA-256；text fixture 另检无 CRLF；增删改 fixture 必须同步更新 manifest。

---

## 10. 审稿 / 写作 / 知识晋升 / 版本接口

v1.7 六类 reviewer 与 v1.8 P9/Knowledge 规则不变。后续版本接口表不变。Knowledge 仍需「开始知识沉淀」。
