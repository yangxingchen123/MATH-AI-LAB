# Mathematical Exploration Engine v0.1

**状态：** 设计 / 过程层  
**不是：** Frozen Schema、不是新 YAML 对象、不是数据库、不是 LLM、不是计算引擎

---

## 核心问题

不要问「如何存储更多数学」。

要问：**如何表示新数学产生的过程。**

表示（entity / unknown region）不是探索。探索是：

```text
Observation → Pattern → Question → Conjecture → Experiment
  → Failure → Revision → Proof → Formal Verification → Theory Evolution
```

---

## 四层约束（禁止合并）

```text
Canonical Layer     已有数学（Frozen Source：K/P/A/M、Lean、Dossier）
        ↓ 只读投影
Universe Layer      数学实体（packages/domain-math）
        ↓ ID 引用
Frontier Layer      未知区域 / 研究方向（packages/domain-frontier）
        ↓ ID 引用
Exploration Layer   研究过程（packages/domain-exploration）
        ↓ 若要进入 canonical
Human Review → Evidence Evaluation → Formal Verification（可选）
        → Canonical Operation（本层不执行写入）
```

| 层 | 包 | 回答的问题 |
| --- | --- | --- |
| Canonical | 仓库事实源 | 我们知道哪些数学？ |
| Universe | `domain-math` | 对象、关系、证据如何投影？ |
| Frontier | `domain-frontier` | 未知区域与方向在哪？ |
| Exploration | `domain-exploration` | 我们正在探索什么、为何相信、哪些路失败了、下一步可能是什么？ |

Frontier 在 v2.0 之前并未独立成包。Universe 继续持有 Candidate 身份；Exploration 用 `ConjectureLifecycle` **包裹** Candidate，不把过程状态写进 Entity。

---

## 明确不做

- 不改 `元数据规范.md` / Frozen YAML
- 不把 Observation / Pattern / Notebook 写成 Knowledge
- 不实现 LLM、embedding、符号/数值计算引擎
- 不自动 Promotion；AI generated 不能变成 Theorem
- 不新增写入 UI。只读 `/explore` 与 Qt「探索」是过程简报，不是 Canonical 编辑器。

---

## 文档

| 文件 | 内容 |
| --- | --- |
| [observation-model.md](observation-model.md) | MathematicalObservation |
| [pattern-model.md](pattern-model.md) | MathematicalPattern |
| [conjecture-evolution.md](conjecture-evolution.md) | ConjectureLifecycle |
| [experiment-framework.md](experiment-framework.md) | ExperimentProtocol |
| [failure-memory.md](failure-memory.md) | Counterexample + FailureMemory |
| [proof-strategy.md](proof-strategy.md) | ProofStrategy |
| [reasoning-graph.md](reasoning-graph.md) | MathematicalReasoningGraph |
| [research-notebook.md](research-notebook.md) | Notebook + Session |
| [memory-architecture.md](memory-architecture.md) | 三层记忆 + 检索/类比接口 |
| [discovery-pipeline.md](discovery-pipeline.md) | Pipeline、Promotion、Actor、Assessment |
| [frontier-catalog.md](frontier-catalog.md) | teorth/erdosproblems 全体文件 pin + 开放问题指针 |

Lab → 过程状态对照：`packages/domain-exploration/src/lab-map.json`（Python / TypeScript 共用；无 Lab stage 映射到 Promotion）。

只读条目：`python -m tools.research_lab explore --id <id>`、`explore --list`、`search-explore --query`（字面命中，无 embedding）、Qt「探索」列表、网页 `/explore/[id]`。推理图见 [reasoning-graph.md](reasoning-graph.md)。模式见 [pattern-model.md](pattern-model.md)。证明策略见 [proof-strategy.md](proof-strategy.md)。笔记本见 [research-notebook.md](research-notebook.md)。前沿开放问题见 [frontier-catalog.md](frontier-catalog.md)。
