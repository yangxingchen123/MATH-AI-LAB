# Observation 模型

`MathematicalObservation` 在 `packages/domain-exploration`。

它是 **前数学信号**，不是 Question、Conjecture、Proof，也不是 Universe `MathematicalEntity`。

## 字段

`id` `description` `origin` `relatedEntities` `evidence` `researchContext` `timestamp`

- `origin`：`numerical_pattern` / `theory_similarity` / `assumption_failure` / `human` / `lab` / `other`
- `relatedEntities`：Universe 实体 ID，只引用
- `researchContext`：Frontier 区域或方向 ID，或短注记
- `evidence`：证据 ID，不是「AI 说看见了」

## 例子

- Unexpected numerical pattern
- Similarity between two theories
- Failure of existing theorem assumption

## 禁止

- 把 Observation 投影成 Theorem / Knowledge
- 无显式生命周期步骤就把 Observation 当成 Conjecture
