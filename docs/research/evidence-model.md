# 证据模型

数学世界里，证据比对象更重要。

`EvidenceRecord`：

- `claim` — 指向 Entity 或稳定 ID，不是「AI 说对了」
- `evidenceType` — HumanProof / LeanProof / Computation / Experiment / Literature / Counterexample / ExpertReview
- `source` — 文件或 ledger 路径
- `status` — unverified / supporting / contradicting / rejected / candidate
- `confidence` — `none` / `heuristic` / `human_claimed` / `machine_checked`

## 硬规则

**AI confidence ≠ mathematical truth。** 没有 `ai_true`。Mock AI 不产生 EvidenceRecord，只产生 Candidate。

## 当前投影

| 源 | evidenceType | confidence | 含义 |
| --- | --- | --- | --- |
| Attempt ledger | HumanProof | human_claimed | 人作答过；correct 仍不是核验定理 |
| Lean manifest SUCCEEDED | LeanProof | machine_checked | 唯一可标 formal_verified 的证据 |
| Lean 仅有源文件 | LeanProof | none | Source Exists ≠ Verified |
| Lab YAML | Experiment 或 Computation | none | status=candidate |
| 参考资料 | Literature | none | 文献存在，不是命题为真 |

Attempt 永远不是 Theorem 的充分证据。
