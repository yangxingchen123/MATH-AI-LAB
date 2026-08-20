# MATH-AI-LAB 博士级数学研究工作台全功能升级设计

**设计日期：** 2026-08-20

**文档状态：** 已完成会话级总体设计确认，等待仓库级人工审核

**适用项目：** MATH-AI-LAB

**设计类型：** Umbrella Architecture / Capability Roadmap

**实施状态：** 未开始

---

## 1. 文档职责与权威边界

本文定义 MATH-AI-LAB 从 Foundation v1 数学学习工作台升级为博士级数学研究工作台的目标能力、架构边界、数据流、失败语义、验证策略和分阶段路线。

本文是**设计与路线 authority**，不是 Frozen Schema authority，也不是对当前生产状态的宣称。它不得覆盖：

- `项目规则.md`；
- `元数据规范.md` 中已冻结的 Knowledge / Problem / Attempt / Method Schema；
- `AGENTS.md` 的高频执行规则；
- `09_长期记忆/项目进度.md` 的当前动态状态；
- 已有 Normal Operation、P9、Workspace 和 Verification 的生产语义。

如本文与上述 authority 冲突，实施前必须修订本文或形成明确的版本化迁移设计，不得直接改变 Frozen Schema。

本文批准的是**全功能目标**，不是一次性实现全部能力的授权。每个版本仍须单独设计、计划、测试、审核和实施。

---

## 2. 背景与当前事实

MATH-AI-LAB 已建立以下 Foundation 能力：

- Problem 中心化；
- Attempt 与 AI Solution 分离；
- Canonical Solution；
- Knowledge / Problem / Attempt / Method 结构化对象；
- Validator、Indexer、Workspace 和 Generated View；
- Atomic Mutation；
- Normal Operation；
- LaTeX 构建、检查和原子发布；
- Verification Contract；
- AUTO / REVIEW / STUDY / RESEARCH 交互边界。

当前目标不再是继续横向堆叠 Foundation Registry，而是在保留上述核心语义的前提下，完整增加博士研究所需能力。

设计时已观察到一个必须先关闭的当前基线问题：仓库当前测试存量为 618，但 Linux / GitHub 环境存在 3 个由 `C:\MATH-AI-LAB` 绝对路径造成的失败。因此，升级实施的第一个版本必须是跨平台 Foundation Closure；在现有测试和新增回归测试全部通过、远程 Core 变绿前，不得把整体状态描述为跨平台完成。

---

## 3. 核心目标

最终系统必须支持从原始研究问题到正式成果的完整链路：

```text
研究问题
→ 文献与原始资料
→ 可追溯证据
→ 数学推理 / 数学模型 / 形式化命题
→ 计算实验与反例
→ 可复现结果
→ 正式图表
→ 严格审稿
→ LaTeX / PDF / 论文成果
→ 长期知识与研究记忆
```

系统是否成功，不以模块数量、代码行数、解析 PDF 数量或 AI 输出长度衡量，而以以下能力衡量：

1. 研究问题能否被准确界定；
2. 关键主张能否回到可靠来源或可验证推导；
3. 模型与实验能否独立复现；
4. 图表能否由代码和数据重新生成；
5. Lean 证明能否通过且与自然语言命题一致；
6. 失败路线和反对证据能否保留；
7. 论文、代码、数据、图表和补充材料能否保持一致；
8. 第二个不同类型的真实项目能否复用这些能力。

---

## 4. 不可削减的功能全集

本设计采用“功能不减少、架构解耦、能力分级、分期实现”的原则。以下能力均属于最终交付范围，不得在后续优化中无说明删除：

1. 研究问题与项目管理；
2. PDF 与多格式文档读取；
3. MinerU 文档解析；
4. 内容精选与原页复核；
5. 文献检索、版本识别、引用和比较；
6. Claim–Evidence 证据链；
7. 数学推理、反例、一般化和条件检查；
8. 多类型数学建模；
9. 可复现计算实验；
10. 负结果与研究决策记录；
11. 完整制图和出版级图表；
12. Lean / Mathlib 形式化；
13. 严格审稿、反驳和复核；
14. LaTeX、论文与正式成果发布；
15. 知识图谱与跨项目复用；
16. 全文检索、混合检索和可引用 RAG；
17. 受控多角色 / 多 Agent 研究协作；
18. 长期研究记忆和能力成长证据。

