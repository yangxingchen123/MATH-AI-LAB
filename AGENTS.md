# MATH-AI-LAB Agent 执行规则

本文件只保存 Agent 每次进入项目时需要快速遵守的高频执行规则。

---

## 1. Authority 与冲突处理

| 文件 | 职责 |
|------|------|
| `项目规则.md` | 长期稳定制度 / 完整治理规则 |
| `元数据规范.md` | Frozen Schema technical authority |
| `09_长期记忆/项目进度.md` | 动态 Phase / capability / next-step |
| 各模板 | 具体文档结构 |
| 设计历史文档（如 `学习证据架构.md`、`Method与ErrorMode架构.md`、`派生学习状态架构.md`） | rationale / Pilot history；**不得**覆盖 Frozen Schema |

**冲突处理：**

* `AGENTS.md` 与 `项目规则.md` 冲突 → 以 `项目规则.md` 为准。
* 任一下游（`项目规则.md`、`AGENTS.md`、模板、工具）与 **Frozen Schema**（`元数据规范.md`）冲突 → **修下游**，不得反向修改 Frozen Schema。

**动态项目状态**（Phase、capability、pytest 基线等）查看 `09_长期记忆/项目进度.md`，不在本文件维护。

---

## 2. 总体执行原则

本项目用于长期数学学习、研究、验证、知识整理与正式成果输出。

执行任务时遵循：

`简单` → `可运行` → `稳定` → `可验证` → `再自动化`

默认：

* 只读取完成当前任务需要的最少上下文；
* 不无意义扫描整个项目；
* 不重复读取已经明确的信息；
* 优先最小必要修改；
* 不因局部任务重构整个项目；
* 当前任务完成后停止；
* 不自行扩展下一任务。

---

## 3. 数学任务高频规则

重要数学问题优先按照：

`问题识别` → `为什么想到` → `数学直觉` → `严格推导` → `条件检查` → `验证` → `人工审核`

推进。

重点解释：

> 为什么能够想到这种方法？

不得用「显然、易得、不难发现、类似可得」等表述跳过具有学习价值的关键步骤。

重要内容主动检查（按需展开，无法严格确认时明确指出，不得猜测）：

* 定义域 / 值域；
* 定理使用条件；
* 连续 / 可微 / 可积 / 收敛；
* 凸性 / 可逆性；
* 边界 / 参数范围；
* 极值存在与达到、唯一性；
* `sup/max`、`inf/min` 不混淆；
* 必要 / 充分条件。

**资料优先级**（按需读取，用户指定资料优先）：

1. 用户指定教材、论文或可靠原始资料；
2. `03_参考资料/`；
3. 已审核的 `01_知识库/`；
4. 已审核的 `02_题目库/已解决/`；
5. Agent 自身推理。

不得编造数学史、人物、定理归属、原始文献或具体引用；无可靠依据时标记 `待查证`。

学习状态导航按需见 `09_长期记忆/个人学习档案.md`、`当前学习状态.md`、`数学知识地图.md`、`已解决问题索引.md`。

### 数学交互（默认 AUTO）

* **默认 AUTO**：「怎么做」「不会」「解答」「证明」「解释」「为什么」→ 直接完整回答（one-turn completeness）。
* 非机械题须解释**为什么想到**；RESEARCH 主动扩展；REVIEW 优先批改用户原解。
* **STUDY** 仅用户显式 opt-in（「我想自己做」「先别给答案」「只给提示」）；才启用分级提示 / 独立 Attempt 保护。
* 不得默认 Level 1/2/3、不得默认「先想想再回答」；用户说「直接告诉我」→ 立即 AUTO。
* **AI 解答 ≠ User Attempt**；AI 解题默认不创建 Attempt；Attempt 只记录用户真实 solving/reasoning。
* 不得为保护 Evidence 拒绝或延迟用户正常请求的完整答案。完整 authority：`项目规则.md` 四点五。

---

## 4. Source / Generated / Workspace

### 4.1 事实源优先级

涉及项目状态、文件状态、题目状态或成果状态时：

* **实际 Source / filesystem 优先**于长期记忆汇总；
* `01_知识库/` 实际内容 → 正式知识归档状态；
* `02_题目库/` 实际文件与 YAML → 正式 Problem；目录 `未解决/` / `研究中/` / `已解决/` **仅**工作流组织，**不等于** YAML `status`；
* `08_成果输出/` 实际内容 → 成果是否已发布；
* 汇总信息（`项目进度.md`、`已解决问题索引.md` 等）与仓库冲突 → 以仓库为准并修正汇总。

普通数学任务不因此扫描整个项目；仅状态判断或工作台维护任务才检查相关目录。

### 4.2 Generated 数据

`09_长期记忆/自动索引/**` = **GENERATED**，**不得人工编辑**。

修正路径：改 source 或 derivation policy → validate → `sync`（或 `rebuild`）。

Derived learning-state views 同理；设计 authority 见 `派生学习状态架构.md`。

### 4.3 高频根目录

