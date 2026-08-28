# 建模、竞赛论文与文献整理

权威目录职责：`项目规则.md` §九。种类分流：`项目规则.md` 第四节 §0。本文件只写操作顺序。

竞赛 / 应用建模 **不是** 课后证明题：不要套用第四节「严格推导（本题）」当主产出，不要把整卷登记进 `02_题目库/`。共用脊柱仍有效：先重构问号，再检索，再选模押注（可识别 / 可证伪 / 否决），数值 run 只是证据层中的一层。

## 两类建模

**计算建模（v1.4）**：模型已定义，要可复现地跑。

```text
python -m tools.modeling doctor
python -m tools.modeling run --engine ols --output-root "<dir>" --run-id "<id>"
python -m tools.modeling select --path "<candidates.yaml>"
```

`select` 要求每个候选写清：针对的问号、为什么想到、数据、可识别条件、可证伪条件。缺一项则不可用。

工程在 `05_代码/<项目>/`。

**竞赛 / 应用数学建模**：从题面到论文。

```text
python -m tools.workbench bootstrap --kind contest_modeling --name "<赛题名>" --title "<标题>"
python -m tools.workbench attach-md --contest "<赛事>" --slug "<题号>" --md "<PDFTomd.md>"
python -m tools.modeling select --path "05_代码/<赛题名>/configs/candidates.yaml"
python -m tools.workbench run-experiment --name "<赛题名>" --engine soc --run-id "<id>"
python -m tools.workbench run-experiment --name "<赛题名>" --engine soc_sensitivity --run-id "<id>"
python -m tools.workbench run-experiment --name "<赛题名>" --engine soc_piecewise --run-id "<id>"
python -m tools.workbench find-data --name "<赛题名>"
python -m tools.workbench contest-pipeline --name "<赛题名>"
python -m tools.workbench coverage --name "<赛题名>"
python -m tools.open_data search --query "smartphone power dataset" --project "07_项目/<赛题名>"
```

一次创建 `07_项目/` Dossier、`05_代码/` 实验工程和 `04_LATEX/数学建模/` 论文骨架。`contest-pipeline` 串联选模、开放数据检索、stdlib 实验、问号覆盖审计，并在 `documents/candidates/` 写出 Evidence **候选**（不改正式 `evidence.md`）。`coverage` 可单独复跑审计。二者**不会**宣称论文完成，不会发布 PDF，不会写入 Knowledge。`find-data` 只写开放数据候选，不估参。

然后：题面 → 假设 → `model_selection.md` → `05_代码/<同名>/` 实验 → `04_LATEX/数学建模/` 排版。未授权不发布 PDF，不写入 Knowledge。

## 论文收录与精读

```text
python -m tools.reference_library ingest-paper --slug "<slug>" --title "<标题>" --domain "<领域>" --pdf "<可选路径>"
python -m tools.research_project init --project "07_项目/<slug>-精读" --title "<标题>" --kind literature
```

`ingest-paper` 只写 `03_参考资料/论文/<领域>/<slug>/identity.md` 和 SHA-256。没有 MinerU 时 **不** 自动 PDF→MD（`parse_status: DEGRADED`）。读懂文章写在精读项目的 `reading_notes.md`；引用必须标明 QUOTE / PARAPHRASE / INFERENCE。审核前不进 `01_知识库/`。

## 题目收录

- 习题 / 定理题 → `02_题目库/`（Frozen Problem；用题目模板）
- 竞赛整卷 → `03_参考资料/竞赛/` + `07_项目/`（`--kind contest_modeling`）；**不要**建成一道 `Pxxxx`
- 文献原文 → `03_参考资料/论文/`；读懂 → `--kind literature`
- 赛题登记：`python -m tools.reference_library ingest-contest --contest 美赛 --slug 2026-A --title "..." --pdf "<可选.pdf>"`
- 能力总览：`python -m tools.workbench status`
- 未分类 → `00_收件箱/`
- 种类拿不准 → 先当临时提问回答，不创建错误落点
