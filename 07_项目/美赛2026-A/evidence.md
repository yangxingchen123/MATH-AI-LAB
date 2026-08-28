# Evidence

本文件是 Claim–Evidence 的权威记录。

<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0001 BEGIN -->
- status: SUPPORTED
- evidence_refs: EVD-0001
- core: true
---
在能量守恒方程 \(E_{\mathrm{eff}}\dot{\mathrm{SOC}}=-P\) 且 \(P\) 为正常数时，\(\mathrm{SOC}(t)=\mathrm{SOC}_0-Pt/E_{\mathrm{eff}}\)，放空时间 \(t_{\mathrm{empty}}=E_{\mathrm{eff}}\mathrm{SOC}_0/P\)。对 known-answer \(E_{\mathrm{eff}}=15\,\mathrm{Wh}\)、\(P=3\,\mathrm{W}\)、\(\mathrm{SOC}_0=1\)，有 \(t_{\mathrm{empty}}=5\,\mathrm{h}\)，且 Euler 在 \(t=2.5\,\mathrm{h}\) 得到 \(\mathrm{SOC}=0.5\)。这是模型内的数学事实，不是真实手机测量。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0001 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0001 BEGIN -->
- claim_ref: CLM-0001
- polarity: SUPPORT
- kind: COMPUTATION
- source_citation: run:05_代码/美赛2026-A/outputs/soc-baseline-001
---
`metrics.json` sha256 `7628c228a8bae14d62d90659988f36ba71533fac5193d00f2a55d85bd7bcb175`。`python -m tools.workbench run-experiment --name 美赛2026-A --engine soc --run-id soc-baseline-001` 输出 `tte_hours=5.0`，`soc_exact=0.5`，`soc_euler≈0.5`，`tte_idle_hours=50.0`。同一套 ASSUMED 功率下的情景比较（非本次 manifest 内）：screen_heavy ≈ 4.29 h，nav_gps ≈ 4.05 h，\(\eta=0.75\) 的 baseline ≈ 3.75 h。待机相对「3 W 合成负载」差一个数量级；低温容量缩放把 TTE 按比例缩短。参数尚未被开放数据集校准（ASM-0006）。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0001 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0002 BEGIN -->
- status: SUPPORTED
- evidence_refs: EVD-0002, EVD-0003
- core: true
---
在可加工率与 \(t_{\mathrm{empty}}=E_{\mathrm{eff}}\mathrm{SOC}_0/\sum P_i\) 下，分项相对弹性等于 \(-P_i/P\)。假定基线 \((0.3,1.5,0.8,0.2,0.1,0.1)\,\mathrm{W}\) 上，屏幕份额 \(0.5\) 最大，GPS 与后台各约 \(0.033\)。容量缩放改变 TTE 绝对值，不改变份额排序。这是模型内排序，不是实测耗电排名。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0002 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0002 BEGIN -->
- claim_ref: CLM-0002
- polarity: SUPPORT
- kind: COMPUTATION
- source_citation: run:05_代码/美赛2026-A/outputs/soc-sensitivity-001
---
`metrics.json` sha256 `6d0df77b5ac21981a0c13045ae2e8427064938db1de12a56debd2543c6f9936b`。`elas_screen=-0.5`，`elas_cpu≈-0.267`，`elas_idle=-0.1`，`elas_net≈-0.067`，`elas_gps=elas_bg≈-0.033`，`elas_total_power≈-1`，`elas_energy≈1`。屏幕 \(+20\%\) 后 TTE \(\approx 4.545\,\mathrm{h}\)；\(\eta=0.75\) 得 \(3.75\,\mathrm{h}\)；\(\alpha=0.85\) 得 \(4.25\,\mathrm{h}\)。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0002 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0003 BEGIN -->
- claim_ref: CLM-0002
- polarity: LIMIT
- kind: INFERENCE
- source_citation: project-note:ASM-0006
---
功率向量未经开放许可数据校准。若真实屏幕功率不是最大项，或功率不可加，则「先降亮度」这条排序会错。弹性公式本身不依赖具体瓦数，但名次依赖份额。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0003 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0003 BEGIN -->
- status: OPEN
- evidence_refs: EVD-0004
- core: false
---
把 CLM-0002 译成建议：用户与操作系统应优先削减当前最大功率份额（本假定基线是屏幕）；关闭份额很小的后台，TTE 变化很小；低温与老化应通过 \(E_{\mathrm{eff}}\) 缩放修正剩余时间，而不是改份额排序；同一方程可推广到其他便携电池，只要负载可加。建议继承 ASM-0006，不是现场试验结论。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0003 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0004 BEGIN -->
- claim_ref: CLM-0003
- polarity: SUPPORT
- kind: INFERENCE
- source_citation: run:05_代码/美赛2026-A/outputs/soc-sensitivity-001
---
DEC-0002：干预按 \(|\text{elasticity}|=P_i/P\) 排序。EVD-0002 给出本假定基线上的份额。OS 策略对应「估计分项功率 → 算份额 → 先限最大项；冷/老化时只改 \(E_{\mathrm{eff}}\)」。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0004 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0004 BEGIN -->
- status: SUPPORTED
- evidence_refs: EVD-0005
- core: true
---
在分段常数 \(P(t)\) 下，同一组负荷的顺序会改变 TTE。known-answer：\(E_{\mathrm{eff}}=15\,\mathrm{Wh}\)，先 \(6\,\mathrm{W}\times 1\,\mathrm{h}\) 再 \(0.3\,\mathrm{W}\) 得 \(31\,\mathrm{h}\)；对调顺序得 \(3.45\,\mathrm{h}\)，比值约 \(9\)。平均功率模型看不见这个差。这是能量守恒的路径依赖，不是实测日程。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0004 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0005 BEGIN -->
- claim_ref: CLM-0004
- polarity: SUPPORT
- kind: COMPUTATION
- source_citation: run:05_代码/美赛2026-A/outputs/soc-piecewise-001
---
`metrics.json` sha256 `70176e49536954d2f0751241b9f3d2ae50432a86dd27b112a105bd8e979f0f3c`。`tte_burst_first_hours=31.0`，`tte_idle_first_hours=3.45`，`soc_burst_at_1h=0.6`，Euler 与解析解在 \(t=1\,\mathrm{h}\) 一致，`order_ratio≈8.99`。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0005 END -->
