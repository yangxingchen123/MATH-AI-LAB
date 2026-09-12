# Proof Strategy

不要只存证明文本。要表示 **证明搜索方式**，供未来推理使用。

`ProofStrategy`：

- `strategy`（如 induction / contradiction / compactness / category argument / algebraic construction）
- `applicableConditions`
- `successfulCases`
- `failedCases`
- `limitations`

这不是 Proof 对象，也不是 Lean 证明。成功案例只是 ID 列表，不蕴含 Canonical 定理。`strategyIsProof` 恒为 false。

当前仓库只做 **词法扫描**：公开 `theorem` 正文里出现 `induction` 或 `odds` 才记一条策略。`private theorem` 不投影。没有命中 compactness / contradiction / category_argument，就不编造。`intro h` 不是 contradiction。

只读条目：`python -m tools.research_lab explore --id strategy:induction`。检索：`search-explore --query induction`。
