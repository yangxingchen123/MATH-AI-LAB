# Pattern 模型

`MathematicalPattern` 表示 **重复出现的结构**。Pattern ≠ Theorem。

## 字段

`pattern` `instances` `supportingEvidence` `confidence` `relatedTheory`

`kind`：`symmetry` / `invariant` / `repeated_relationship` / `hidden_correspondence` / `other`

`confidence` 只有 `none` / `heuristic` / `human_claimed`。没有 `machine_checked`，避免把模式当成已证命题。

## 例子

- Symmetry
- Invariant
- Repeated relationship
- Hidden correspondence

## 禁止

- Pattern 自动升级为 Canonical 定理
- 用模式置信度冒充数学真值

## 投影

`projectRecurringPatterns` / `tools.research_lab.patterns.pattern_clusters` 只记录 **至少 2 个实例** 的重复结构：

- correspondence `family` 聚类（algebra / analysis / discrete）
- Universe `formal_proof` 的 ID 前缀聚类（`ALG-` / `ANL-` / `DISC-`）
- 同 origin 的 Observation（若 ≥2）

置信度固定为 `heuristic`。单例不记为 Pattern。

