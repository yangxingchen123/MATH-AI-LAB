# 关系模型

保留既有 **Explicit / Derived**。新增 `MathematicalRelation`：数学语义，不是 `related_to` 标签。

## 字段

`type` `source` `target` `origin` `evidence`

`evidence` 至少有：`kind`（explicit_field / derived_reverse / lean_manifest / attempt_ledger / lab_record / none）、可选 `sourcePath`、短 `note`。

## 关系类型（v0.1 实际产生）

| type | 何时出现 |
| --- | --- |
| depends_on | Knowledge.prerequisites（explicit） |
| uses | Problem.knowledge、Method.knowledge（explicit） |
| derived_from | 上述反向（derived） |
| verified_by | 稳定 ID 与 Lean 条目可绑定，且仅当 Lean **Verified** |
| motivated_by | 类型存在；Attempt 不是 Entity，故 v0.1 **不画边**，改记 `ProofAttempt` 事件 |

## 类型存在、当前数据几乎不产生

`generalizes` `special_case_of` `equivalent_to` `contradicts` `proves` `disproves`

**禁止：** Attempt.outcome=correct ⇒ `proves` Theorem。

关系 **不得写回** canonical。