功能存在不等于每个任务强制调用。系统最终必须提供全部能力，但运行时只激活当前任务所需模块。

---

## 5. 设计原则

### 5.1 稳定核心不被重型能力污染

现有 Foundation 核心保持轻量：

```text
Problem / Attempt / Solution
Knowledge / Method
Validator / Indexer / Workspace
Normal Operation
LaTeX / PDF / Verification
```

MinerU、建模求解器、Lean、绘图和 RAG 使用独立环境或服务。不得把全部重型依赖加入根 `requirements.txt`。

### 5.2 功能完整与部署隔离并存

每项能力必须具备明确接口，但不得形成一个全局动态 Capability Registry 或新的通用 Agent Framework。第一阶段使用显式适配器、CLI、文件和 HTTP 接口。

### 5.3 Source / Derived / Reviewed / Formal 四级分离

| 等级 | 含义 | 可否直接作为正式结论 |
| --- | --- | --- |
| Source | 原始论文、教材、数据、题目 | 可作为依据，但仍需解释适用性 |
| Derived | MinerU 解析、程序输出、AI 草稿 | 不可直接晋升 |
| Reviewed | 已回查原文、验证模型或检查证明 | 可进入研究档案 |
| Formal | 已人工批准并正式发布 | 可进入正式知识和成果 |

### 5.4 研究主张必须可证伪

研究档案不只记录支持材料，还必须记录反对证据、边界、失败实验和可能推翻当前结论的条件。

### 5.5 数值验证不代替严格证明

Python、求解器、仿真和图像用于验证、探索或构造反例。它们不能自动替代严格数学证明。

### 5.6 Lean 编译不代替语义审核

`lake build` 通过只说明形式命题在给定环境中被证明，不说明形式命题准确表达了原始自然语言问题。形式化陈述必须人工核对。

### 5.7 失败隔离

外部能力失败不得破坏：

- 正式 Problem / Attempt / Knowledge / Method Source；
- 已发布 PDF；
- 现有 Generated Workspace；
- 已通过验证的研究结果；
- 普通数学回答。

### 5.8 递增而非替换

版本关系必须满足：

```text
v1.0.1 ⊂ v1.1 ⊂ v1.2 ⊂ ... ⊂ v2.2
```

生产稳定能力如需废弃，必须有版本化替代方案、迁移路径和兼容期，不允许静默删除。

---

## 6. 总体架构

```text
Interaction Layer
AUTO / REVIEW / STUDY / RESEARCH
        |
        v
Foundation Core
Problem / Attempt / Solution / Knowledge / Method
        |
        v
Research Capability Layer
Project / Document / Evidence / Modeling / Experiment
Figure / Lean / Review / Retrieval / Collaboration
        |
        v
External Engines
MinerU / Python Project Envs / Solvers / Lean+Mathlib
Plot Engines / Search Index / Vector Store / Model Providers
        |
        v
Evidence & Validation Layer
Provenance / Hash / Run Manifest / QA / Counterevidence
        |
        v
Artifact Layer
Markdown / JSON / Code / Data / Figure / Lean / LaTeX / PDF
```

### 6.1 Foundation Core

职责：

- 保持现有对象和工作流语义；
- 维护 Source、Generated 和 Artifact 的一致性；
- 为研究能力提供稳定身份和发布目标；
- 不直接承担 OCR、求解器、Lean 编译或向量检索。

### 6.2 Research Capability Layer

职责：

- 提供显式能力入口；
- 管理当前研究项目的资料、模型、实验、证据和审查；
- 将外部引擎输出转化为可检查的候选结果；
- 在人工批准后连接现有 Knowledge、Problem 和 P9。

### 6.3 External Engines

职责：

- 执行重型或专用任务；
- 使用独立版本、依赖和计算环境；
- 通过稳定文件或服务接口返回结果；
- 不直接修改正式 Source。

### 6.4 Evidence & Validation Layer

职责：

- 保存来源、页面、哈希、版本和运行配置；
- 区分原始事实、解析结果、AI 推断和人工结论；
- 执行质量检查、复现检查、反例检查和一致性检查。

