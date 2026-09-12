# 研究实验室用法（v2.2-lab Pilot）

本指南对应 `tools.research_lab`。它是 Candidate Contract，**不是** Frozen Schema，**不是** v2.2 总架构关闭，**不是**数学四大准备度。

设计权威：`docs/superpowers/specs/2026-08-28-research-lab-maturity-design.md`。
思路权威：`项目规则.md` 第四节；机检副本：`tools/research_lab/protocol.yaml`。

实验室分两层，不要混：

| 层 | 命令 | 做什么 |
| --- | --- | --- |
| 运行条件 | `operate` | 根目录、协议、lockfile、Frozen Schema、Lean sidecar、探索层健康、禁令。**不**跑 P001 / sum-free |
| 探索简报 | `explore` / `search-failure` / `search-explore` | 五问只读。`explore --id` 打开一条；`explore --list` 列目录。失败 journal 与目录字面检索。前沿开放问题来自本地 pin 的 `vendor/erdosproblems/` 全体文件（不是接口、不是定理）。**不**写 Canonical |
| 思路 | `protocol` / `route` / `check-session` | 种类分流、重构先于检索、角色隔离、卡住必须写障碍、工具优先、infra 禁止新 P |
| 研究循环 | `cycle` / `advance` / `list-problems` / `reproduce` / `funnel` | 状态机、猜想/先验、C0 廉价候选、失败聚类、证据链指纹 |
| 投稿门禁 | `journal` / `prior-art-matrix` | G0–G6 脚手架。过关也不宣称四大 |
| 原始清单 | `backlog` / `pipeline` / `adapters` / `recipe` | 90 天 40 项全部有决议：done / sidecar / unplugged / policy |
| 实验室内核 | `check-task` / `lemma-graph` / `repair` / `risks` / `cost-report` | 任务对象、无环引理图、禁止改陈述的修复、风险登记 |
| 实例校准 | `verify` / `evaluate-sum-free` | 已知界演示。可选，不是「优化系统」的交付 |

---

## 命令

```text
python -m tools.research_lab operate
python -m tools.research_lab explore
python -m tools.research_lab explore --format markdown
python -m tools.research_lab explore --id reasoning --format markdown
python -m tools.research_lab explore --id frontier --format markdown
python -m tools.research_lab explore --list --format markdown
python -m tools.research_lab search-failure --query "not_sum_free"
python -m tools.research_lab search-explore --query "induction"
python -m tools.research_lab protocol
python -m tools.research_lab route --kind infra
python -m tools.research_lab cycle --n 10
python -m tools.research_lab funnel --n 5 --limit 8
python -m tools.research_lab reproduce --file <chain.jsonl>
python -m tools.research_lab journal
python -m tools.research_lab prior-art-matrix
python -m tools.research_lab backlog
python -m tools.research_lab check-task
python -m tools.research_lab lemma-graph
python -m tools.research_lab repair --reason out_of_universe
python -m tools.research_lab risks
python -m tools.research_lab cost-report
python -m tools.research_lab pipeline --n 5
python -m tools.research_lab review-statements
python -m tools.research_lab retrieve --query "sum-free list"
python -m tools.research_lab recipe
python -m tools.research_lab adapters
python -m tools.research_lab list-problems
python -m tools.research_lab list-conjectures
python -m tools.research_lab advance --file tools/research_lab/problems/PROB-SF-001.yaml --to CANDIDATE_SURVIVED
python -m tools.research_lab doctor
python -m tools.research_lab gate
python -m tools.research_lab inventory
python -m tools.research_lab evaluate-sum-free --n 10 --set 6,7,8,9,10
python -m tools.research_lab search-sum-free --n 10
python -m tools.research_lab check-problem
python -m tools.research_lab verify
```

- `cycle` 只调度已登记 evaluator，默认 0 USD，不写正式 Source / `项目进度.md`。`--chain` 可把密封 run 追加到 JSONL（拒绝覆盖进度页）。`advance` 只打印下一状态，默认不落盘。
- `reproduce` 用密封记录重跑：陈述哈希或结果指纹对不上即失败。
- `journal` 检查 G0–G6；当前校准题 `PROB-SF-001` 必须 `paper_ready: false`。`funnel` 只跑 C0 确定性候选，失败原因聚类，0 USD 不报 cost-adjusted success。
- `inventory --write` 可写 JSON；`--sidecar` 可写派生进度旁路，但拒绝覆盖 `项目进度.md` / Frozen Schema。
- `backlog` 对照最初 90 天 40 项：能做的已做；模型/Mathlib/SAT/调度器以 UNPLUGGED 插座关闭，不假装已接入。
- 用户说「优化系统 / 运行条件 / 继续实验室」且没有新题面：种类 = `infra`。禁止新 P00xx、新 Lean 定理、再跑一遍 P001 演示。
- `evaluate-sum-free` / `search-sum-free` / `verify` 是实例校准：复现 `{1..n}` 上 sum-free 已知界 `ceil(n/2)`，不是新定理。
- 失败 journal：`tools.research_lab.failures.append_failure`；拒绝结果保留。默认 sidecar `tools/research_lab/sidecars/failures.jsonl`（不进 git）。`explore --failures` 读入五问；`search-failure --query` 只做字面匹配，无 embedding。`search-explore --query` 对探索目录做字面匹配，命中固定 `status: candidate`。
- 前沿开放问题：`vendor/erdosproblems/` 是 `teorth/erdosproblems` Apache-2.0 的**全体文件 pin**（不是 API）。运行时只读本地 `data/problems.yaml`。`explore --id frontier` / `erdos:3`；已结算条目 `explore --id frontier-audit` / `erdos:1`（前沿备查，不是定理）。不复制题面，不建成 `P00xx`。说明：`docs/research/exploration/frontier-catalog.md`。
- 成本台账：`tools.research_lab.ledger.append_entry`；超硬上限抛 `BudgetExceeded`；相同 `input_hash` 不计第二次费用。

---

## 落点

| 产物 | 目录 |
| --- | --- |
| 开放研究 / Dossier | `07_项目/` |
| Lean | `06_LEAN形式化/`（P001-L0：`QuadraticConjugate.lean`；PROB-SF-001：`SumFree.lean`；均为校准，不是实验室本体） |
| 计算实验 | `05_代码/` + v1.4 |
| 运行条件与思路 | `tools/research_lab/` |

禁止另建平行的 `research/`、`formal/`、`experiments/` 根目录。

---

## Lean 双层政策

普通学习问答：Lean 可选。可形式化的发表关键引理、有限证书、代数恒等式、高风险边界：默认走 Lean。深层分析证明先写人类证明。P001 的 Lean 证明是训练项目，不是数学创新。
