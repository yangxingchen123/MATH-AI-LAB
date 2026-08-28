# 模型选取

对每个候选模型写清：为什么想到、适用条件、数据需求、可检验预测、否决理由。

禁止用「显然适合」跳过选取。未选中的路线记入 `negative_results.md`。

| 候选 | 针对的问号 | 选用 / 否决 | Decision 引用 |
| --- | --- | --- | --- |
| 能量守恒 ODE（集总 SOC） | Q1–Q3, Q5 | 选用（基线） | DEC-0001 |
| Thevenin / 等效电路 | Q1, Q2（若需电压） | 暂缓 | DEC-0001 |
| 仅离散拟合或黑箱 ML | 全部 | 否决 | DEC-0001 |

清单机读副本：`05_代码/美赛2026-A/configs/candidates.yaml`。

## 为什么想到能量守恒

赛题要的是 \(\mathrm{SOC}(t)\) 和 time-to-empty，并且必须有连续时间物理陈述。SOC 的定义已经是「剩余能量 / 有效容量」。因此最简合理定律是

\[
E_{\mathrm{eff}}\frac{\mathrm{d}}{\mathrm{d}t}\mathrm{SOC}(t)=-P(t),\qquad
E_{\mathrm{eff}}=E_{\mathrm{nom}}\eta(T)\alpha.
\]

若 \(P\) 在一段使用情景内近似为常数，则

\[
\mathrm{SOC}(t)=\mathrm{SOC}_0-\frac{P}{E_{\mathrm{eff}}}t,\qquad
t_{\mathrm{empty}}=\frac{E_{\mathrm{eff}}\mathrm{SOC}_0}{P}.
\]

这给出可证伪预测：恒定负载下 SOC 必须近似直线，TTE 必须与功率成反比。然后再按 ASM-0003 把 \(P\) 拆成屏幕 / CPU / 网络 / GPS / 后台，回答「谁最伤续航」。

Thevenin 电路能解释电压平台，但当前没有开放许可的 I–V 数据，参数不可识别。黑箱回归被赛题原文排除。

## 适用与否决

- **适用：** 放电、功率可按使用情景给定或估计、关心的是时间而不是端电压波形。
- **否决 ML-only：** 与赛题 “data as support, not substitute” 冲突，不是因为「不高级」。
- **暂缓等效电路：** 等有开源电压数据再打开，不在基线里假装已经校准。