---

## 7. 建议目录边界

现有规划目录继续使用，不新增重复职责的根目录：

```text
MATH-AI-LAB/
├── 03_参考资料/
│   └── <资料或项目>/
│       ├── source/             # 原始资料；默认不提交受版权保护的大文件
│       ├── derived/            # MinerU及其他解析输出
│       └── reviewed/           # 已核对精选资料与修订记录
├── 05_代码/
│   └── <建模项目>/
│       ├── pyproject.toml
│       ├── src/
│       ├── tests/
│       ├── configs/
│       ├── experiments/
│       ├── figures/
│       └── outputs/
├── 06_LEAN形式化/
│   ├── lakefile.toml
│   ├── lean-toolchain
│   ├── lake-manifest.json
│   ├── MathAILab/
│   │   ├── Problems/
│   │   ├── Knowledge/
│   │   ├── Methods/
│   │   └── Research/
│   └── Tests/
├── 07_项目/
│   └── <研究项目>/
│       ├── research_dossier.md
│       ├── assumptions.md
│       ├── evidence.md
│       ├── decisions.md
│       └── reports/
├── 04_LATEX/
├── 08_成果输出/
└── tools/
    ├── document_ingest/        # 后续版本
    ├── research_evidence/      # 后续版本
    ├── experiment_support/     # 后续版本
    ├── figure_build/           # 后续版本
    ├── lean_check/             # 后续版本
    ├── retrieval/              # v2后续版本
    └── research_review/        # v2后续版本
```

上述目录是目标边界，不授权本轮创建全部目录或工具。

---

## 8. Research Dossier

`07_项目/<项目>/research_dossier.md` 是研究项目的人工可读主导航，但第一阶段不是 Frozen Schema，也不分配新的全局对象 ID。

最小内容：

```markdown
# 研究项目

## 1. 研究问题
## 2. 研究边界
## 3. 当前假设
## 4. 待验证主张
## 5. 文献证据
## 6. 数学模型或证明
## 7. 实验与结果
## 8. 反例和失败路线
## 9. 决策记录
## 10. 当前贡献
## 11. 局限
## 12. 下一步
```

研究档案可以链接 P/K/M、代码、文献精选稿、实验运行、图表和 Lean 文件，但不得用路径替代已有 Frozen 对象 ID。

至少完成多个真实项目并观察到稳定查询需求后，才允许为 Research Question、Claim、Evidence、Paper 或 Source 提出候选 Schema。该评估不得反向修改现有 Frozen Schema。

---

## 9. 文档智能与 MinerU

### 9.1 能力范围

目标支持：

- PDF；
- 扫描 PDF；
- 图片；
- DOCX；
- PPTX；
- XLSX；
- 后续网页资料；
- 标题、段落、列表；
- 公式到 LaTeX；
- 表格到结构化格式；
- 图像、图注和脚注；
- 页码、阅读顺序和边界框；
- 多文献比较和证据精选。

### 9.2 部署边界

MinerU 使用独立环境或服务，不进入根 `requirements.txt`，不复制源码到 MATH-AI-LAB。v1.2 初始适配目标为固定 MinerU `3.4.5`；升级时必须执行输出兼容性测试。实施和分发时必须记录上游版本、许可证和必要归属，不得把模型文件或第三方依赖的再分发权视为默认获得。

支持两种等价后端：

1. 本地 CLI；
2. 已配置的 MinerU API。

Adapter 不得假定永久本地部署，也不得把 API 地址写死在 Source。

### 9.3 消费接口

v1.2 的主消费接口：

- `*.md`；
- `content_list.json`；
- `layout.pdf`；
- `images/`；
- 必要时使用 `middle.json` 调试。

不得以仍可能变化的 `content_list_v2.json` 作为 v1.2 唯一生产契约。

### 9.4 数据流

```text
原始文件
→ SHA-256与来源记录
→ 隔离解析
→ Derived Package
→ 版面/公式/表格抽查
→ 面向研究问题的内容精选
→ 原页复核
→ Reviewed Evidence Pack
→ Research Dossier
```

### 9.5 精选资料包

每份重要资料至少支持记录：

