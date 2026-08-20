# MATH-AI-LAB 数学建模与可复现实验规范

**状态：** Candidate
**上位契约：** [博士级数学研究工作台总架构](2026-08-20-doctoral-research-workbench-design.md)
**对应版本：** v1.4 Modeling & Reproducible Experiment Framework

---

## 1. 目标

工作台必须帮助研究者把现实问题转为定义明确、可求解、可验证、可解释且可复现的模型。它提供模型选择、环境隔离、运行记录和验证框架，不重新实现所有求解器，也不把“代码能运行”当作“模型正确”。

---

## 2. 能力与引擎分离

最终模型家族保持完整：符号模型、线性规划、整数规划、非线性规划、凸优化、多目标优化、鲁棒优化、随机优化、网络与图模型、ODE、PDE、数值模拟、统计模型、参数估计、机器学习比较基线。

候选引擎仅是默认适配方向：

| 场景 | 候选引擎 | 最小 fallback |
| --- | --- | --- |
| 符号推导 | SymPy | 人工推导 + 数值抽查 |
| 数值 / ODE / 通用优化 | NumPy / SciPy | 已知答案小实例 |
| 数据处理 | pandas | 标准 CSV/Parquet 接口 |
| 凸优化 | CVXPY | 开源求解器 |
| LP / MIP / NLP | Pyomo + 项目选定求解器 | 开源可用求解器或降级为导出模型 |
| 网络与路径 | NetworkX | 规范化节点/边数据 |
| 统计模型 | statsmodels | 显式估计与诊断接口 |
| 机器学习基线 | scikit-learn | 固定切分与简单基线 |
| PDE / 专用仿真 | 项目级专用环境 | 可验证基准算例 |

商业引擎、GPU 和专用硬件不得成为工作台 Core 的强制条件。每个引擎记录操作系统、Python、CPU/GPU、许可证、版本、fallback 和最近 health-check。

---

## 3. 标准建模流程

```text
现实问题
→ 决策边界与研究问题
→ 假设及可证伪条件
→ 集合 / 参数 / 变量 / 单位
→ 目标函数、方程与约束
→ 数据、来源和数据等级
→ 小规模已知答案实例
→ 求解或仿真
→ 结构不变量与数值诊断
→ 基线比较
→ 敏感性 / 不确定性 / 鲁棒性
→ 解释、局限、反例和决策
```

每一步必须能回到 canonical `assumptions.md`、`evidence.md` 或 append-only `decisions.md`，Dossier 只提供导航。

---

## 4. 项目隔离

模型项目放在：

```text
05_代码/<项目>/
├── pyproject.toml
├── lock/                    # 选择一种受支持的精确锁定形式
├── src/
├── tests/
├── configs/
├── data/
│   ├── README.md
│   └── manifests/
├── experiments/
├── figures/
└── outputs/
    └── <run-id>/
```

约束：

- 依赖锁在项目环境，不进入 Foundation 根环境；
- Notebook 可用于探索，但正式 run 必须有脚本或命令入口；
- 原始大数据遵守外部存储政策，只提交 manifest、URI、hash 和许可；
- secrets 只从环境或 secret store 获取；
- 每个正式结果必须能够在干净环境由记录命令重建。

---

## 5. Run Manifest

每个正式运行生成不可变、可机读 manifest。它扩展总架构 Provenance Envelope，不是新的全局 Frozen Schema。

```yaml
run_id: "project-local immutable id"
status: "QUEUED | RUNNING | SUCCEEDED | PARTIAL | FAILED | CANCELLED"
git_commit: "40-character commit"
dirty_worktree: false
command: ["python", "-m", "package.entry", "--config", "configs/base.yaml"]
inputs:
  - ref: "dataset or upstream run"
    sha256: "64 lowercase hex characters"
config_sha256: "64 lowercase hex characters"
environment:
  os: "exact OS"
  python: "exact version"
  lock_sha256: "64 lowercase hex characters"
  packages_ref: "environment export path"
solver:
  name: "name or null"
  version: "exact version or null"
  license: "license class or null"
randomness:
  seeds: [0]
  deterministic_claim: "exact | tolerance | statistical"
started_at: "RFC 3339 UTC"
finished_at: "RFC 3339 UTC or null"
outputs:
  - ref: "artifact path"
    sha256: "64 lowercase hex characters"
metrics: {}
diagnostics: {}
logs:
  stdout_ref: "stdout log path"
  stderr_ref: "stderr log path"
```

`dirty_worktree: true` 的 run 可以用于探索，但不得成为正式发布的唯一依据。随机或并行计算必须说明确定性层级和容差，禁止把不可保证的逐字节确定性写成承诺。

---

## 6. 模型验证协议

每个正式模型按适用性执行：

