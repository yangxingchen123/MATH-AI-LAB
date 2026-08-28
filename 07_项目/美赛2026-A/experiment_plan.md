# 实验计划

- 代码工程: `05_代码/美赛2026-A/`
- MATLAB: `05_代码/美赛2026-A/matlab/`（可选）
- LaTeX: `04_LATEX/数学建模/美赛2026-A/美赛2026-A.tex`
- 对应问号: 见 `problem.md` Q1–Q6（连续时间 SOC、TTE、驱动因素、影响大小、敏感性、建议）
- 小规模已知答案实例: \(E=15\,\mathrm{Wh}\), \(P=3\,\mathrm{W}\) ⇒ TTE \(=5\,\mathrm{h}\)；\(t=2.5\) 时 SOC \(=0.5\)
- 基线: 能量守恒 ODE（DEC-0001）；`engine=soc`
- 敏感性参数: 分项功率、\(\eta(T)\)、\(\alpha\)、初始 SOC（ASM-0003 / ASM-0004）
- 正式 run 命令: `python -m tools.workbench run-experiment --name 美赛2026-A --engine soc --run-id soc-baseline-001`
- 敏感性命令: `python -m tools.workbench run-experiment --name 美赛2026-A --engine soc_sensitivity --run-id soc-sensitivity-001`
- 分段使用: `python -m tools.workbench run-experiment --name 美赛2026-A --engine soc_piecewise --run-id soc-piecewise-001`
- 选模命令: `python -m tools.modeling select --path "05_代码/美赛2026-A/configs/candidates.yaml"`

结果以 Evidence 进入 `evidence.md`，不要把 Notebook 截图当作唯一依据。数据必须可引用、开放许可。