- 资料身份与来源；
- 当前阅读目的；
- 核心问题；
- 定义、假设、定理、模型和算法；
- 关键公式、图表和实验；
- 局限与冲突证据；
- 与当前研究问题的关系；
- 页码和块坐标；
- 人工核对状态。

解析成功不得自动创建 Knowledge，也不得把 AI 摘要伪装为原文。

### 9.6 失败语义

- 原始资料始终保留；
- 解析失败不创建 Reviewed 结果；
- 部分页失败必须显式报告缺失范围；
- Adapter 不可用时返回可诊断状态，不得修改正式 Source；
- 同一文件哈希、引擎版本和配置重复执行应优先复用缓存。

---

## 10. 文献检索与证据链

### 10.1 文献能力

目标支持：

- 标题、作者、年份、DOI、版本和出版状态；
- 原始论文优先；
- BibTeX / CSL 可用元数据；
- 相关工作比较矩阵；
- 支持证据和反对证据；
- 撤稿、更正、版本更新和失效标记；
- 原文页码或结构化块定位。

### 10.2 Claim–Evidence 原则

每个准备进入正式成果的核心主张必须至少明确：

- 主张内容；
- 适用范围；
- 支持来源；
- 反对或限制材料；
- 证据类型；
- 当前可信度判断；
- 尚未完成的验证。

第一阶段使用 Research Dossier 正文表达，不提前冻结 Claim Schema。

### 10.3 Novelty Matrix

博士级研究项目必须能够比较：

| 维度 | 既有工作 | 当前工作 | 真实新增 |
| --- | --- | --- | --- |
| 问题 |  |  |  |
| 假设 |  |  |  |
| 方法 |  |  |  |
| 数据 |  |  |  |
| 理论 |  |  |  |
| 实验 |  |  |  |
| 结果 |  |  |  |

无法填写“真实新增”时，不得使用“具有创新性”等表述。

---

## 11. 数学建模能力

### 11.1 支持的模型家族

最终能力必须覆盖：

- 符号模型；
- 线性规划；
- 整数规划；
- 非线性规划；
- 凸优化；
- 多目标优化；
- 鲁棒优化；
- 随机优化；
- 网络与图模型；
- ODE；
- PDE；
- 数值模拟；
- 统计模型；
- 参数估计；
- 机器学习比较基线。

“覆盖”指工作台能够为项目选择、配置、运行、验证并记录适当工具，不意味着重新实现所有求解器。

### 11.2 推荐工具边界

| 场景 | 候选工具 |
| --- | --- |
| 符号推导 | SymPy |
| 数值计算 / ODE / 通用优化 | NumPy / SciPy |
| 数据处理 | pandas |
| 凸优化 | CVXPY |
| LP / MIP / NLP | Pyomo + 适当求解器 |
| 网络与路径 | NetworkX |
| 统计模型 | statsmodels |
| 机器学习基线 | scikit-learn |
| PDE / 专用仿真 | 项目级专用环境 |

依赖在 `05_代码/<项目>/` 内锁定，不进入 Foundation 根环境。

### 11.3 标准建模流程

```text
现实问题
→ 决策边界
→ 假设
→ 集合 / 参数 / 变量 / 单位
→ 目标函数与约束
→ 数据与来源
→ 小规模已知答案实例
→ 求解
→ 结构不变量检查
→ 基线比较
→ 敏感性 / 不确定性 / 鲁棒性
→ 结果解释与局限
```

### 11.4 项目结构

```text
05_代码/<项目>/
├── pyproject.toml
├── src/
├── tests/
├── configs/
├── experiments/
├── figures/
└── outputs/
```

Notebook 可以用于探索，但正式实验必须有可重复执行的脚本或命令入口。

### 11.5 模型验证

每个正式模型按适用性检查：

- 单位和维度；
- 变量域；
- 约束可行性；
- 守恒关系；
- 边界和极端情景；
- 手算或已知答案小实例；
- 基准方法；
- 参数敏感性；
- 识别性；
- 求解器状态与最优性含义；
- 数值容差；
- 结果解释范围。

---

## 12. 实验与可复现性

每个正式实验运行必须生成可机读运行清单。该清单是项目级 ephemeral/generated contract，不是新的全局 Frozen Schema。

