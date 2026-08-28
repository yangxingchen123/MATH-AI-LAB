# 赛题

- 赛事: 美赛（MCM/ICM）
- 年份: 2026
- 题号: A
- 标题: Modeling Smartphone Battery Drain
- 官方题面路径: `03_参考资料/竞赛/美赛/2026-A/source.pdf`
- source_sha256: `e88b8e4a57f89754deffb427015e649f35ea0698c341322a7a7d17ff9ce324f0`
- 转写路径: `03_参考资料/竞赛/美赛/2026-A/derived/p0001-0003.md`（PDFTomd chunk；较干净）
- 转写备档: `03_参考资料/竞赛/美赛/2026-A/derived/2026美赛A.md`（笔记版；大量 `$t_{0}$` 误识别）
- parse_status: DEGRADED（外部 PDFTomd，非 MinerU；Requirement 1 有一段 OCR 乱码）
- 基线模型: 能量守恒 ODE（DEC-0001 / CLM-0001）

引用约定：`QUOTE` = 转写中可读的原文；`PARAPHRASE` = 转述；`INFERENCE` = 我们的推断，不是赛题原句。

## 问题重述

**PARAPHRASE.** 智能手机续航看起来不稳定：有时能撑一整天，有时午饭前就耗尽。用户常把这归因于 “heavy use”，但耗电其实由屏幕尺寸与亮度、处理器负载、网络活动、后台应用，以及温度、电池历史与充电方式共同决定。

**QUOTE.** 核心任务：

> develop a continuous-time mathematical model of a smartphone's battery that returns the state of charge (SOC) as a function of time under realistic usage conditions. This will be used to predict the remaining time-to-empty under different conditions. You should assume that the phone has a lithium-ion battery.

**PARAPHRASE.** 数据只可用于估计参数和验证，不能替代连续时间模型。只做离散曲线拟合、逐步回归或黑箱机器学习、而没有显式连续时间模型，不满足本题。所用数据必须有文档、可自由获取，且开放许可。

**QUOTE（硬约束，出现两次）.**

> Your model must be grounded in clearly defined physical or mechanical reasoning; discrete curve fitting or other mathematical forms that are disconnected from an explicit continuous-time description of battery behavior will not satisfy the requirements.

**OCR 损坏（不得补写）.** Requirement 1 在 “using a” 与 “simplest reasonable description of battery drain” 之间有乱码 `eon ynn w nn n w nsns o w-snn`。2026-08-22 用 `pypdf` 读 `source.pdf`：`extract_text()` 三页皆空；内容流是矢量描边（无文本层），不能据此修补。仍以 PDFTomd 转写为准，不猜测该句。

**转写编号异常.** 要求列表出现两个 `2.`、两个 `3.`。下面按语义拆成问号，不假装官方编号已经干净。

**术语（QUOTE，Glossary）.**

- SOC：剩余能量相对满容量的比例，常用百分比。
- Time-to-Empty：电池完全放空前的估计剩余时间。
- Power Consumption：从电池取电的功率。
- Processor Load：处理器当前实际工作量。

## 要交付的问号

1. **连续时间 SOC 模型.** 先给出电池消耗的最简合理连续时间描述，再加入屏幕、处理器负载、网络、GPS 与其他后台任务等贡献项。数据只作支撑。
2. **Time-to-Empty.** 在不同初始电量和使用情景下计算或近似放空时间；与观测或合理行为比较；量化不确定性；指出模型何处好、何处差。
3. **差异与快速耗电驱动.** 说明模型如何解释不同结果，并指出各情景下快速掉电的具体驱动因素。（转写中编号为第二个 `2.`）
4. **影响大小.** 哪些活动或条件最缩短续航？哪些对模型结果出乎意料地几乎无影响？（转写中编号为第一个 `3.`）
5. **敏感性与假设.** 改变建模假设、参数值和使用模式波动后，预测如何变化。
6. **建议.** 把结果译成用户可执行的省电建议（如降亮度、关后台、切换网络模式）；操作系统可如何据此做更有效的省电；并考虑电池老化降低有效容量，以及框架能否推广到其他便携设备。

## 论文必须包含（QUOTE 结构）

- 模型与控制方程的清楚描述
- 假设与设计选择的理由
- 参数估计方法与验证结果
- 优点、局限与可能推广
- 一页式执行摘要（主要结果、洞察、建议）
- 提交 PDF ≤ 25 页：Summary Sheet、目录、完整解答、文内引用与参考文献；若使用生成式 AI，另附 AI Use Report（不计入 25 页）
