---
name: math-modeling-lab
description: MATH-AI-LAB contest modeling agent. Routes CUMCM / MCM / ICM / 国赛 / 美赛 / 数模赛题 from problem text to Dossier, experiments, and paper scaffold. Use when the user pastes a contest problem, asks 怎么建模, 选什么模型, 写数模论文, 美赛, 国赛, CUMCM, MCM/ICM, or wants the math-modeling-solver / math-modeling-paper workflow inside this repo.
---

# 竞赛建模 Agent（MATH-AI-LAB）

先读本文件，再读已经拷进本仓库的 solver / paper skill。本仓库的目录职责优先于上游「每阶段停下来问一次」。

工作副本（直接用）：

- solver：`.cursor/skills/math-modeling-solver/SKILL.md` 与同目录 `references/`
- paper：`.cursor/skills/math-modeling-paper/SKILL.md` 与同目录 `references/`
- 代码模板：`05_代码/_模板/数模竞赛_v1/`

MIT pin（只读，不要改）：`vendor/math-modeling-skills/`

## 何时用

用户给了赛题文本、要拆题/选模/写代码/写数模论文、提到美赛/国赛/CUMCM/MCM/ICM/电工杯时使用。

课后习题、定理证明、开放纯数学研究 **不要**走本 skill。

## 落点（硬约束）

| 产物 | 位置 |
|------|------|
| 题面与问号 | `07_项目/<name>/problem.md` |
| 假设 / 选模 / 否决 | `assumptions.md` · `model_selection.md` · `decisions.md` |
| 实验计划与证据 | `experiment_plan.md` · `evidence.md`（计算层） |
| 论文提纲 | `paper_outline.md` |
| 代码 | `05_代码/<name>/src/`（MATLAB → `matlab/`） |
| 代码模板来源 | `.cursor/skills/math-modeling-solver/references/code-templates/` 或 `05_代码/_模板/数模竞赛_v1/` |
| 论文 TeX | `04_LATEX/数学建模/<name>/<name>.tex` |
| 赛题原文 | `03_参考资料/竞赛/`（有 PDF/MD 时） |

禁止：

- 把竞赛整卷建成 `02_题目库/` 的 `Pxxxx`
- 自动创建 Knowledge / Method
- 未授权发布 PDF 到 `08_成果输出/`
- 把数值 run 写成「已证明现实」
- 把 matplotlib / scipy / 求解器写入仓库根 `requirements.txt`
- 修改 `vendor/math-modeling-skills/` 原文

## 启动

已有同名 Dossier 则继续写，不要重建。

没有脚手架且用户已给出赛题名时：

```text
python -m tools.workbench bootstrap --kind contest_modeling --name "<name>" --title "<标题>"
```

没有赛题名时先问一句（赛事 + 年份 + 题号，如 `2026-MCM-A`），不要用 `P00xx` 当 name。

有题面 MD 时：

```text
python -m tools.workbench attach-md --contest "<赛事>" --slug "<题号>" --md "<path.md>"
```

选模押注写入 `05_代码/<name>/configs/candidates.yaml` 后：

```text
python -m tools.modeling select --path "05_代码/<name>/configs/candidates.yaml"
```

每个候选必须有：针对的问号、为什么想到、数据、可识别条件、可证伪条件、一行否决。缺一项则不可用。

能用仓库 stdlib 引擎的，优先：

```text
python -m tools.workbench run-experiment --name "<name>" --engine <engine> --run-id "<id>"
python -m tools.workbench coverage --name "<name>"
```

vendor 模板若需要 numpy，先检查 sidecar：

```text
python -m tools.modeling contest-doctor
python -m pip install -r tools/modeling/requirements-contest.txt
```

不得把这些包写入仓库根 `requirements.txt`。`coverage` / `contest-pipeline` 只写 Evidence **候选**，不改正式 `evidence.md`，不宣称论文完成。

## 与上游 skill 的差异

上游 solver 默认「每阶段停下来等确认」。在本仓库：

- **AUTO（默认）**：用户说「怎么做 / 解答 / 直接做」时，一轮内做完拆题、文献上限检索、选模押注、代码落盘、论文草稿片段；写入 Dossier，不要只停在对话。
- **STUDY**：仅当用户说「我想自己做 / 先别给答案 / 一步一步」时，才按上游分阶段停顿。
- 文献检索仍遵守上游硬上限：最多 5 次 WebSearch，找到 5–8 篇即停。
- 不得编造论文、DOI、期刊分区；无依据标 `待查证`。
- 矩阵/Cookbook/Playbook 是候选，不是唯一答案；落选路线写 `negative_results.md`。
- 代码从模板改写到本题符号，写入 `05_代码/<name>/`，不要把可运行脚本只贴在聊天里当终点。
- 论文正文写入 `04_LATEX/数学建模/<name>/` 与 `paper_outline.md`；图表优先仓库 figure/stdlib，Matplotlib 只作为该竞赛工程的局部依赖。

## 证据层

启发式直觉 ≠ 数值/图像 ≠ 人可读论证 ≠ Lean。竞赛论文里的「结果」默认是计算/数据层。

## 下一步加载

1. 解题：读取并执行 `.cursor/skills/math-modeling-solver/SKILL.md`
2. 写作：读取并执行 `.cursor/skills/math-modeling-paper/SKILL.md`
3. 操作顺序：`10_提示词/Math_Modeling_Agent_Usage_Guide.md`
