# Assumptions

本文件是假设的权威记录。

<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0001 BEGIN -->
- status: ACTIVE
- scope: 电池被表示为一个集总锂离子储能单元，输出标量 SOC(t)
- rationale: 赛题要求连续时间 SOC，而不是电极内部浓度场。Doyle–Fuller–Newman 一类分布模型在缺少开源 identifiability 数据时不可识别，因此先用集总能量守恒。
- falsifiable_when: 恒定功率下 SOC 相对时间出现无法用容量缩放解释的强非线性，或端电压对 TTE 的影响超过功率项。
---
赛题要求假设锂离子电池。本假设把电池看成一个有效能量库 \(E_{\mathrm{eff}}\)，状态只用 \(\mathrm{SOC}\in[0,1]\)。不在基线中引入多节串并联、热失控或完整等效电路。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0001 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0002 BEGIN -->
- status: ACTIVE
- scope: 放电阶段能量守恒：\(E_{\mathrm{eff}}\dot{\mathrm{SOC}}=-P(t)\)
- rationale: SOC 的定义就是剩余能量与有效容量之比。把它写成连续时间微分方程，是满足「物理推理 + 连续时间」的最简定律；恒定功率下有解析解，可做 known-answer。
- falsifiable_when: 开源测量表明 Peukert / 倍率容量损失大到使 TTE 系统性偏离 \(E_{\mathrm{eff}}\mathrm{SOC}_0/P\)。
---
不把离散曲线拟合当作控制方程。Euler 离散只用于求解，不替代连续时间陈述。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0002 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0003 BEGIN -->
- status: ACTIVE
- scope: 总功率为屏幕、CPU、网络、GPS、后台与待机功率之和
- rationale: 赛题把这些因素列为可叠加的耗电贡献。先用线性叠加，才能逐项比较「谁最伤续航」。
- falsifiable_when: 交互项（例如高亮度与高 CPU 的热耦合）使总功率不能用分项之和近似。
---
\[
P(t)=P_{\mathrm{idle}}+P_{\mathrm{screen}}+P_{\mathrm{cpu}}+P_{\mathrm{net}}+P_{\mathrm{gps}}+P_{\mathrm{bg}}.
\]
<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0003 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0004 BEGIN -->
- status: ACTIVE
- scope: 温度与老化只通过有效容量进入模型：\(E_{\mathrm{eff}}=E_{\mathrm{nom}}\eta(T)\alpha\)
- rationale: 赛题点名低温掉容量与寿命历史。乘性缩放是对「有效容量下降」的最简编码，不必先引入完整 Arrhenius 老化动力学。
- falsifiable_when: 低温主要改变内阻/可用功率而不是可用能量，导致 TTE 变化不能用 \(\eta\alpha\) 吸收。
---
\(\eta(T)\) 与 \(\alpha\) 当前取情景常数，不是已校准的材料曲线。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0004 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0005 BEGIN -->
- status: ACTIVE
- scope: 预测 time-to-empty 的区间内不充电
- rationale: TTE 的定义是放到空的时间。充电会把问题变成另一条轨迹。
- falsifiable_when: 使用情景包含中途充电或无线边充边用。
---
基线只做放电。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0005 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0006 BEGIN -->
- status: ACTIVE
- scope: 当前数值是量级假设，不是开放数据集估计
- rationale: 赛题允许引用公开规格，但要求许可与文档。仓库里还没有开放许可的手机耗电数据集，因此参数一律标 ASSUMED，只用于机制比较与 known-answer。
- falsifiable_when: 登记了开放许可的功率/容量数据后，同一方程给出的 TTE 排序或量级被数据否定。
---
\(E_{\mathrm{nom}}=15\,\mathrm{Wh}\) 对应大约 \(4000\,\mathrm{mAh}\times 3.85\,\mathrm{V}\) 的量级，不是某一型号的实测。待引用公开规格后再替换。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0006 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0007 BEGIN -->
- status: ACTIVE
- scope: 真实一天的使用近似为分段常数 \(P(t)\)
- rationale: 赛题要求不同使用情景与使用模式波动。ODE 已允许任意 \(P(t)\)；分段常数是仍能解析求 TTE 的最简「一天」。
- falsifiable_when: 段内功率波动大到使分段 TTE 与细采样积分系统性偏离，或倍率容量使顺序效应与能量守恒预测相反。
---
段与段之间功率可跳变。不在基线中对段内再做随机过程。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0007 END -->
