# Candidate 生命周期

未来 AI 与 Lab 产出 **不能** 直接进入数学世界。

## 状态

`idea` → `exploring` → `supported` → `promoted`

随时可以 `rejected`。`promoted` 表示「可以提交给未来 Domain Operation」，**不是**已经写成 Theorem。

## 管道

```text
Candidate → Human Review → Validation → Domain Operation → Canonical Entity
```

v0.1：只实现状态机与拒绝自动升级。`promoteToCanonical()` 恒失败。

过程状态（`generated` / `tested` / `challenged` / `resolved` 等）在 Exploration 的 `ConjectureLifecycle`，不写进本层 Candidate。见 [exploration/conjecture-evolution.md](exploration/conjecture-evolution.md)。

## 当前源

- Research Lab records：固定 `candidate: true`
- Mock `AIResearchProvider`：origin=`ai_mock`，status=`idea`

## 禁止

- Candidate 自动变成 Theorem / Knowledge / Problem
- UI 把 Lab 猜想画成已证明
- 无 Human Review 的 Promoted