| 目录 | 职责 |
|------|------|
| `01_知识库/` | 审核后的正式知识（概念 / 定理 / 方法本身） |
| `02_题目库/` | 具体问题如何被研究和解决 |
| `04_LATEX/` | LaTeX 模板与工程 source |
| `08_成果输出/` | 正式成果（含 `PDF/`） |
| `09_长期记忆/自动索引/` | Generated 导航与统计 |

完整目录职责见 `项目规则.md`。

研究稿不得直接复制成正式知识条目。正式 Problem 身份以 YAML `id` 为准。

### 4.4 Workspace 命令

```text
python -m tools.workspace_indexer check
python -m tools.workspace_indexer sync
python -m tools.workspace_check check
```

| 组件 | 职责 |
|------|------|
| Validator / Checker | read-only validation |
| Indexer | derived write only |
| Workflow / Creator | authorized source mutation |

---

## 5. Structured Object 高频协议

处理 Knowledge / Problem / Attempt / Method / Error Mode 等结构化对象前，先确认 contract 成熟度（draft / candidate / frozen）。

**Frozen 对象**：只按 `元数据规范.md` 执行；不得为当前任务方便新增或改字段、lifecycle 或关系语义。

**核心分离：**

`Schema` ≠ `Template` ≠ `Validator` ≠ `Indexer` ≠ `Workflow`

未 Frozen 的对象类型（如 Error Mode）**不得**当作 Frozen production Schema 或创建正式对象。

设计历史文档不得覆盖 Frozen Schema。Frozen 章节索引：K §6 · P §7 · A §8 · M §9（`元数据规范.md`）。

### Attempt 保护

1. 只能来自**用户**真实 solving / reasoning Evidence（AI 代为生成解法 **不是** Attempt）。
2. **禁止**为测试、统计、coverage、demo 而伪造 Attempt。
3. one Attempt → one evaluation target（`problem` + optional `part`）。
4. Recording ≠ Assessment；不得无依据猜 `outcome`。
5. Reattempt → new A ID；Correction → same A ID + `corrections` append。
6. Attempt 是 historical Evidence，**无** static `status` lifecycle。
7. **STUDY 模式**才保护 independent Attempt；AUTO 下不得 withhold 完整答案。
8. **Logical Attempt ≠ physical file：** production storage 按 Problem 聚合为 `Pxxxx.md` Ledger；新 Attempt append 到已有 Ledger，**不**创建 `Axxxxxx.md`。

### Normal Operation（高频）

* 临时提问（无 P ID）→ 只回答，**不** persistence / finalize。
* 正式 Problem 直接解题（如「直接解答 P0002(a)」）→ canonical Solution upsert + source finalize（若 WRITTEN）+ **`reconcile_problem`（NO_OP 也进入）**。
* AI Solution **≠** User Attempt；AUTO 默认 **不** 创建 Attempt。
* User Attempt append 到 `Pxxxx.md`；1 STUDY episode = 1 Attempt；参考答案 **不** 记 Attempt。
* Source candidate validate 后再 atomic replace；失败 official 不变。
* Workspace **check-first**；STALE 才 sync；成功 compact report。
* **正式 Problem：** `AUTO_CLOSE=ON` · `AUTO_ARTIFACT=ON`：canonical COMPLETE + self-check + validator PASS → `研究中`→`已解决` → 物化 LaTeX → 真实 P9 → canonical PDF。用户 opt-out（「先别归档 / 不要 PDF」）优先。
* 临时提问：**不** persist / **不** reconcile / **不** PDF。
* **Production operations（Layer 2）：** `persist_canonical_solution_op` · `record_user_attempt_op` · `study_to_auto_op` · `reconcile_problem_op` · `publish_pdf_op`。NO_OP 跳过 source finalizer，**仍** reconcile。
* Maintenance：`python -m tools.normal_operation check-closure --problem Pxxxx` / `--all`；`reconcile --problem Pxxxx`。

### Problem 保护

* Problem YAML `status` ≠ workflow directory ≠ Attempt outcome。
* 正式身份以 YAML `id` 为准。

**Operational workflow**（filesystem directory，不得新增重复 YAML 字段）：

| 目录 | 含义 |
|------|------|
| `未解决/` | 已登记，尚未 substantive mathematical activity |
| `研究中/` | 已发生实质性 solving / reasoning / research |
| `已解决/` | 研究完成 + 人工审核 + 明确归档授权 |

* `未解决/` → `研究中/`：仅当已发生实质性数学研究活动时可自动移动（读题面、改格式、询问题意**不**触发）；只改目录位置，不改 YAML `status` / identity / knowledge mapping / Attempt outcome。
* `研究中/` → `已解决/`：**正式 Problem 默认 AUTO_CLOSE**：canonical coverage COMPLETE + AI self-check + Problem Validator PASS 且无用户 opt-out 时自动移动。不再要求再说「审核通过，请归档」。
* `已解决/` → `研究中/`：不得自动；仅用户明确要求时。

### Validator 命令

Problem：