至少记录：

- Git commit；
- 数据哈希；
- 配置哈希；
- 环境或锁文件哈希；
- Python和关键库版本；
- 求解器与版本；
- 随机种子；
- 执行命令；
- 开始和结束时间；
- 运行状态；
- 标准输出和错误摘要；
- 结果文件与哈希。

正式复现至少包括：

1. 同一环境重复执行；
2. 干净环境执行；
3. 小规模已知结果验证；
4. 随机实验容差说明；
5. 失败和中止运行保留。

失败运行不得被成功运行静默覆盖。

---

## 13. 制图能力

### 13.1 完整范围

目标支持：

- 函数与数学对象图像；
- 几何示意图；
- 网络和路径图；
- 热力图、等高线、三维曲面；
- 误差、收敛和敏感性；
- 情景与组间比较；
- 算法流程和架构图；
- 交互式探索；
- 出版级静态图；
- 数学动画；
- 非精确概念插图。

### 13.2 工具分工

| 场景 | 工具 |
| --- | --- |
| 数值和统计图 | Matplotlib / Seaborn |
| 交互探索 | Plotly |
| 网络与路径 | NetworkX / Graphviz |
| 精确数学图 | TikZ / PGFPlots |
| 工作流和架构 | Mermaid |
| 数学动画 | Manim |
| 非精确信息插图 | AI 图像生成 |

AI 生成图不得用于需要精确坐标、数据、拓扑或数学关系的正式图表。

### 13.3 正式图表契约

每张正式图表必须能够回答：

- 它支持哪个研究主张；
- 数据来自哪次运行；
- 源程序和配置在哪里；
- 如何重新生成；
- 单位、图例和不确定性如何表示；
- 黑白打印和色觉缺陷场景是否可读。

优先输出 PDF / SVG；位图按用途提供足够分辨率。图表进入 `04_LATEX` 或 `08_成果输出` 前必须检查哈希和生成来源。

---

## 14. Lean / Mathlib 形式化

### 14.1 目标结构

```text
06_LEAN形式化/
├── lakefile.toml
├── lean-toolchain
├── lake-manifest.json
├── MathAILab/
│   ├── Problems/
│   ├── Knowledge/
│   ├── Methods/
│   └── Research/
└── Tests/
```

采用一个统一 Lake 工程，固定 Lean 和 Mathlib 依赖，避免每个 Problem 重复建立环境。

### 14.2 完整能力

- 自然语言命题到 Lean 候选；
- Mathlib 定理和定义检索；
- 交互式证明；
- `lake build` 验证；
- Problem / Knowledge / Method / Research 链接；
- 形式陈述与自然语言陈述一致性审查；
- 依赖版本锁定；
- 路径过滤的 Lean CI；
- 版本升级后的证明漂移检测；
- 可复用形式化引理和方法沉淀。

### 14.3 硬性规则

- 正式通过不得包含 `sorry`；
- 不得包含 `admit`；
- 不得用新增虚假 `axiom` 绕过证明；
- `lake build` 必须通过；
- 形式命题必须人工核对；
- Lean 失败不得阻塞普通数学回答和非形式化成果；
- 是否对当前任务启用 Lean 仍受用户明确意图和任务适用性控制。

Lean 能力属于最终必备能力，但不要求每个 Problem 自动形式化。

---

## 15. 严格审稿与反驳

### 15.1 审查角色

目标支持以下受控角色：

- Solver：提出解法、模型或证明；
- Skeptic：寻找反例、失效边界和替代解释；
- Verifier：检查推导、代码、数值和条件；
- Literature Reviewer：核对来源、版本和文献结论；
- Modeling Reviewer：检查假设、识别性、约束和解释；
- Reproducibility Reviewer：检查数据、环境和运行清单；
- Editor：检查结构、表达、引用和成果一致性。

v1 阶段可以由同一 AI 分角色顺序执行；v2.1 才允许在明确审计边界下引入多 Agent 编排。

### 15.2 审稿输出

审稿必须输出：

- 发现的问题；
- 严重程度；
- 支持证据；
- 可执行修改；
- 尚需人工决策的分歧；
- 修改后的复核结论。