1. 单位与维度一致；
2. 集合、变量域和参数范围明确；
3. 约束可行性或方程适定性；
4. 守恒、不变量、单调性、对称性等结构性质；
5. 边界、极端和退化情景；
6. 手算或已知答案小实例；
7. 与朴素基线或既有方法比较；
8. 参数敏感性与不确定性；
9. 可识别性或不可识别性；
10. 求解器状态、可行解、局部/全局最优含义；
11. 数值容差、离散化误差与收敛；
12. 数据泄漏、训练/验证/测试隔离；
13. 结果允许解释的范围；
14. 失败、反例和违反假设时的行为。

未适用的检查必须写明理由，不能静默省略。

---

## 7. 家族专项要求

| 家族 | 额外强制检查 |
| --- | --- |
| 符号模型 | 定义域、分支、奇点、符号假设 |
| LP / MIP | 可行性、界、gap、整数容差、infeasible certificate |
| NLP | 初值、局部性、梯度/Hessian、constraint qualification |
| 凸优化 | 凸性、Slater 条件、对偶和 KKT 适用性 |
| 多目标 | 标量化选择、Pareto 支配和权衡解释 |
| 鲁棒/随机优化 | 不确定集或分布假设、场景覆盖和外样本表现 |
| 网络模型 | 节点/边语义、方向、权重、连通与拓扑不变量 |
| ODE | 初值/边值、存在唯一性、稳定性、步长误差 |
| PDE | 边界条件、适定性、网格收敛和数值稳定性 |
| 统计模型 | 采样机制、残差、置信区间、多重比较、效应量 |
| 参数估计 | 识别性、profile/后验、不确定性和参数相关 |
| 机器学习基线 | 数据泄漏、拆分、调参边界、校准和简洁基线 |

---

## 8. 复现等级

| 等级 | 要求 |
| --- | --- |
| R0 探索 | 代码或 Notebook 可运行，非正式证据 |
| R1 重复 | 同一环境、同一输入、同一配置可重复 |
| R2 重建 | 干净环境按 lock 和 manifest 重建 |
| R3 独立复核 | 第二执行者按文档复现并核对解释 |

`PILOT` 至少达到 R2；`VERIFIED` 至少在两个不同项目达到 R3。

随机实验的复现不能只比较某一次输出 hash。应固定随机策略，并比较预先定义的统计量、置信区间或误差容差。

---

## 9. 失败、取消与恢复

- `FAILED` 保存输入、配置、环境、日志、求解器状态和部分诊断；
- `PARTIAL` 明确哪些场景/分片成功，哪些缺失；
- `CANCELLED` 记录取消发起者、原因和最后一致 checkpoint；
- 重试使用新 `run_id` 并以 `retry_of` 连接；
- 失败 run 不被成功 run 覆盖，也不能从报告中删除；
- 输出先写隔离目录，全部验证通过后才注册为成功 artifact；
- 引擎不可用时可以切换已验证 fallback，切换必须形成新 run 和新 provenance；
- 无安全 fallback 时显式阻断对应能力，不伪造结果。

负结果和失败路线应进入研究决策记录，尤其包括模型不可识别、不可行、基线更优、假设被反例推翻和数值不稳定。

---

## 10. Figure 与 Claim 接口

模型结果只有通过验证 Gate 后才可被正式 Figure 消费。Figure manifest 必须引用准确 `run_id`、输出 hash、变量/指标定义和 Claim ref。重新运行若改变输入、配置或环境，旧图不得自动宣称仍代表新结果。

数值图不能自动提升 Claim 的信任级；Claim 是否从 `DERIVED` 变为 `REVIEWED` 取决于模型审查、数据审查和解释审查。

---

## 11. Health-check

建模 `doctor` 只读报告：

- 项目环境是否可创建和锁定；
- Python、核心库、求解器及许可证；
- CPU/GPU 和平台限制；
- 最小已知答案实例的状态；
- 上次成功 run 和 Evidence；
- fallback 可用性；
- 数据入口是否满足等级和许可要求。

health-check 不自动下载商业求解器、不接受许可证、不写正式结果。

---

## 12. v1.4 强制 Gate

- Run manifest 必填字段完整率 `100%`；
- 输入、配置、环境锁和产物 hash 覆盖率 `100%`；
- 至少一个优化家族与一个非优化家族达到 `PILOT`；
- 两个 Pilot 均通过已知答案实例、同环境重复、干净环境重建；
- 超出容差的重建差异检出率 `100%`；
- 失败 run 历史保留率 `100%`；
- 无效求解状态被误标为成功的次数 `0`；
- 未记录许可证的非默认求解器进入正式 run 的次数 `0`。

其余模型家族保持 `TARGET` 不等于删减；成熟度按路线矩阵逐项提升。
