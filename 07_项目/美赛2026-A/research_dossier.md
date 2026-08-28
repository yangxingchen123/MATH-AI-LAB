# 2026 MCM Problem A

## 项目类型

数学建模竞赛（美赛 / 国赛 / 其他）。本目录是研究 Dossier，**不是** `02_题目库` 习题。

## 赛题

完整题面：`03_参考资料/竞赛/美赛/2026-A/source.pdf`；转写：`derived/p0001-0003.md`。问号与重述见 `problem.md`。决策边界：必须有显式连续时间锂电 SOC 模型；数据只作参数估计与验证。

## 模型选取

导航 `model_selection.md`。选定、否决与可逆性写入 `decisions.md`，不要只在对话里决定。

## 实验

导航 `experiment_plan.md`。Python / MATLAB 工程放 `05_代码/<同名项目>/`。计算证据写入 `evidence.md`（`kind: COMPUTATION`）。

## 论文

导航 `paper_outline.md`。LaTeX 工程放 `04_LATEX/数学建模/<赛事>/<题>/`，正式 PDF 经授权后发布到 `08_成果输出/PDF/数学建模/`。

## 人工结论

基线采用能量守恒 ODE（DEC-0001）。known-answer：15 Wh / 3 W → 5 h。分项弹性等于负份额（DEC-0002）。分段使用下顺序会改 TTE：先重后轻 31 h，先轻后重 3.45 h（CLM-0004）。建议是机制翻译，不是实测。论文为工作草稿，未授权不发布。

<!-- MATH-AI-LAB:RESEARCH-DOSSIER GENERATED BEGIN -->
<!-- MATH-AI-LAB:RESEARCH-DOSSIER GENERATED END -->
