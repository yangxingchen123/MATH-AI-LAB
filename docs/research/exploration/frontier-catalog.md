# Frontier 开放问题目录

Frontier 回答：**未知区域在哪？** 不是「我们证明了什么」。

## 上游：全体文件 pin，不是接口

钉住 [teorth/erdosproblems](https://github.com/teorth/erdosproblems)（Apache-2.0）。

`vendor/erdosproblems/` 是该仓库在 pin `5308c57c700559416b9f205df274b136784203e7`（2026-09-07）上的**全体 tracked 文件**，与 `vendor/math-modeling-skills/` 一样是只读 pin。清单与政策见 `vendor/erdosproblems/UPSTREAM.md`。

运行时**只读本地文件**：

- 事实源：`vendor/erdosproblems/data/problems.yaml`
- 许可证：`vendor/erdosproblems/LICENSE`
- 字段说明：`vendor/erdosproblems/CONTRIBUTING.md`、`schema/problems.schema.json`

没有 GitHub API、没有 HTTP 客户端、不跟随 `main`、不爬 https://www.erdosproblems.com。上游 `scripts/`、`docs/`、`.github/` 一并钉住，便于核对他们如何从 YAML 生成 README；本仓库 **`operate` / `gate` 不执行这些脚本**，也不把上游 `requirements.txt` 并进根依赖。

**不**把 `google-deepmind/formal-conjectures` 的 Lean 引进本仓库 lake（Mathlib 保持 UNPLUGGED）。

本仓库覆盖层（不是上游原文）：`vendor/erdosproblems/UPSTREAM.md`、`NOTICE`。

## 投影（内存过滤，不是再下一份上游子集）

YAML 本身没有题面 `statement` 字段。本仓库**不复制** erdosproblems.com 的题面正文。

内存里：

1. 保留 tags 含 `additive combinatorics` 的记录；
2. 只把 `status.state` 为 `open` 或 `open …` 的记录投影为 `OpenQuestion`（`erdos:<n>`，组「前沿」）；
3. 其余加法组合论记录进入 **前沿备查**（同一 `erdos:<n>`，组「前沿备查」）：可检索，**不是** OpenQuestion，**不是**定理。

`proved` / `disproved` / `solved` / `decidable` 等状态留在完整 `problems.yaml`，也可经 `frontier-audit` / `search-explore` 本地查看。YAML 里的 `comments` 只当短 nickname（如 sum-product problem），不当题面。

TypeScript 侧的 `packages/domain-frontier/src/erdos-additive.json` 是同一投影的**本地派生镜像**（给网页 / vitest 用），不是远程接口。`operate` / `gate` 会核对：整树 30 个上游文件在、`UPSTREAM.md` 的 pin 一致、JSON 与 YAML 投影一致。Bump pin 后用 `dump_erdos_index_json()` 重建。

## 语义

| 对象 | 含义 |
| --- | --- |
| `region:additive-combinatorics` | UnknownRegion |
| `dir:erdos-additive` | ResearchDirection |
| `erdos:<n>` | OpenQuestion 指针，`not_a_theorem` |

禁止：写成 Knowledge、建成 `P00xx`、自动 Promotion、把 `formalized: yes` 当成本库 Lean 核验。

只读：`python -m tools.research_lab explore --id frontier`、`explore --id erdos:3`、`search-explore --query erdos`、Qt「探索」、网页 `/explore`。