```text
python -m tools.problem_validator check-file "<PATH>"
python -m tools.problem_validator check
```

Attempt：

```text
python -m tools.attempt_validator check-file "<PATH>"
python -m tools.attempt_validator check
```

Method（source root：`12_方法库/`）：

```text
python -m tools.method_validator check-file "<PATH>"
python -m tools.method_validator check
```

**修改后流程：**

* Method / Attempt：Validator PASS → `workspace_indexer sync` → `workspace_check check`。
* Indexer **只消费** Validated Registry；不得自行 parse / validate / 修复 raw source。
* Validator ERROR 时：不得继续索引发布、Workflow promotion、derived state 更新或下游正式生成。
* `check-file` 非孤立单文件检查；需要 uniqueness / registry / relation 时须全库 validation。
* `tools.problem_candidate_gate` 已 DEPRECATED，不得作 Problem Schema v1 正式 authority。

**Authoring 要点**（非 Schema 表）：`02_题目库/题目模板.md` 仅作 scaffold，不得解析模板推导 Schema；新建 Problem 默认 `status: draft`；knowledge mapping 未完成则省略 `knowledge`；仅真实 multipart 才写 `parts`；数学正文放 Markdown，不堆 YAML 字段。

没有明确授权时，不得自动做 Schema mutation、ID allocation、lifecycle promotion、formal archive 或 Knowledge creation。

---

## 6. 人工审核与 Source Mutation 权限

标准流程：`AI研究` → `AI自检` → `人工审核` → `正式归档`

**四个高频授权语义：**

| 用户表述 | 含义 |
|----------|------|
| `审核通过` | 仅内容审核通过 |
| `审核通过，请归档` | 允许执行当前研究任务的标准归档 |
| `开始知识沉淀` | 允许正式 Knowledge authoring |
| `生成 LaTeX 讲义` 或等价明确要求 | 允许进入正式 LaTeX 输出 |

说「审核通过」时**不得**自动：移动文件、正式归档、创建知识条目、更新长期记忆、生成 LaTeX / PDF。

**未经授权不得：**

* 正式归档、Knowledge creation；
* 大规模修改长期记忆；
* 删除原始资料；
* 覆盖无关正式成果；
* 修改与当前任务无关的 Source；
* 大范围重构目录。

---

## 7. LaTeX 高频协议

LaTeX 模板决定「长什么样」；Knowledge / reviewed material 决定「写什么」。详细流程、内容组织、图像、编译检查、成果覆盖见 `项目规则.md` §14。

### 模板与 entrypoint

**默认母版：** `04_LATEX/模板/数学讲义模板_v1/`（ElegantBook v4.7 vendor + XeLaTeX）

* 模板入口：`main.tex` — **仅**属于模板母版。
* 创建具体讲义：以 `main.tex` 为 scaffold，将入口 **重命名**为 `<主题目录名>.tex`。
* **不要**把 `elegantbook.cls` 或 `vendor/` 复制进具体工程。
* 编译依赖由 P9 注入 pinned vendor：`vendor/ElegantBook-v4.7/elegantbook.cls`。
* **禁止**在具体工程继续使用 `main.tex` 作为 canonical entrypoint。

**示例：**

```text
04_LATEX/专题讲义/数学变换/勒让德变换/勒让德变换.tex
```

不得直接修改模板母版；不为单个主题重新设计无必要的新 LaTeX 风格。

### 正式编译与发布

```text
python -m tools.latex_build check "<04_LATEX/project>"
python -m tools.latex_build build "<04_LATEX/project>"
```

* `check`：只编译检查，**不**发布到 `08_成果输出/`。
* `build`：inspection PASS 后 atomic publish。
* 正式成果：`08_成果输出/PDF/资料类型/数学领域/<主题>.pdf`（basename 与 topic entrypoint 一致）。
* compiler **不得**直接写入 formal root；failed build **不得**破坏已有 formal PDF。
* build 已成功时，**不要**手工复制 PDF。

Source project 主要保存 `<主题>.tex`、`.cls` / `.sty` / `.bib`、`figures/` 等；build 中间文件优先在 isolated workspace。

---

## 8. Production Code / TDD / 完成规则

修改 Validator / Indexer / Workflow / Creator 等**生产代码**时：

`RED` → `GREEN` → `REFACTOR`（先写失败测试，再最小实现）

内部模块优先调用 Python public API 并复用 `ValidationResult`；不要用 subprocess 调 CLI 做模块通信。

**Python**：可用于数值验证、实验、绘图；代码放 `05_代码/`。**数值结果不能代替严格证明。**

**Lean**：非默认；仅任务适合且用户明确要求时使用。

完成用户当前明确要求后停止。除非用户当前明确授权，**不自动**：

* 进入下一 Phase；
* 创建下一 Knowledge / 其他 LaTeX 讲义；
* 更新全部长期记忆；
* 引入 RAG、Multi-Agent、向量数据库、Lean、CI；
* 重构整个项目。

核心原则：

> 少量、高质量、可验证的操作，优先于大量碎片化操作。
