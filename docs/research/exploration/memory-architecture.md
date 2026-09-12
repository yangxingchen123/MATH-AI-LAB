# Mathematical Memory 架构

未来 AI 需要三层记忆，缺一不可。

## Short-term

当前 `ResearchSession`（可选 notebook id）。

## Long-term

已核验数学。只存 Universe / Canonical **ID**，不复制实体正文，避免与 Universe 合并。

## Failure

`FailureMemorySystem` 中被拒绝的路径。

## 检索与类比（接口 only）

`MathematicalSearchProvider`：

- `searchConcept` `searchProof` `searchStrategy` `searchFailure` `searchAnalogy`

命中固定 `status: "candidate"`。无 embedding。

仓库现用字面检索：`python -m tools.research_lab search-explore --query "<text>"` 扫探索目录；`search-failure` 只扫失败 journal。都不是语义检索。

`MathematicalSimilarityEngine`：

- `findAnalogies` `findGeneralizations` `findRelatedStructures` `findPotentialConnections`

输出只能是 Universe `Candidate`（通常 `idea`）。默认 `NullSimilarityEngine` / `NullSearchProvider` 返回空列表。
