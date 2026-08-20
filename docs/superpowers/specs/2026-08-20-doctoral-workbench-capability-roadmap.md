# MATH-AI-LAB 能力成熟度与版本路线

**状态：** Candidate
**上位契约：** [博士级数学研究工作台总架构](2026-08-20-doctoral-research-workbench-design.md)

---

## 1. 职责

本文负责回答三个问题：某项能力当前处于什么成熟度、哪个版本交付什么框架、用什么证据才允许关闭版本。本文不保存实时状态；实现后的状态只写入 `09_长期记忆/项目进度.md`。

---

## 2. 成熟度状态机

```text
TARGET → PILOT → STABLE → VERIFIED
```

| 状态 | 进入条件 | 禁止表述 |
| --- | --- | --- |
| `TARGET` | 能力已获范围批准并有专项设计 | “已经支持” |
| `PILOT` | 固定 fixture 和一个真实项目 Gate 通过 | “普遍可用” |
| `STABLE` | 契约、失败语义、回归、health-check 和迁移规则稳定 | “所有场景已验证” |
| `VERIFIED` | 至少两个不同类型真实项目复用且专项关闭 Gate 通过 | 无 Evidence 的“博士级完成” |

引擎另设 `SUPERSEDED_ENGINE`：新引擎通过兼容测试和迁移期后，旧引擎可标为被替代；对应能力不得因此降为不存在。

状态变更记录必须包含：能力、旧状态、新状态、Gate Evidence、验证日期、适用范围、已知限制、回滚或降级方式。

---

## 3. Gate Template

每个 Gate 都必须填满以下字段：

```yaml
gate_id: "version-or-capability/gate-name"
baseline: "exact reproducible state"
metric: "one or more computable measures"
threshold: "explicit pass values"
fixture:
  ref: "immutable fixture reference"
  sha256: "fixture hash"
evidence:
  - "test log, manifest, review or artifact path"
failure_action: "BLOCK | ROLLBACK | DEGRADE with exact action"
```

关闭规则：全部强制 Gate 通过；失败项不得用口头解释豁免。确需改变 Threshold 时，先修订规范并保留决策记录，不能在验收后反向降低标准。

---

## 4. 能力覆盖矩阵

矩阵中的“v1 交付点”表示首次形成可测试框架，不表示直接达到 `VERIFIED`。

| 能力组 | 子能力 | 首次交付 | v2.2 最低状态 |
| --- | --- | --- | --- |
| 研究管理 | 问题、边界、假设、决策、负结果 | v1.1 | `VERIFIED` |
| 文档 | PDF、扫描 PDF、图片、DOCX、PPTX、XLSX | v1.2 | PDF / 扫描 PDF `VERIFIED`；其余 `STABLE` |
| 解析 | 标题、段落、列表、公式、表格、图片、脚注、阅读顺序 | v1.2 | 关键研究对象 `VERIFIED` |
| 精选 | 原页复核、精确锚点、引用/转述/推断 | v1.2–v1.3 | `VERIFIED` |
| 文献 | 身份、版本、DOI、引用、比较、撤稿/更正 | v1.3 | `VERIFIED` |
| 证据 | 支持证据、反对证据、Claim–Evidence、Novelty Matrix | v1.3 | `VERIFIED` |
| 数学 | 严格推理、反例、边界、条件、一般化 | 既有 + v1.7 | `VERIFIED` |
| 建模 | 模型选择、配置、运行、验证、解释 | v1.4 | 框架 `VERIFIED`；家族见 §5 |
| 实验 | 环境锁定、运行清单、复现、负结果 | v1.4 | `VERIFIED` |
| 制图 | 静态、交互、精确数学图、动画、概念插图 | v1.5 | 框架 `VERIFIED`；家族见 §6 |
| Lean | 候选形式化、构建、语义对照、漂移检测 | v1.6 | `STABLE`，至少两类命题 `VERIFIED` |
| 审稿 | 证明、模型、文献、数据、成果一致性 | v1.7 | `VERIFIED` |
| 写作发布 | LaTeX、论文、补充材料、P9 | 既有 + v1.8 | `VERIFIED` |
| 知识复用 | Reviewed → 授权 → Formal Knowledge | v1.8 | `VERIFIED` |
| 检索/RAG | Metadata、FTS、BM25、向量、Hybrid、Cited RAG | v2.0 | Hybrid 与引用式回答 `VERIFIED` |
| 多角色 | Solver、Skeptic、Verifier、Literature、Modeling、Formalizer、Reproducer、Editor | v2.1 | 受控编排 `STABLE`；关键角色 `VERIFIED` |
| 长期记忆 | 项目状态、研究轨迹、能力成长 Evidence | v1.1–v2.2 | `VERIFIED` |
| 治理 | 数据等级、Git、许可、AI 贡献、保留策略 | v1.1 起 | `VERIFIED` |

---

## 5. 模型家族覆盖矩阵

