# Discovery Pipeline 与 Promotion

## DiscoveryPipeline

```text
Observation → Exploration → Candidate → Experiment → Critique
  → Proof Attempt → Verification → Promotion
```

不允许跳级。实验/批评可以退回 exploration（修订）。进入 `promotion` 必须：

- Human review
- Evidence evaluation
- Formal verification：`done` 或显式 `skipped`（`pending` 阻止）
- 非 AI actor

Lab 阶段投影见 `packages/domain-exploration/src/lab-map.json`。**没有任何 Lab stage 映射到 `promotion`。** `PAPER_READY` 只到 `verification`。

Verification 在 Promotion 规则里 **可选**（`done` 或显式 `skipped`；`pending` 则阻止）。AI 不能标记 skip；FormalSystem / Human 可标记 `done`。

## Promotion（禁止自动升级）

```text
Candidate
  → Human Review
  → Evidence Evaluation
  → Formal Verification（可选）
  → Canonical Operation
```

Exploration 层：

- `requestPromotion` 最多给出 **handoff 授权**（`wroteCanonical: false`）
- `executeCanonicalWrite` **恒失败**（并调用 Universe `promoteToCanonical`，同样失败）

没有 Domain Operation，本层不能写仓库。

## ResearchActor

`Human` / `AI` / `FormalSystem`

例：AI generated conjecture；Human modified assumption；Lean verified proof。

与 Universe `ResearchEvent.actor`（`human` / `system` / `lab` / `ai_mock`）分开，避免把过程层事件写进实体时间线。

## ResearchAssessment

人类记录：`novelty` `difficulty` `evidence` `connections` `formalStatus`

AI 不得录入评估。

## 未来多智能体（接口 only）

`ExplorerAgent` `ProofAgent` `CriticAgent` `ExperimentAgent` `FormalizationAgent`

无实现。若将来接入，返回值必须是 Candidate，不得声明定理。

## TheoryEvolutionGraph

`extends` `simplifies` `unifies` `specializes`

表示旧理论到新理论的演化，不是推理图，也不是 Frozen 关系字段。`evolutionProvesTheorem` 恒为 false。

当前仓库只投影 **孤立模块节点**（`correspondence.yaml` 的 `lean_file`）。**不编造** extends/simplifies/unifies/specializes 边。只读条目：`explore --id evolution`。