审稿角色不得直接批准正式归档。

---

## 16. 检索、RAG与长期记忆

### 16.1 分级路线

```text
Metadata与文件索引
→ 全文检索
→ BM25
→ 向量检索
→ 混合检索
→ 带来源的引用式RAG
```

### 16.2 博士级 RAG 要求

- 回答附可打开来源；
- 来源定位到页码或结构化块；
- 区分原文、解析文本、AI总结和推断；
- 同时检索支持与反对证据；
- 检测来源版本更新和失效；
- 不把未审核 Derived 内容当正式证据；
- 有独立评测集和检索质量报告；
- 检索失败时明确承认，而不是补写虚构内容。

RAG 是最终功能，不在 Foundation Closure 阶段实现。进入 v2.0 前必须先证明普通索引和全文检索无法满足真实规模需求。

---

## 17. 多角色与多 Agent

多 Agent 是最终能力之一，但不得建立无边界自治框架。

### 17.1 进入条件

- 单角色顺序审查已稳定；
- 各角色输入输出已明确；
- 冲突和失败语义已验证；
- 有真实任务证明并行或隔离角色具有收益；
- 人工门禁和审计日志已存在。

### 17.2 安全边界

- Agent 输出默认为 Candidate；
- 不得直接修改 Frozen Source；
- 不得自动晋升 Knowledge；
- 不得自动批准 Claim；
- 不得隐藏角色之间的分歧；
- 正式成果仍需人工审核。

---

## 18. 运行状态与错误处理

研究能力运行结果应保持确定性分层报告。可复用现有 `LayerStatus` 等语义时优先复用，但不得强行把不同领域状态塞入 Normal Operation `OperationResult`。

每次能力调用至少区分：

- 是否请求；
- 是否可用；
- 是否执行；
- 候选结果是否生成；
- 质量检查是否通过；
- 是否经过人工审核；
- 是否发布正式成果。

通用失败原则：

1. Candidate 失败不得覆盖 Reviewed / Formal；
2. 外部服务不可用时不得伪装为成功；
3. 部分成功必须报告缺失范围；
4. Artifact 失败不回滚已验证数学结果；
5. 基础设施失败不扣留用户当前数学答案；
6. 可重试任务必须保持幂等或使用独立运行目录；
7. 错误信息必须提供下一步可执行建议。

---

## 19. 测试与持续验证

### 19.1 Core 保持轻量

Core CI 不安装 MinerU 模型、建模求解器全集、Lean 或向量数据库。适配器单元测试使用 fake executable、fixture 或 mock service。

### 19.2 分离验证配置

目标验证配置：

| Profile | 内容 |
| --- | --- |
| `core` | 现有 Foundation Validator、Workspace、pytest |
| `latex-smoke` | 现有 P9 / XeLaTeX 检查 |
| `document-smoke` | 文档适配器契约和小型公开fixture |
| `modeling-smoke` | 小规模已知答案模型 |
| `figure-smoke` | 图表可再生和基本检查 |
| `lean-smoke` | Lake工程和选定真实命题 |
| `retrieval-eval` | 检索和引用质量评测 |
| `research-acceptance` | 端到端研究项目验收 |

重型 profile 使用路径过滤或显式触发，不得使普通 Core 失去快速诊断能力。

### 19.3 测试层次

每项能力应按需具备：

- 单元测试；
- 接口契约测试；
- 失败注入测试；
- 临时目录集成测试；
- 真实任务 Pilot；
- 人工质量抽检；
- 跨平台检查；
- 端到端 Acceptance。

测试不得伪造用户 Attempt 或污染 production Source。

---

## 20. 版本路线

### v1.0.1 — Foundation Portability Closure

能力：

- 修复 `C:\MATH-AI-LAB` 绝对路径；
- Windows / Linux 路径一致；
- 远程 Core 绿色；
- LaTeX Smoke 绿色；
- 项目状态描述一致。

验收：

```text
pytest                >= 618 collected, 0 failed
verification core     PASS
latex-smoke           PASS
workspace             CURRENT
```

### v1.1 — Research Project & Dossier

能力：

- `07_项目/` 真实落地；
- Research Dossier；
- 假设、主张、证据、失败、决策和贡献记录；
- 与 P/K/M、代码和成果链接。

