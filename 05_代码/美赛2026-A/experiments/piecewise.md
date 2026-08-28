# 分段使用

```text
python -m tools.workbench run-experiment --name 美赛2026-A --engine soc_piecewise --run-id soc-piecewise-001
```

known-answer（\(E=15\,\mathrm{Wh}\)）：

- 先 \(6\,\mathrm{W}\times 1\,\mathrm{h}\) 再 \(0.3\,\mathrm{W}\) ⇒ TTE \(=31\,\mathrm{h}\)
- 先 \(0.3\,\mathrm{W}\times 1\,\mathrm{h}\) 再 \(6\,\mathrm{W}\) ⇒ TTE \(=3.45\,\mathrm{h}\)

同一组活动，顺序不同。功率仍是假定。
