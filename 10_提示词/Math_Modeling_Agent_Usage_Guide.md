# 竞赛建模 Agent 用法

本仓库接入的是 [Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills)（MIT）。文件已经下载并拷进本仓库：

- 工作副本：`.cursor/skills/math-modeling-solver/`、`.cursor/skills/math-modeling-paper/`、`05_代码/_模板/数模竞赛_v1/`
- 只读 pin：`vendor/math-modeling-skills/`
- 目录地图：`10_提示词/数模竞赛/README.md`

这不是 Frozen Schema，不是 Knowledge，也不是「已经能冲奖」的认证。权威目录职责仍是 `项目规则.md` 第九节。

## 你怎么用

在 Cursor 对话里直接说，例如：

- 「用数模智能体做这道题」+ 粘贴题面
- 「2026 美赛 A 怎么建模」
- 「帮我写国赛论文摘要」

Agent 应自动加载 `math-modeling-lab`，再走 solver（拆题/选模/代码）或 paper（写作）。

默认 **AUTO**：一轮给出拆题、选模押注、代码落盘和论文草稿片段，并写入 Dossier。只有你说「我想自己做 / 先别给答案 / 一步一步」时才分阶段停。

## 文件落在哪

同名三件套：

- `07_项目/<name>/` — Dossier（问号、假设、选模、证据）
- `05_代码/<name>/` — 可复现实验（模板在 `src/` / `matlab/`）
- `04_LATEX/数学建模/<name>/` — 论文骨架

没有脚手架时 Agent 应运行：

```text
python -m tools.workbench bootstrap --kind contest_modeling --name "<name>" --title "<标题>"
```

竞赛整卷 **不要**建成 `02_题目库/` 的 `Pxxxx`。

## 与仓库建模框架的关系

| 能力 | 用谁 |
|------|------|
| 拆题、95+ 场景矩阵、Cookbook、代码模板、论文结构 | `.cursor/skills/math-modeling-solver` 与 `math-modeling-paper` |
| 选模清单是否可检验 | `python -m tools.modeling select` |
| stdlib 已知答案实验（含 SOC） | `python -m tools.workbench run-experiment` |
| 问号覆盖审计 | `python -m tools.workbench coverage` |
| 正式 PDF | 你明确授权后再 `python -m tools.latex_build build` |

Cookbook 里的 matplotlib / scipy 只允许出现在竞赛 sidecar，不得进入仓库根环境。

## 竞赛数值 sidecar

根 `requirements.txt` 只有 PyYAML / pytest。要跑 AHP / GA / ODE 等模板：

```text
python -m pip install -r tools/modeling/requirements-contest.txt
python -m tools.modeling contest-smoke
```

或双击 `安装数模竞赛环境.bat`。sklearn / 时间序列 / seaborn 是可选项：

```text
python -m pip install -r tools/modeling/requirements-contest-ml.txt
```

`contest-doctor` 缺 numpy 时是 DEGRADED，不是 Core FAIL。xgboost 默认不装。

## 更新上游

不要手改 `vendor/math-modeling-skills/`。换 pin 时改 `UPSTREAM.md` 中的 commit，并核对 MIT LICENSE 仍在。
