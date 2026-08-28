# Research Project Usage Guide（v1.1）

本指南说明 `tools.research_project` 的生产用法。权威语法与操作语义以 `docs/superpowers/specs/2026-08-20-doctoral-workbench-research-workflow-design.md` §3 为准。

## CLI

只读：

```text
python -m tools.research_project check --project "<07_项目/Name>"
python -m tools.research_project status --project "<07_项目/Name>"
python -m tools.research_project doctor
python -m tools.research_project check-append-only --project "<07_项目/Name>" --base-ref <sha>
python -m tools.research_project check-append-only --all --base-ref <sha>
python -m tools.research_project assess-external-processing --project "<07_项目/Name>"
python -m tools.research_project gate --format json
python -m tools.research_project literature-gate --format json
```

写入：

```text
python -m tools.research_project init --project "<07_项目/Name>" --title "Title"
python -m tools.research_project init --project "<07_项目/Name>" --title "Title" --kind contest_modeling
python -m tools.research_project init --project "<07_项目/Name>" --title "Title" --kind literature
python -m tools.research_project add-assumption --project "<path>" --candidate "<file>"
python -m tools.research_project supersede-assumption --project "<path>" --ref ASM-0001 --candidate "<file>"
python -m tools.research_project add-claim --project "<path>" --candidate "<file>"
python -m tools.research_project add-evidence --project "<path>" --candidate "<file>"
python -m tools.research_project append-decision --project "<path>" --candidate "<file>"
python -m tools.research_project record-negative-result --project "<path>" --candidate "<file>"
python -m tools.research_project update-governance --project "<path>" --candidate "<file>"
python -m tools.research_project reconcile --project "<path>"
python -m tools.research_project add-literature --project "<path>" --candidate "<file>"
python -m tools.research_project add-novelty --project "<path>" --candidate "<file>"
python -m tools.research_project add-review --project "<path>" --candidate "<file>"
```

`add-claim` 的 candidate 不得引用尚不存在的 Evidence。`update-governance` 每次恰好一条 GOVERNANCE（`GOV-0001`）或一条 AI_CONTRIBUTION。`assess-external-processing` 只做 `PROJECT_POLICY_PREFLIGHT`，不是上传批准。

## Record Grammar

每条记录必须是：

```text
BEGIN marker
metadata lines
---
body
END marker
```

`---` 强制分隔 metadata 与 body。body 可含标题、列表与冒号。`GOVERNANCE` 只能是 `GOV-0001`。

## Generated 边界

`research_dossier.md` 的 Generated 区由 `reconcile` 重写；人工区 byte-for-byte 保留。`RECONCILE_REQUIRED` 只出现在 `status` / `doctor` / 操作结果中，不写入 Generated。

## Decision append-only

历史 Decision 记录禁止改、删、重排、前插或记录内空白变化。只允许尾部追加。`--all` 检查 `07_项目/` 下除 `_模板` 外的全部 `decisions.md`。

## Governance vs Assessment

`validate_project` 不因 PERSONAL/RESTRICTED 且未授权而失败。`assess-external-processing` 在 v1.1 中仅当 `PUBLIC` + authorized + `VERIFIED_FOR_EXTERNAL_PROCESSING` 时给出项目级 `ALLOWED`。AI 贡献通过 `update_governance` 追加 `AI_CONTRIBUTION`。

v1.1 不安装、不调用 MinerU / 求解器 / Lean / RAG。v1.3 文献身份、Novelty Matrix 与六类审稿记录是 Candidate Contract 扩展，仍不是 Frozen Schema。引用撤稿/更正文献必须 `acknowledges_status: true`。不得在没有可验证新增 Evidence 时使用「首次」「创新」「显著领先」。

建模框架（v1.4，标准库 Pilot，求解器不进根环境）：

```text
python -m tools.modeling doctor
python -m tools.modeling validate-manifest --path "<manifest.yaml>"
```

制图框架（v1.5，标准库 SVG/Mermaid，Matplotlib 不进根环境）：

```text
python -m tools.figure doctor
python -m tools.figure gate
python -m tools.figure validate-manifest --path "<manifest.yaml>"
python -m tools.figure render --family numerical --output "<dir>" --run-id "<run>"
```

Lean 形式化框架（v1.6；lake 未安装时 doctor=DEGRADED，不阻断 Core）：

```text
python -m tools.lean_formalization doctor
python -m tools.lean_formalization gate
python -m tools.lean_formalization build
python -m tools.lean_formalization scan --root "06_LEAN形式化"
python -m tools.lean_formalization check-correspondence
python -m tools.lean_formalization check-manifest --path "06_LEAN形式化/manifests/ALG-001.yaml"
```

审稿缺陷扫描与成果一致性（v1.7 / v1.8）：

```text
python -m tools.review "<path>"
```

检索（v2.0 Metadata → FTS → BM25 → Hybrid RRF；无向量库、无 PDF 原页锚点）：

```text
python -m tools.retrieval gate
python -m tools.retrieval ask --query "<q>" --principal PUBLIC
```

权限过滤在召回前执行；证据不足时拒答；回答一律 Candidate，不写正式 Source。向量 Sidecar 未安装。

受控多角色（v2.1；固定缺陷 fixture 上对照单角色；超时/取消回退单角色）：

```text
python -m tools.collaboration gate
python -m tools.collaboration run --root "<path>"
```

Agent 不得直接修改 Knowledge / 正式 PDF / Frozen Source。未通过真实收益 Gate 前保持 PILOT。

文献登记与竞赛/精读脚手架：`10_提示词/Modeling_and_Literature_Usage_Guide.md`。

```text
python -m tools.reference_library doctor
python -m tools.reference_library ingest-paper --slug "<slug>" --title "<title>" --domain "<domain>" --pdf "<optional.pdf>"
```
