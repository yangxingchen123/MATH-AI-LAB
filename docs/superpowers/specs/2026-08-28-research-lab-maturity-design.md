# MATH-AI-LAB 研究实验室成熟度（v2.2-lab Pilot）

**状态：** Candidate
**上位契约：** [博士级数学研究工作台总架构](2026-08-20-doctoral-research-workbench-design.md)
**对应版本：** v2.2-lab Pilot（**不是** v2.2 Doctoral Workbench Closure）
**触发：** 2026-08-28 顶刊级审读方案落地；禁止按公开仓库快照一次性重构。

---

## 1. 目标与非目标

本 Pilot 把审读方案中的 **L0–L2 可执行切片**接到现有目录与 Candidate Contract 上，而不是另起 `research/`、`formal/`、`experiments/` 平行树。

保留：Source / Generated / Workspace 分层；AI 研究 → AI 自检 → 人工审核 → 正式归档；证据分层；Frozen Schema 不可为当前任务改写。

**非目标：**

- 不宣称数学四大准备度、不承诺烧钱命中率；
- 不引入向量库、Prefect/Temporal、多机 GPU prover、Mathlib（P001-L1 触发）；
- 不关闭 v2.2 总架构；不把讲义产量、Lean 行数、pass@k 当研究 KPI；
- 不把 P001 形式化宣传为数学创新。

成功分层沿用审读方案的 S1–S5。本 Pilot 只验收 **S0 工程门禁 + 运行条件层 + 思路协议机检 + P001-L0 / sum-free 作为实例校准（可选）**。失败候选写入 journal，不得删除。优化系统时交付运行条件与协议，不交付又一道 P00xx。

---

## 2. 三轨映射（不得平行建树）

| 审读轨道 | 核心产物 | 本仓库落点 |
| --- | --- | --- |
| A. 数学发现 | 开放问题、猜想、人类证明、Dossier | `07_项目/`（`--kind research`）+ `02_题目库/` |
| B. Lean 验证 | 固定工具链、零 `sorry`、语义对照 | `06_LEAN形式化/` + `tools.lean_formalization` |
| C. ATP/智能体 | 成本台账、硬上限、evaluator、Candidate 编排 | `tools.research_lab` + 既有 `tools.collaboration`（Candidate only） |

B/C 不能替代 A 的数学原创性。竞赛整卷仍不进 `02_题目库/`。

---

## 3. 成熟度对照（审读 L0–L6 ↔ 既有版本）

| 审读等级 | 既有能力 | 本 Pilot |
| --- | --- | --- |
| L0 学习工作台 | Foundation + P001 闭环 | 保持；进度页仍只记判断，清单由 inventory 派生 |
| L1 可复现实验室 | v1.4 modeling runs | inventory + sum-free evaluator + 成本硬上限 |
| L2 形式化实验室 | v1.6 Lake 工程 | P001-L0 整数二次共轭；sum-free 奇数构造、`[1,2,3]` 反例与配对上界（DISC-003–006）；Mathlib 仍为 `none` |
| L3–L6 | v2.0–v2.2 路线 | **不做**；有客观 evaluator 且专家选题后再升级 |

---

## 4. Lean 双层政策

- **普通学习问答：** Lean 可选，失败不阻断 Core。
- **可形式化的发表关键引理、有限枚举、代数恒等式、组合证书、高风险边界：** 默认要求走 `06_LEAN形式化/`，正式目标零 `sorry` / `admit` / 未说明 `axiom`。
- **暂不适合 Lean 的深层分析证明：** 先人类证明与局部形式化；禁止为形式化率扭曲研究方向。

P001 分层：

| 层 | 内容 | 本 Pilot |
| --- | --- | --- |
| L0 | 二次函数共轭的整数代数骨架（Fenchel–Young、达到、等号、`p<0` 仍有限） | **交付** |
| L1 | Mathlib `Real` / `ConvexOn` 接口 | 触发：需要 ℝ 上界或与 mathlib 定义对齐时 |
| L2 | statement-fidelity 扰动集 | **交付检测器**；不接外部模型 |

---

## 5. 目录与触发阈值

不创建审读文中的平行根目录。升级触发：

| 能力 | 现在 | 何时升级 |
| --- | --- | --- |
| 元数据 | YAML + 现有 Dossier | >10 万任务或多人并发才换 PostgreSQL |
| 检索 | 既有 v2.0 FTS/BM25/RRF | >5000 定理段落且不够用才加向量 |
| 工作流 | Python CLI + Actions | 每日 >1000 长任务才上调度器 |
| Mathlib | 未加入 | P001-L1 或研究引理依赖 mathlib 定义时，单独 PR 钉 commit |

---

## 6. Gate（v2.2-lab）

