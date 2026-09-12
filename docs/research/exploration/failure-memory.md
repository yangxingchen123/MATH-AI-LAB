# Failure Memory 与反例

数学经常靠反例前进。失败是可复用对象，用来避免重复死路。

## CounterexampleRecord

`claim` `counterexample` `construction` `whyFailure` `lesson` `futureDirection`

例：

- Claim：All functions satisfying X are continuous.
- Counterexample：Function Y
- Lesson：Missing boundedness assumption.

反例记录 ≠ Universe 实体类型 `counterexample`。前者是过程教训，后者是对象占位。

## FailureMemorySystem

`failedAttempt` `reason` `assumptionFailure` `methodFailure` `lesson` `relatedFutureResearch`

查找是字面匹配（reason / method / assumption / id），**没有 embedding**。

失败记忆进入 [MathematicalMemory](memory-architecture.md) 的第三层，不删除 Attempt，也不改 Frozen Attempt Schema。

## Lab journal（sidecar，不是 Source）

- 路径：`tools/research_lab/sidecars/failures.jsonl`（gitignore；目录可空）
- 写入：`tools.research_lab.failures.append_failure`（拒绝结果保留，禁止当删除）
- 读取：`python -m tools.research_lab explore --failures <path>`
- 检索：`python -m tools.research_lab search-failure --query "<reason>"`

命中状态永远是 `candidate`。Journal 行会投影进五问「哪些失败了」，**不能**写成 Canonical / Theorem。
