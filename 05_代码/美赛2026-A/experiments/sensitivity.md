# 敏感性实验

```text
python -m tools.workbench run-experiment --name 美赛2026-A --engine soc_sensitivity --run-id soc-sensitivity-001
```

known-answer：对 \(P=\sum P_i\)，\(\partial \log t_{\mathrm{empty}}/\partial \log P_i=-P_i/P\)。baseline 中屏幕 \(1.5/3=-0.5\)。\(\eta=0.75\) 时 TTE \(=3.75\,\mathrm{h}\)。

参数仍是 ASM-0006 量级假设。
