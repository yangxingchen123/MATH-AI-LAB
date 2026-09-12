# Reasoning Graph

`MathematicalReasoningGraph` **不是** 知识图谱，也不是 Universe `MathGraph`。

## 节点

`premise` → `transformation` → `intermediate` → `conclusion`

## 边

`requires` `transforms` `strengthens` `weakens` `contradicts` `generalizes`

## 硬规则

- 边的端点必须已存在
- `generalizes` 不是 `proves`
- 图的存在 **不** 等于定理已证（`reasoningProvesTheorem` 恒为 false）

## 引理依赖投影

`projectLemmaReasoning` / `tools.research_lab.lemmas.reasoning_graph` 只消费 correspondence 里声明的 `depends_on`：

- 无依赖 → `premise`
- 有依赖且被其它引理依赖 → `intermediate`
- 有依赖且不被依赖 → `conclusion`
- 边：`requires`（dependent → dependency）

**同一 Lean 文件里的相邻顺序不是推理边。** 那只给 `lemma_graph` 做无环检查。

已写入 correspondence、且能在 Lean 源文件里核对到的 `depends_on`：

- `ALG-004`（`add_comm`）← `ALG-002`（`nat_add_zero`）、`ALG-003`（`zero_add`）
- `ANL-004`（`quadratic_at_neg`）← `ANL-001`（`fenchel_young_quadratic`）

`length_rev` 的归纳证明没有调用 `rev_nil` 定理，所以 **不** 给 `DISC-002` 写 `depends_on: [DISC-001]`。

只读条目：Qt「探索」里的「推理图」、`python -m tools.research_lab explore --id reasoning`、网页 `/explore/reasoning`。

理论如何被后继理论替换，见 `TheoryEvolutionGraph`（extends / simplifies / unifies / specializes），在 [discovery-pipeline.md](discovery-pipeline.md)。