v1.4 关闭的是统一 Modeling Framework。每个家族独立记录成熟度，禁止用两个 Pilot 代表全部覆盖。

| 模型家族 | 最小验证对象 | v1.4 要求 | v2.2 最低状态 |
| --- | --- | --- | --- |
| 符号模型 | 可手算恒等或解析结果 | `PILOT` | `STABLE` |
| 线性规划 | 已知最优解小实例 | `PILOT` | `VERIFIED` |
| 整数规划 | 已知整数最优解与界 | `TARGET` | `STABLE` |
| 非线性规划 | 局部/全局含义明确的基准 | `TARGET` | `STABLE` |
| 凸优化 | KKT / 对偶可核对实例 | `PILOT` | `VERIFIED` |
| 多目标优化 | 可核对 Pareto 前沿 | `TARGET` | `STABLE` |
| 鲁棒优化 | 不确定集与最坏情景 | `TARGET` | `STABLE` |
| 随机优化 | 固定种子与统计容差 | `TARGET` | `STABLE` |
| 网络与图模型 | 已知路径、流或匹配结果 | `PILOT` | `VERIFIED` |
| ODE | 具有解析解或守恒量的系统 | `PILOT` | `VERIFIED` |
| PDE | 具有基准解和网格收敛证据的算例 | `TARGET` | `STABLE` |
| 数值模拟 | 可重复仿真与误差分析 | `PILOT` | `VERIFIED` |
| 统计模型 | 合成数据与已知参数 | `PILOT` | `VERIFIED` |
| 参数估计 | 识别性与置信/不确定性分析 | `PILOT` | `VERIFIED` |
| 机器学习比较基线 | 无数据泄漏的固定切分基线 | `TARGET` | `STABLE` |

任何家族升为 `STABLE` 前，必须通过单位/域、已知答案实例、求解状态、敏感性、环境复现和失败隔离六类 Gate。专用工具、商业求解器或 GPU 只能是可选引擎；必须记录许可及 fallback。

---

## 6. 制图家族覆盖矩阵

v1.5 关闭的是 Figure Contract 和出版流程，不代表每个渲染引擎均已验证。

| 图形家族 | 精确性要求 | v1.5 要求 | v2.2 最低状态 |
| --- | --- | --- | --- |
| 函数与数学对象图像 | 坐标、定义域、参数可追溯 | `PILOT` | `VERIFIED` |
| 数值与统计图 | 数据、单位、不确定性可追溯 | `PILOT` | `VERIFIED` |
| 误差/收敛/敏感性图 | 指标和基准明确 | `PILOT` | `VERIFIED` |
| 热力图/等高线/三维曲面 | 网格、色标和投影明确 | `TARGET` | `STABLE` |
| 网络与路径图 | 拓扑和权重由数据生成 | `TARGET` | `STABLE` |
| 几何与精确数学图 | 几何关系可核查 | `PILOT` | `VERIFIED` |
| 算法流程与架构图 | 节点/关系与规范一致 | `PILOT` | `STABLE` |
| 交互式探索 | 与静态正式图同源 | `TARGET` | `STABLE` |
| 出版级静态图 | 矢量、字体、版面、灰度可读 | `PILOT` | `VERIFIED` |
| 数学动画 | 时间参数、状态和脚本可重建 | `TARGET` | `STABLE` |
| 非精确概念插图 | 明示非数据/非证明图 | `TARGET` | `STABLE` |

AI 图像不得承担精确坐标、数据值、拓扑或证明关系。二进制 hash 因嵌入元数据发生差异时，必须同时比较规范化内容或语义 manifest，不能伪称逐字节确定性。

---

## 7. 版本关闭矩阵

### v1.0.1 — Foundation Portability Closure

- **Baseline：** 设计时 `615 passed, 3 failed`，失败与硬编码 Windows 路径有关。
- **Metric：** Core、完整 pytest、新增 Windows/POSIX 路径回归、LaTeX smoke。
- **Threshold：** 所有强制测试 `0 failed`；`verification core PASS`；`latex-smoke PASS`；`workspace CURRENT`；远程 Core 绿色；无仓库根绝对路径假设。
- **Fixture：** 临时仓库根、含空格路径、POSIX 与 Windows 风格输入。
- **Evidence：** 本地测试日志与远程 CI run。
- **Failure Action：** 阻断 v1.1；回滚生产修改，保留失败测试。

### v1.1 — Research Project & Dossier

- 交付 Dossier 导航、canonical assumptions/evidence/decisions、负结果和项目级 provenance；
- 固定“摘要不是事实源”规则；
- 至少一个真实项目完成创建、更新、审查和无破坏回滚；
- 未经授权不得创建 Knowledge 或修改 Frozen Schema。

### v1.2 — Document Intelligence

- MinerU CLI/API Sidecar、输入 hash、缓存、Derived Package、页级 QA；
- PDF 与扫描 PDF Pilot 必须包含公式、表格、双栏或版面复杂样例；
- 关键精选内容必须能回到 page index、printed label、bbox 与 source hash；
- 部分失败不得被标记为成功。