```yaml
gate_id: "v2.2-lab/research-lab-pilot"
baseline: "v1.6 Lean FRAMEWORK PILOT + stdlib-only Python Core"
metric:
  - inventory_key_roots_present
  - ledger_hard_cap_block_rate
  - ledger_cache_hit_no_double_charge
  - sum_free_known_bound_reproduced
  - fidelity_mutant_detection_rate
  - quadratic_correspondence_present
  - sidecar_core_failure_count
  - blind_search_recovers_known_bound
  - failure_journal_retains_rejects
  - exhaustive_bound_holds
  - sum_free_upper_bound_correspondence
  - operating_preflight_pass
  - protocol_contract_present
  - stage_machine_legal
  - cost_funnel_caps_present
  - deterministic_cycle_zero_usd
  - evidence_chain_reproducible
  - literature_fields_present
  - stop_contract_present
  - journal_blocks_paper_without_pi
  - prior_art_matrix_present
  - funnel_clusters_failures
  - tool_first_contract_present
  - original_backlog_closed
  - lab_kernel_post40
threshold:
  inventory_key_roots_present: "100%"
  ledger_hard_cap_block_rate: "100%"
  ledger_cache_hit_no_double_charge: "100%"
  sum_free_known_bound_reproduced: "100%"
  fidelity_mutant_detection_rate: "100%"
  quadratic_correspondence_present: 1
  sidecar_core_failure_count: 0
  blind_search_recovers_known_bound: "100%"
  failure_journal_retains_rejects: "100%"
  exhaustive_bound_holds: "100%"
  sum_free_upper_bound_correspondence: 1
  operating_preflight_pass: "100%"
  protocol_contract_present: "100%"
  stage_machine_legal: "100%"
  cost_funnel_caps_present: "100%"
  deterministic_cycle_zero_usd: "100%"
  evidence_chain_reproducible: "100%"
  literature_fields_present: "100%"
  stop_contract_present: "100%"
  journal_blocks_paper_without_pi: "100%"
  prior_art_matrix_present: "100%"
  funnel_clusters_failures: "100%"
  tool_first_contract_present: "100%"
  original_backlog_closed: "100%"
  lab_kernel_post40: "100%"
failure_action: "BLOCK v2.2-lab Pilot closure; keep failing tests; do not claim 四大 or v2.2 VERIFIED"
```

Lean Sidecar 不可用时：`quadratic_correspondence_present` 与 `sum_free_upper_bound_correspondence` 仍检查 YAML/源文件；`operate` 的 lean 为 DEGRADED；`verify` 的 `lake build` 继续 DEGRADED，**不得**让 Core 失败。

---

## 7. 两层：运行条件 vs 实例校准

| 层 | 入口 | 失败含义 |
| --- | --- | --- |
| 运行条件 | `python -m tools.research_lab operate` | 实验室不能安全开工（缺根目录、协议坏、Frozen Schema 文件缺失） |
| 思路 | `protocol` / `route` / `check-session` | 当前会话跳过重构、用证明链写建模、infra 去开新 P、卡住却不写障碍、宣称已证却仍卡住 |
| 研究循环 | `cycle` / `advance` / `reproduce` / `funnel` | 状态机非法跳转、漏斗超限、evaluator 拒绝、证据链指纹对不上 |
| 投稿门禁 | `journal` / `prior-art-matrix` | G0–G6 未过；无 Human PI；先验矩阵为空 |
| 实例校准 | `verify` | P001 / sum-free 演示回归；**不是**系统本体 |

`operate` 不得 import sum-free / P001 源。infra 任务禁止新 Problem、新 Lean 定理。

---

## 8. 明确不做（本 Pilot）

外部 LLM 调用、专用 prover、SAT/SMT 证书重放、LeanBlueprint 网站、独立复现容器、领域专家真人签字流程、开放问题的新颖性宣传、宣称四大。

## 9. P1 脚手架（不是 L5 / 四大）

审读方案第 4–6 个月与 P1 中、可在无模型无 Mathlib 时先做的系统切片：

- G0–G6 投稿门禁机检；S1 已知题必须 `paper_ready: false` 且 `claims_四大: false`
- Human PI 不得把最终判断外包；`EXTERNAL_REVIEWED` / `PAPER_READY` 需要 `human_pi_signoff`
- prior-art 关系矩阵（same / special_case / corollary / similar_method / numeric_only / unknown）
- C0 廉价确定性候选漏斗：失败原因聚类、连续无改进则停、0 USD 时不报告 cost-adjusted success
- 工具优先：evaluator / `simp` / `ring` 能过则禁止再调昂贵模型

P1 其余项（专用 Lean 模型、前沿模型、Mathlib、SAT、Prefect、LeanBlueprint 网站）以 **UNPLUGGED / policy** 插座关闭，由 `python -m tools.research_lab backlog` 机检，不假装已接入、不宣称四大。

最初 90 天 40 项（P0.1–P2.40）全部有决议：done、sidecar（inventory 旁路，永不写 `项目进度.md`）、unplugged 或 policy。

## 10. 40 项之后的实验室内核（仍不是四大）

审读 §7.3 / §6.7 / §10.5 / §16 中、无模型也可做的部分：

- 任务对象 schema（`check-task`）
- 引理依赖图必须无环（`lemma-graph`；不是 LeanBlueprint 网站）
- 局部修复只换候选、禁止改陈述；`out_of_universe` 不得重试（`repair`）
- 风险登记册机检（陈述漂移、新颖性幻觉、预算爆炸、评价器投机）
- 成本报表：0 USD 不计算 cost-adjusted success

入口：`python -m tools.research_lab risks`
