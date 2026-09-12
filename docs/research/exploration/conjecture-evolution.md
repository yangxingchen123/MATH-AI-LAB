# Conjecture 演化

Universe 的 `Candidate`（`packages/domain-math`）仍然只表示 **候选身份**。

Exploration 增加 `ConjectureLifecycle`：**过程状态机**，按 `candidateId` 包裹 Candidate，不合并两层。

## 状态

`idea` → `generated` → `exploring` → `tested` → `supported` → `challenged` → `modified` → `resolved` → `rejected`

- `generated`：AI / mock 产出。不是真。
- `resolved`：研究问题在过程上被结算（证明、否证、或撤回问题）。**不是** Theorem，**不是** Canonical 写入。
- Universe `promoted` 映射为 lifecycle `supported`（「可以提交 Operation」），绝不映射为定理。

Lab 阶段 → lifecycle / discovery pipeline 的对照表是 `packages/domain-exploration/src/lab-map.json`（Python `tools.research_lab.lab_map` 与 TS 共用）。例如 `FALSIFICATION` → lifecycle `challenged`、pipeline `experiment`；`CANDIDATE_SURVIVED` → `tested` / `critique`。该表 `never_maps_to_promotion: true`。

## 转移规则

每一次转移必须有：

- `event`
- `actor`（Human / AI / FormalSystem）
- `evidence`

禁止：

```text
AI generated  →  Theorem
AI actor      →  supported | resolved
generated     →  resolved   （跳过探索）
```

`supported` / `resolved` 只能由 Human 声明。

## 与 Candidate 管道的关系

```text
Candidate ──fromCandidate()──► ConjectureLifecycle
                                      │
                                      ▼
Human Review → Evidence Evaluation → Canonical Operation（Exploration 不执行）
```

详见 [discovery-pipeline.md](discovery-pipeline.md) 与 [candidate-lifecycle.md](../candidate-lifecycle.md)。
