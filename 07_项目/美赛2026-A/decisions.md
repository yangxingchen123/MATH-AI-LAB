# Decisions

本文件是研究决策的权威记录（append-only）。

<!-- MATH-AI-LAB:RESEARCH-RECORD type=DECISION ref=DEC-0001 BEGIN -->
- date: 2026-08-22
- question: 用什么连续时间对象表示 SOC 并预测 TTE？
- options: 能量守恒 ODE|Thevenin 等效电路|黑箱回归/机器学习
- choice: 能量守恒 ODE
- basis: 赛题禁止把离散拟合或黑箱 ML 当作唯一模型；能量守恒直接给出 SOC(t) 与解析 TTE，且分项功率可检验。等效电路留到需要电压时再加。
- cost: 忽略电压效率与倍率容量，可能高估或低估真实 TTE。
- reversible: true
- revisit_when: 得到开放许可的电压–电流轨迹，或恒功率 known-answer 与公开测量系统性偏离。
---
为什么先想到能量守恒：SOC 被赛题定义为剩余能量相对满容量的比例。把它微分，立刻得到 \(\dot{\mathrm{SOC}}=-P/E_{\mathrm{eff}}\)。这比先上等效电路更可识别，也比「直接拟合 SOC 曲线」更符合物理推理要求。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=DECISION ref=DEC-0001 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=DECISION ref=DEC-0002 BEGIN -->
- date: 2026-08-22
- question: 用什么量比较「谁最伤续航」并给出省电建议？
- options: 分项功率份额/弹性|只比较情景 TTE 差值|先拟合真实耗电数据再排序
- choice: 分项功率份额/弹性
- basis: 在 \(t_{\mathrm{empty}}=E_{\mathrm{eff}}\mathrm{SOC}_0/P\) 下，对分项 \(P_i\) 的相对弹性恰好是 \(-P_i/P\)。排序不依赖容量和初始电量，可直接回答 Q4 并翻译成 Q6。
- cost: 若功率不可加或效率随负载变化，份额排序会错。
- reversible: true
- revisit_when: 开放许可数据否定可加性，或电压效率项进入基线。
---
为什么想到弹性：问的是「改哪个活动，TTE 变多少」。相对弹性把「变化」标准化。对本模型它退化成分额，这既是简化也是可证伪点。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=DECISION ref=DEC-0002 END -->

<!-- MATH-AI-LAB:RESEARCH-RECORD type=DECISION ref=DEC-0003 BEGIN -->
- date: 2026-08-22
- question: 如何表示「使用模式波动」而不离开连续时间能量守恒？
- options: 分段常数 P(t)|把一天压成平均功率|随机微分方程
- choice: 分段常数 P(t)
- basis: 平均功率抹掉顺序；SDE 在无开放轨迹时不可识别。分段常数保留顺序，TTE 仍是能量积分的首次到达时间。
- cost: 段内波动被忽略；known-answer 用的 6 W / 0.3 W 仍是假定。
- reversible: true
- revisit_when: 有开放许可的按小时使用轨迹，或需要段内噪声。
---
为什么想到分段：同一组活动「先重后轻」和「先轻后重」会在不同时刻抽走能量。能量守恒下 TTE 是剩余能量沿 \(P(t)\) 走到零的时间，所以顺序必须进模型。
<!-- MATH-AI-LAB:RESEARCH-RECORD type=DECISION ref=DEC-0003 END -->