验收：至少一个真实长期研究项目形成完整档案，且不修改 Frozen Schema。

### v1.2 — Document Intelligence

能力：

- MinerU CLI / API 适配；
- PDF与多格式解析；
- 文件哈希与缓存；
- Markdown / JSON / 图像处理；
- 页码和边界框；
- 内容精选与人工复核。

验收：原生数学PDF、扫描资料、公式/表格密集资料均通过真实抽检。

### v1.3 — Literature Evidence

能力：

- DOI / BibTeX / 版本记录；
- 文献比较矩阵；
- Claim–Evidence候选链；
- 支持与反对证据；
- Novelty Matrix；
- 引用一致性检查。

验收：一个真实项目的所有核心文献性主张可回到来源。

### v1.4 — Modeling & Reproducible Experiments

能力：

- 项目独立Python环境；
- 多模型家族接入边界；
- Run Manifest；
- 小规模已知答案验证；
- 基线、敏感性、不确定性与负结果。

验收：至少一个优化模型和一个不同模型家族完成可复现 Pilot。

### v1.5 — Figure & Visualization

能力：

- 数值、网络、精确数学和交互图；
- 出版级检查；
- 图表来源和哈希；
- 与P9连接；
- 数学动画和非精确解释图边界。

验收：静态数据图、网络图、精确数学图均可由干净环境重新生成。

### v1.6 — Lean Formalization

能力：

- 统一Lake工程；
- Mathlib依赖；
- Problem/Knowledge/Research链接；
- 无`sorry`正式证明；
- Lean CI；
- 陈述一致性审核。

验收：真实命题通过编译、语义复核和CI。

### v1.7 — Critical Review

能力：

- Solver / Skeptic / Verifier等角色；
- 反例攻击；
- 模型与文献审查；
- 修改和复核闭环。

验收：一个研究成果经过完整审稿记录并完成修改闭环。

### v1.8 — Research Writing & Artifact Consistency

能力：

- 证据驱动论文写作；
- 图表、表格、代码、数据与正文一致性；
- 补充材料；
- 审稿回复；
- P9正式发布。

验收：一个研究项目生成可复查的论文级成果包。

### v2.0 — Hybrid Retrieval & Cited RAG

能力：全文、BM25、向量和混合检索；引用式回答；版本与失效检测；检索评测。

验收：真实研究资料集上的检索和引用质量达到预先定义的评测标准，且不存在未引用主张冒充来源内容。

### v2.1 — Controlled Multi-Agent Research

能力：受控角色编排、并行研究、分歧保留、人工门禁和审计。

验收：相对于单角色基线，在至少一个真实复杂任务上证明质量或效率收益。

### v2.2 — Doctoral Research Workbench Closure

能力：跨项目复用、长期研究记忆、能力成长证据和端到端研究闭环。

验收：第二个不同领域真实项目复用成功，且未破坏 Foundation 核心语义。

---

## 21. 实施分解

本设计是 umbrella architecture，范围过大，不允许用一个实现计划一次完成。必须拆成下列独立子项目，每个子项目执行：

```text
专项设计
→ 用户审核
→ 实施计划
→ TDD实现
→ 专项验证
→ 真实Pilot
→ 人工验收
```

子项目顺序：

1. v1.0.1 Foundation Portability Closure；
2. v1.1 Research Project & Dossier；
3. v1.2 Document Intelligence；
4. v1.3 Literature Evidence；
5. v1.4 Modeling & Reproducible Experiments；
6. v1.5 Figure & Visualization；
7. v1.6 Lean Formalization；
8. v1.7 Critical Review；
9. v1.8 Research Writing；
10. v2.0 Retrieval & RAG；
11. v2.1 Multi-Agent；
12. v2.2 Closure。

批准本设计后，下一份实施计划只覆盖 v1.0.1，不得夹带 MinerU、建模、Lean 或 RAG 实现。

---

## 22. 权限与人工门禁

自动化允许：

- 写入隔离缓存；
- 生成 Derived 候选；
- 执行只读检查；
- 运行临时实验；
- 生成审查报告；
- 在明确授权范围内创建项目级代码和配置。

仍需明确授权或现有规则规定的门禁：

