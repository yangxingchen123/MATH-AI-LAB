# 基线实验

命令：

```text
python -m tools.modeling select --path "05_代码/美赛2026-A/configs/candidates.yaml"
python -m tools.workbench run-experiment --name 美赛2026-A --engine soc --run-id soc-baseline-001
```

known-answer：\(E_{\mathrm{eff}}=15\,\mathrm{Wh}\)，\(P=3\,\mathrm{W}\)，\(\mathrm{SOC}_0=1\) ⇒ \(t_{\mathrm{empty}}=5\,\mathrm{h}\)。
Euler 在 \(t=2.5\,\mathrm{h}\) 应得到 \(\mathrm{SOC}=0.5\)。

参数是 ASM-0006 量级假设，不是开放数据集估计。
