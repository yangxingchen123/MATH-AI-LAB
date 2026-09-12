# Experiment 框架

`ExperimentProtocol` 是 **抽象**，不是计算引擎。

为将来预留：symbolic / numerical / counterexample search / automated exploration。

## 字段

`hypothesis` `variables` `method` `expectedOutcome` `actualOutcome` `interpretation` `evidence`

`method`：`symbolic` / `numerical` / `counterexample_search` / `automated_exploration` / `other`

## 语义

- 记录「打算试什么、期望什么、实际看见什么、如何解释」
- `actualOutcome` 不是证明
- 数值/符号结果不能代替人可读证明或 Lean 核验

## 禁止

- 在本层实现求解器、搜索器或 LLM
- 把实验成功写成 Theorem