- 正式 Knowledge authoring；
- Frozen Schema修改；
- 正式归档；
- Claim批准；
- 论文主张确认；
- 正式PDF发布；
- 大规模资料导入；
- RAG数据库正式建设；
- 多Agent直接修改Source。

当前显式用户要求“功能不能减少，只能加强”意味着最终目标能力不得无说明删除，但不构成对所有版本立即实施、修改Schema或发布成果的授权。

---

## 23. 主要风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 重型依赖破坏核心环境 | 独立环境 / 服务 / 显式适配器 |
| OCR或公式解析错误 | 原页定位、抽检和Reviewed门禁 |
| 资料大量堆积但无研究产出 | Research Dossier与Claim驱动精选 |
| 模型能运行但含义错误 | 单位、假设、已知实例、基线和审稿 |
| 图表漂亮但不支持主张 | Figure–Claim–Run关联 |
| Lean证明了错误形式命题 | 自然语言与形式陈述人工对照 |
| RAG产生无来源答案 | 引用强制、反对证据、检索评测 |
| 多Agent扩大错误 | 角色隔离、Candidate默认、人工门禁 |
| 新Schema泛滥 | Markdown Pilot先行，真实查询需求后候选化 |
| 基础设施建设压过数学研究 | 每个版本以真实研究Pilot验收 |
| 跨平台状态漂移 | v1.0.1先关闭路径和CI问题 |

---

## 24. 被拒绝的替代方案

### 24.1 单一大环境

拒绝原因：MinerU、求解器、Lean、绘图和RAG依赖复杂，容易破坏现有轻量Core和跨平台CI。

### 24.2 直接复制MinerU源码

拒绝原因：增加维护和许可责任，失去上游升级边界。采用固定版本的外部CLI/API适配更合适。

### 24.3 立即冻结Research/Claim/Source Schema

拒绝原因：缺少足够真实对象和查询证据，容易制造重复事实和长期迁移负担。

### 24.4 取消Lean、RAG或多Agent

拒绝原因：违反已确认的“功能不减少，只能加强”目标。正确处理方式是保留为完整目标能力并设置成熟度和进入门槛。

### 24.5 每次任务强制调用所有能力

拒绝原因：功能存在不等于全量激活。强制调用会增加成本、延迟和失败面，且不提高每类数学任务的质量。

---

## 25. 总体验收定义

MATH-AI-LAB 达到博士级研究工作台，不以“所有工具已安装”判定，而以以下端到端证据判定：

1. 真实研究问题被清晰界定；
2. 关键文献可解析、精选并回到原页；
3. 核心主张同时记录支持、限制和反对证据；
4. 模型、数据、环境和实验可复现；
5. 图表由正式运行生成并与正文一致；
6. 适合的命题可由Lean验证且语义一致；
7. 失败路线和修改决策被保存；
8. 成果经严格审稿和反例攻击；
9. LaTeX、PDF、代码、数据、图表和补充材料形成一致成果包；
10. 第二个不同领域项目能够复用能力；
11. Foundation Core仍保持稳定、可验证、可维护；
12. 功能全集未被削减，且各模块可独立升级和替换。

---

## 26. 主要外部参考

- MATH-AI-LAB：<https://github.com/yangxingchen123/MATH-AI-LAB>
- MinerU 中文说明：<https://github.com/opendatalab/MinerU/blob/master/README_zh-CN.md>
- MinerU 输出文件：<https://opendatalab.github.io/MinerU/zh/reference/output_files/>
- MinerU 许可证：<https://github.com/opendatalab/MinerU/blob/master/LICENSE.md>
- Mathlib：<https://github.com/leanprover-community/mathlib4>
- Mathlib 文档：<https://leanprover-community.github.io/mathlib4_docs/>

外部项目的当前版本和接口可能变化。正式实施必须锁定版本并保存兼容性验证结果，不得仅凭本文链接推断未来行为。

---

## 27. 下一步

本文经仓库级人工审核后，下一步仅执行：

> 为 v1.0.1 Foundation Portability Closure 编写详细实施计划。

在该计划获得批准前，不实施代码修复，不创建MinerU、建模、Lean、RAG或多Agent生产模块。