### v1.3 — Literature Evidence

- 文献身份、版本、DOI、BibTeX/CSL、支持/反对证据和 Novelty Matrix；
- 核心 Claim 的 citation coverage 为 `100%`；
- 已知撤稿/更正 fixture 必须被识别并阻断未经说明的正式引用；
- 引用、转述和推断分类准确率在固定评测集达到 `100%`。

### v1.4 — Modeling & Reproducible Experiment Framework

- 统一模型项目边界、run manifest、长任务状态和验证清单；
- 至少一个优化家族与一个非优化家族达到 `PILOT`；
- 同环境和干净环境均能重建结果，容差写入 Gate；
- 家族覆盖按 §5 独立报告，禁止宣称 15 个家族全部完成。

### v1.5 — Figure & Visualization Framework

- Figure manifest、Claim/Run 连接、静态发布、可访问性和 LaTeX 集成；
- 至少完成数值图、网络图、精确数学图和流程/架构图四个不同家族 Pilot；
- 每张正式图的源程序、数据、配置和 provenance 可追溯；
- 图形覆盖按 §6 独立报告。

### v1.6 — Lean Formalization

- 单一 Lake 工程、锁定工具链、语义对照和路径 CI；
- 至少两类真实命题构建通过；
- 正式通过不得含 `sorry`、`admit` 或用于绕过证明的新增 `axiom`；
- 工具链失败不阻塞非 Lean 研究路径。

### v1.7 — Critical Review

- 建立 Proof / Evidence / Model / Reproducibility / Formalization / Editor 六类审查；
- 固定缺陷 fixture 必须被对应角色发现；
- 严重缺陷阻断 Formal 发布；
- 审查意见、处置和复核结果可审计。

### v1.8 — Research Writing & Artifact Consistency

- 论文、引用、代码、数据、图表、Lean、补充材料和 PDF 建立一致性检查；
- AI 贡献和作者责任记录完整；
- Knowledge 晋升只发生在明确 `开始知识沉淀` 授权后；
- P9 仍为正式 PDF 发布唯一入口。

### v2.0 — Hybrid Retrieval & Cited RAG

- Metadata → FTS → BM25 → Vector → Hybrid 的增量路线有对照基线；
- 固定评测集达到专项检索阈值；
- 核心回答 citation coverage `100%`，unsupported attribution `0`；
- 权限过滤在召回前执行，Restricted 内容不得外泄。

### v2.1 — Controlled Multi-Agent Research

- 角色输入、输出、工具调用、成本、状态和复核均可审计；
- Agent 只产出 Candidate，不得直接修改正式 Source；
- 固定评测任务上，质量指标至少一项显著优于单角色基线，且严重错误率不升高；
- 超时、取消和单角色 fallback 可用。

### v2.2 — Doctoral Research Workbench Closure

- 总架构 18 项能力均达到 §4 最低状态；
- 至少两个不同类型真实项目端到端复用；
- 安全、许可、学术诚信、失败恢复和成果一致性 Gate 全部通过；
- 第二个项目没有依赖第一个项目的硬编码路径、数据或模板特例。

---

## 8. CI 与验证配置

| 配置 | 安装范围 | 强制性 |
| --- | --- | --- |
| `core` | Foundation 根环境 | 每次修改必跑 |
| `latex-smoke` | 现有 P9 / XeLaTeX 构建边界 | LaTeX 与发布路径修改必跑 |
| `document-smoke` | Adapter + fixture，不下载完整模型时使用 fake/service mock | 文档模块修改必跑 |
| `modeling-smoke` | 小型开源求解器与已知答案 fixture | 建模模块修改必跑 |
| `figure-smoke` | 无头渲染与确定性 fixture | 制图模块修改必跑 |
| `lean` | 锁定 Lean/Mathlib 工具链 | Lean 路径修改必跑 |
| `retrieval-eval` | 固定 corpus 与 query set | 检索/RAG 修改必跑 |
| `full-integration` | 所有获批 Sidecar | 发布候选与定期验证 |
| `research-acceptance` | 两个真实项目的端到端复用 | v2.2 关闭必跑 |

Core 失败始终是发布阻断项。可选 Sidecar 不可用时只能降级对应能力，不得让 Core 产生假失败，也不得伪报 Sidecar 通过。

所有测试继续遵守 Attempt 真实性保护：不得为了 fixture、coverage、统计或演示伪造用户 Attempt，也不得让任何 Sidecar 测试写入 production Source。

---

## 9. 状态报告格式

每次版本评审只允许报告：

1. 当前真实 Baseline；
2. 本版本新增或加强的能力；
3. 各子能力成熟度与 Evidence；
4. 未通过 Gate、失败原因和影响；
5. 已启用 fallback；
6. 下一版本前的阻断项。

禁止用代码量、已安装工具数量或演示截图代替能力证据。
