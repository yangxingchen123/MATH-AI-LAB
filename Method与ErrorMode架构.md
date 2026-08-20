# Method 与 Error Mode 架构

**副标题：** Phase 3D Design Entry — Method / Error Mode Boundary & Semantic Foundation  
**阶段：** Phase 3D-4E — Error Mode Minimal Candidate Schema（**DONE**）  
**最后更新：** 2026-08-20

本文件是 **Phase 3D Method / Error Mode** 的单一设计入口（3D-0 起）。  
**Method Schema v1 正式 technical authority：** `元数据规范.md` §9（**FROZEN**）。  
**Error Mode Schema v1：** **Minimal Candidate**（**CANDIDATE · NOT FROZEN**；authority 见本文件 Phase 3D-4E）。  
K / P / A 仍以 `元数据规范.md` 为准；Attempt 设计历史见 `学习证据架构.md`。

> **3D-4E DONE** → Error Mode Minimal Candidate Schema **CLOSED** → **3D-5E Real Error Mode Pilot** = **WAITING FOR REAL ERROR EVIDENCE**（不得自动开始；不得为对称性制造 Evidence）

---

## 1. Working Definitions

### 1.1 Method（工作定义）

**Method** 是一种具有 **稳定数学意图** 与 **稳定操作结构**、可以 **跨一个或多个 Problem** 重复使用的 **solving / reasoning procedure**（处理程序）。

它回答：**“面对某类数学情境，通常按什么可复用步骤/策略去推进？”**

**什么算 Method（方向性，非字段规范）：**

* 可跨题复用的推理程序，而非一次性步骤链；
* 有 identifiable intent（例如：反解梯度再代入、张量积特征基构造、换元后同步改积分限）；
* 有 stable operation structure（步骤角色稳定，换题后结构仍成立）。

**什么不算 Method：**

| 不是 Method | 原因 |
| --- | --- |
| **Knowledge** | 定理/定义/概念本身（如“$B$ 与 $B^T$ 特征值相同”）是知识，不是 procedure |
| **Problem solution** | 某题完整解答是 Problem 正文或归档内容，不是可复用 Method 对象 |
| **Attempt step** | 单次 Attempt 内的局部操作是 historical evidence，默认留在 Attempt body |
| **Recommendation** | “下一题练什么”“建议复习 X”属于 Derived / Action 层 |
| **单题临时操作** | 只在该题、该次推理中成立、无法抽象为跨题程序的内容 |
| **Pedagogical narrative** | 某次研究如何组织章节（如 P0001 的 sup→经典路径叙述）是写作/研究过程，不是 Method |

### 1.2 Error Mode（工作定义）

**Error Mode** 是数学 solving / reasoning 中，具有 **稳定错误机制** 与 **可重复识别特征**、能够 **跨一个或多个 Attempt / Problem 再次出现** 的 **failure pattern**（失败模式）。

它回答：**“哪类错误机制会反复出现，且值得长期诊断与规避？”**

**什么算 Error Mode：**

* 机制稳定（不是偶然笔误）；
* 可重复识别（有典型表现模式）；
* 跨题或跨 Attempt 可再现；
* 对长期学习诊断有价值。

**什么不算 Error Mode：**

| 不是 Error Mode | 原因 |
| --- | --- |
| **`incorrect` Attempt** | outcome 是 Evidence 标签，不自动升格为 Error Mode |
| **一次算错** | 单次计算错误若无稳定机制，留在 Attempt body |
| **一次 typo / 符号写反** | 孤立失误，无长期诊断价值 |
| **`partial` / `unsolved`** | 未完成 ≠ 错误机制；是 progress/outcome 语义 |
| **Problem 题面缺陷** | 如 P0002 domain 未写明，属于 Content Review，不是 learner Error Mode |
| **Placeholder 汇总行** | `09_长期记忆/错题与错误模式.md` 中 EM001–EM005 若机制/根因仍为「待补充」，尚非正式 Error Mode 对象 |

### 1.3 Error Mode 内部概念层级

| 层级 | 含义 | 与 Object identity 关系 |
| --- | --- | --- |
| **Error manifestation** | 某次 Attempt 上的具体错误表现（写错式子、漏项、停在某步） | **不**作为 Error Mode 身份核心 |
| **Error mechanism** | 稳定的失败机制（如混淆充分/必要、忽略定义域变化） | **推荐**作为 Error Mode identity 核心 |
| **Correction / prevention** | 如何修正或预防 | 可写在 Error Mode body；**不是** identity；属于使用/教学说明 |

**3D-0 决策：** Error Mode object identity **优先围绕 Error mechanism / failure pattern**，而非单次 manifestation。

---

## 2. Promotion Thresholds

### 2.1 Method Promotion Threshold

一段内容 **只有同时** 满足下列四项，才 **值得晋升** 为 **Method Object**：

1. **可复用性（Reusability）** — 3D-0 曾简写为「≥2 个不同 Problem 类」；**3D-1 修正：** 可复用性 **不是** 仅等于已观察次数。须同时满足 Route A 或 Route B（见 **§ Phase 3D-1 · 5. Promotion Threshold**）。**one observed Problem ≠ automatic rejection**。
2. **稳定数学意图** — 程序要达成的数学目标清晰且稳定；
3. **稳定操作结构（Procedure skeleton）** — 步骤/角色可抽象描述，换题后结构仍成立；
4. **不依赖偶然细节** — 不绑定某题特定数值、特定 part 表述或一次性构造。

**否则继续留在：** Problem body · Attempt body · Knowledge（若本质是定理/定义）

> **3D-0 历史 rationale 保留：** 上述「≥2 题」表述反映早期边界直觉；3D-1 将其 refine 为 Observed Reuse **或** Intrinsic Reusability，避免误读为绝对计数门槛。

### 2.2 Error Mode Promotion Threshold

**3D-2 修正：** 「出现次数」**不是** Error Mode identity。晋升判断拆为两层（详见 **Phase 3D-2 · 6. Promotion Threshold + Evidence Policy**）。

#### A. Semantic Qualification（语义资格）

须 **同时** 满足：

1. **Stable Failure Mechanism** — 可命名的 reasoning failure mechanism，而非「这次错了」；
2. **Stable Diagnostic Pattern** — 可重复识别的 diagnostic signature / manifestation family；
3. **Independence from accidental details of one Attempt** — 能脱离单次 Attempt 偶然细节定义；
4. **Long-term Diagnostic Value** — 值得长期诊断与规避。

#### B. Promotion Evidence（晋升证据；≠ identity）

| Route | 条件 |
| --- | --- |
| **Route A — Observed Recurrence** | 已在多个真实 Attempt / Problem 中观察到 **同一 failure mechanism** |
| **Route B — Mechanism-Generalizable Evidence** | 当前可能只有 **一条** 真实错误 Evidence，但 mechanism 已能脱离该题：清楚定义 trigger/context · diagnostic signature · reasoning failure；合理预期未来可再次识别 |

**one observed failure → automatic rejection：NO**

**但：** 无真实错误 Evidence、仅有抽象猜测或占位描述 → **不得** 因「听起来合理」自动成为 production Error Mode（见 3D-2 Evidence Policy）。

**Semantic Qualification ≠ Creation Authorization**

> **3D-0 历史 rationale 保留：** 原「≥2 次独立证据，或 1 次 + 清晰机制」易被误读为 identity 由计数决定；3D-2 将其 refine 为 Semantic Qualification **与** Promotion Evidence 两层。

**否则：** 只保留在 Attempt historical body，或 `09_长期记忆/错题与错误模式.md` 等非正式汇总（**不是**正式 EM object）。

### 2.3 禁止 Derived Leakage（Source 字段）

下列内容 **未来不得** 成为 Method / Error Mode 的 **source YAML 字段**（属于 Phase 3E Derived Learning State）：

`mastery` · `proficiency` · `success_rate` · `frequency` · `last_used` · `last_seen` · `weakness` · `priority` · `recommendation` · `confidence score` · `review_priority` · `mistake_count` · `recurrence_rate`

---

## 3. Object Boundary Table

| 对象 | 层级 | 回答的问题 | 权威来源（目标态） |
| --- | --- | --- | --- |
| **Knowledge** | Static | 概念/定理/变换 **是什么**、为何成立 | `01_知识库/` YAML + body |
| **Problem** | Static | 某道具体题/研究任务 **题面与归档** | `02_题目库/` YAML + body |
| **Method** | Static | 可复用 **处理程序** 是什么 | `12_方法库/` YAML + body |
| **Error Mode** | Static | 可复用 **失败模式机制** 是什么 | 推荐 future root：`13_错误模式库/`（**未创建**；见 3D-4E） |
| **Attempt** | Evidence | 某次真实 solving/reasoning **发生了什么** | `11_学习证据/尝试记录/` |

**Static objects：** Knowledge · Problem · Method · Error Mode  
**Evidence：** Attempt  
**Derived（Phase 3E，禁止写入上述 Source YAML）：** mastery · weakness · frequency · success rate · method proficiency · review priority · recommendation · error recurrence statistics · personal difficulty · …

**五类边界一句话：**

* **Knowledge** — 稳定数学知识对象  
* **Problem** — 稳定题目/任务对象  
* **Method** — 稳定、可复用的数学 **处理程序**  
* **Error Mode** — 稳定、可重复识别的 **失败模式机制**  
* **Attempt** — 一次真实历史的 solving/reasoning **Evidence**

---

## 4. Relationship Boundary

本轮 **不** 决定 YAML relation 字段；只标 **LIKELY / UNLIKELY / DEFER** 及理由。  
**不得** 因 3D-0 结论反向修改 Frozen K / P / A Schema。

| 关系 | 判定 | 理由 |
| --- | --- | --- |
| **Knowledge ↔ Method** | **LIKELY** | Method 常依赖定理/定义（Knowledge）；Knowledge 条目可说明相关方法，但 procedure 身份应在 Method |
| **Knowledge ↔ Error Mode** | **LIKELY** | 错误机制常关联概念误解（Knowledge 缺口）；但 Error Mode 是 failure pattern，不是 Knowledge 本身 |
| **Problem ↔ Method** | **LIKELY** | Problem 可能适用/推荐某 Method；属静态关联，**不是** Attempt 实际用法（Attempt Evidence 层再论） |
| **Problem ↔ Error Mode** | **UNLIKELY**（作为 Problem YAML 权威字段） | 题面对象不宜承载“易错模式列表”为权威事实；更易来自 Attempt 聚合或显式 EM 链接（3D-3+ 再定） |
| **Attempt ↔ Method** | **DEFER** | Attempt v1 **无** `method` 字段（Frozen）；实际用法在 body；未来是否 link Method ID → 3D-1+ / 3E，**不得** retroactive 改 Attempt Schema |
| **Attempt ↔ Error Mode** | **DEFER** | 同上；错误表现留在 Attempt body；正式 EM occurrence 链接 → 3D-2+ / 3E |

**3D-0 明确禁止：** 为当前便利在 Attempt YAML 增加 `method` / `error_mode` 字段。

---

## 5. Real Repository Examples

### 5.1 Method 候选（boundary analysis only；**未**创建 M ID）

| # | 来源 | 摘要 | 判定 | 理由 |
| --- | --- | --- | --- | --- |
| M-ex-1 | A000001 / P0002(b) | 用 $A$ 与 $B^T$ 的特征基构造 $X_{ij}=u_i v_j^T$，再算 $\varphi(X_{ij})$ | **KEEP IN BODY** | 结构仍与 $\varphi(X)=AX-XB$ 强绑定；仓库仅 1 题证据；可复用性未验证 |
| M-ex-2 | A000002 / P0002(a) | 从 $B^T v=\lambda v$ 得 $v^T B=\lambda v^T$ | **KEEP IN BODY** | 本质是 **Knowledge**（转置特征值关系）的应用步骤，不是独立 procedure |
| M-ex-3 | P0001 / K0001 | 经典 Legendre：可逆导数/梯度映射 → 反解 $x(p)$ → 代入 $px-f(x)$ | **PROMOTE CANDIDATE** | 意图稳定、结构稳定、可跨凸分析/优化题复用；待 3D-4 Pilot 用第二题验证 |
| M-ex-4 | P0001 研究叙述 | “先建立 $\sup$ 定义，再说明经典等价” | **KEEP IN BODY** | 研究/写作顺序，非跨题数学 procedure |

### 5.2 Error Mode 候选（boundary analysis only；**未**创建 EM ID）

| # | 来源 | 摘要 | 判定 | 理由 |
| --- | --- | --- | --- | --- |
| EM-ex-1 | `09_长期记忆/错题与错误模式.md` EM001 | “知道计算方法但不理解为何选该方法” | **KEEP IN BODY** | 汇总占位；根因/表现均为「待补充」；无 Attempt 级证据链 |
| EM-ex-2 | 同上 EM003 | “多元复合函数求导符号混乱” | **PROMOTE CANDIDATE**（待 Pilot） | 机制描述较稳定，但仓库 **无** 对应 Attempt 记录；3D-4 前不创建 EM0001 |
| EM-ex-3 | A000002 | partial：未构造 $\varphi$ 特征向量即停止 | **KEEP IN BODY** | 是 **incomplete progress**，不是稳定错误机制；`outcome: partial` 已足够 |
| EM-ex-4 | A000001 独立阶段 | 构造 $X_{ij}$ 后尚未完成计算 | **KEEP IN BODY** | 未完成 ≠ Error Mode；后续在帮助下完成，无“稳定算错机制” |

### 5.3 P0002 / Attempt 边界示例（不创建对象）

* **“利用 $B^T$ 特征向量”** — 步骤/知识应用，**不是** Method object（见 M-ex-2）。
* **“遗漏验证 $\{X_{ij}\}$ 构成基”** — 若只发生一次且已纠正，**不是** Error Mode；若未来跨题反复“构造后未验证线性无关”，再考虑 EM promotion。

### 5.4 Promotion Threshold 验证结论

**WORKABLE** — 现有仓库内容可用上述门槛区分 Knowledge / Attempt body / 未来 Method·EM object，无需修改 threshold。  
EM001–EM005 汇总表 **不能** 直接当作 production Error Mode；需补 mechanism + 证据后再进入 3D-4 Pilot。

---

## 6. Open Questions + Next Phase

### 6.1 Open Questions

1. ~~Method 与 Knowledge 的边界操作规则~~ → **3D-1 CLOSED**（见 Phase 3D-1 §6）
2. ~~Attempt body 中识别到的 method/error **是否**以及 **如何** 在 3E 链接到 M/EM ID~~ → **3D-3 CLOSED**（A↔M / A↔EM = Evidence relation，physical storage **DEFER**；见 Phase 3D-3）
3. `09_长期记忆/错题与错误模式.md` 中 EM001–EM005 **legacy 编号** → **3D-2 Semantic Audit DONE**；正式 migration → **DEFER**（3D-4+ / 3D-6 前）
4. Method / Error Mode 的 **主存储目录** → **DEFER 3D-4**
5. Method / Error Mode lifecycle 是否沿用 K/P 式 → **DEFER 3D-4**
6. **不** 建立 CommonStaticObjectSchema / 共享继承（3D-0 已禁止；若 3D-4 发现重复再提炼）。

### 6.2 3D 推荐主线（**不得**自动执行）

| Phase | 内容 |
| --- | --- |
| **3D-1** | Method Semantic Contract → **DONE** |
| **3D-2** | Error Mode Semantic Contract → **DONE** |
| **3D-3** | Cross-Object Relation Contract → **DONE** |
| **3D-4M** | Method Minimal Candidate Schema → **DONE** |
| **3D-4E** | Error Mode Minimal Candidate Schema → **DONE** |
| **3D-5M** | Real Method Object Pilot → **DONE** |
| **3D-5E** | Error Mode Real Object Pilot（await real error Evidence） |
| **3D-6M** | Method Final Review → **DONE** |
| **3D-7M** | Method Schema v1 Freeze → **DONE** |
| **3D-8M** | Method Validator v1 → **DONE** |
| **3D-9M** | Method Workspace Integration → **DONE** |
| **3D-6** | Final Review（cross-object） |
| **3D-7** | Schema Freeze + Propagation |
| **3D-8** | Method / Error Mode Validators |
| **3D-9** | Validated Registry → Workspace Integration |

### 6.3 3D-0 明确 Non-Goals

* 未创建 M0001 / EM0001 或任何 production Method / Error Mode object  
* 未设计 Frozen Schema / YAML 字段表  
* 未创建 Validator / Indexer 集成  
* 未修改 Frozen K / P / A Schema  
* 未修改 A000001 / A000002  

---

# Phase 3D-1 — Method Semantic Contract

**状态：** DONE（2026-08-19）  
**范围：** 只冻结 Method **语义**；不设计 YAML、ID、目录、Validator、关系存储。

---

## 1. Working Definition

### 1.1 正式工作定义（3D-1 CLOSED）

**Method** 是一种具有 **稳定数学意图（Stable Mathematical Intent）** 与 **稳定推理/操作机制（Stable Reasoning / Operative Mechanism）**、能够 **脱离单一 Problem 的偶然细节** 而复用的 **solving / reasoning procedure**。

它主要回答：

> 面对某类数学情境，为了达到某种 **中间或最终数学目标**，通常按照什么 **稳定 reasoning mechanism** 推进？

**3D-0 定义审查结论：** **WORKABLE**，3D-1 在 identity 与 granularity 上 **收紧**，未推翻 3D-0 方向。

### 1.2 什么算 Method（语义层）

* 可独立回答 **When / Intent / Mechanism / Skeleton**（见 §4）；
* identity 为 **procedural**，不是 propositional；
* 可经 **Observed Reuse** 或 **Intrinsic Reusability** 证明超越单题偶然性（见 §5）；
* Method intent 可以是 **稳定的 intermediate mathematical effect**，不必等于某 Problem 的最终结论。

### 1.3 什么不算 Method（3D-1 重申并 CLOSED）

| 不是 Method | 原因 |
| --- | --- |
| **Knowledge** | 回答「是什么 / 为何成立」，不是 procedure |
| **Knowledge Application（薄）** | 仅「在此应用定理 T」，无稳定 scene + construction + skeleton |
| **Problem Solution** | 完整解答目标是一次性任务完成，不是可复用 procedure 对象 |
| **Attempt step** | 单次 historical evidence |
| **Recommendation / Derived** | 练什么、优先复习什么 |
| **单题不可抽象操作** | 只能写成「本题令 $X=uv^T$」，无法脱离题面说明 When/Intent/Mechanism |
| **Pedagogical / research narrative** | 写作或研究组织顺序（如 P0001「先 sup 再经典等价」） |
| **过细原子操作** | 转置、代入、展开、普通求导等（见 §4 Granularity） |
| **过粗方法标签** | 「构造法」「代数法」「利用定理」（见 §4 Granularity） |

---

## 2. Identity Contract

### 2.1 Identity Core（**CLOSED**）

$$\text{Method Identity} = \text{Stable Mathematical Intent} + \text{Stable Reasoning / Operative Mechanism}$$

| 成分 | 含义 | 示例 |
| --- | --- | --- |
| **Stable Mathematical Intent** | 该 Method 想实现的数学作用（可为中间结构） | 暴露谱结构；构造满足定理条件的辅助对象；把约束问题转为对偶形式；制造零点/单调性/正交性 |
| **Stable Reasoning / Operative Mechanism** | 依赖什么核心 reasoning mechanism 推进 | 反解梯度再代入；利用左右特征结构构造秩一对象；构造端点等值辅助函数再应用 Rolle |

**Procedure skeleton** 是 Mechanism 的可描述外壳（见 §7），参与 identity 判定，但不单独构成 identity。

### 2.2 Identity 明确 **不** 依赖（**CLOSED**）

Method identity **不得** 由以下因素决定：

Problem ID · Attempt ID · 用户 · 文件名 · 变量名 · 某个具体例题 · 具体数字 · 使用时间 · 使用次数 · 成功率 · mastery · proficiency · 教学顺序 · 推荐优先级

### 2.3 Applicability（语义重要，存储 DEFER）

**3D-1 冻结：** 一个合格的 Method **必须** 在语义上能说明 **「什么数学情境下值得考虑它？」**

若无法回答 When，通常说明对象 **过宽** 或 **只是局部操作**。

**如何保存 Applicability**（YAML / body / Knowledge relation）→ **DEFER 3D-4**。

### 2.4 Mathematical Preconditions vs Knowledge Prerequisites（**CLOSED** 区分）

| 概念 | 含义 | 示例 |
| --- | --- | --- |
| **Mathematical Preconditions** | 方法 **可成立 / 可使用** 所需的数学条件 | 矩阵可对角化；函数连续；对象非零；算子可逆 |
| **Knowledge Prerequisites** | **理解** 该 Method 需掌握的知识 | 需知 Rolle 定理；需理解特征向量；需知 Hessian |

两者 **不是** 同一概念。字段设计 → **DEFER 3D-4**。

---

## 3. Same / Different / Variant

### 3.1 Same Method Rule（**CLOSED**）

若两个 procedure 满足：

* mathematical intent 基本一致；
* core reasoning mechanism 一致；
* operative skeleton 一致；
* 差异主要来自变量、维度、符号、坐标选择、具体 Problem 表面形式；

则通常 → **SAME METHOD**（差异写入 body 作为 variant / example，**不** 新建 identity）。

**Conceptual Test 1：** 经典 Legendre 路径在一元（$p=f'(x)$）与多元（$p=\nabla f(x)$）→ **SAME METHOD**；notation / dimension 差异为 variant。

### 3.2 Different Method Rule（**CLOSED**）

若最终服务目标类似，但 **core mathematical mechanism 明显不同** → **DIFFERENT METHOD CANDIDATES**。

**不因**「最后证明同一结论」而合并。

**Conceptual Test 2（P0002 谱问题）：**

| 方案 | Core mechanism | 判定 |
| --- | --- | --- |
| **A** | 利用左右特征向量构造秩一对象，使 $\varphi(X)=\lambda X$ | Method candidate A |
| **B** | vec / Kronecker 表示，把 $\varphi$ 转为矩阵特征值问题 | Method candidate B |

→ **DIFFERENT METHODS**（mechanism 不同）。

### 3.3 Variant Rule（**CLOSED**；不设计 variant 字段）

若变化仅涉及 notation · parameters · dimension · coordinate choice · 某步实现细节 · Problem 表面包装，而 **intent + core operative mechanism** 未实质变化：

→ **same Method + variant / example in body**

只有当 **core reasoning mechanism** 或 **procedure skeleton** 发生 **实质变化**，才考虑 **new Method identity**。

---

## 4. Granularity + Atomicity

### 4.1 Minimum Useful Granularity（**CLOSED**）

一个 Method **至少** 必须能独立回答：

| # | 问题 |
| --- | --- |
| **When** | 什么数学情境下值得考虑它？ |
| **Intent** | 它试图达到什么数学目标 / 中间结构？ |
| **Mechanism** | 它依靠什么核心数学机制？ |
| **Skeleton** | 大致按什么稳定 procedure 推进？ |

不要求固定步骤数；但若四问 **无法** 回答 → 通常 **不应** 晋升为 Method Object。

### 4.2 过细 — 通常 **不是** 独立 Method（**CLOSED**）

| 示例 | 原因 |
| --- | --- |
| 等式两边同除一个数 | 无独立 intent + skeleton |
| 展开括号 | 代数原子操作 |
| 将等式转置 | 符号操作 |
| 代入已知公式 | 除非整段构成更大 procedure 的一步 |
| 写出特征方程 | 局部写式 |
| 普通求导 / 一次矩阵乘法 | 无独立 procedure identity |
| A000002：$B^T v=\lambda v \Rightarrow v^T B=\lambda v^T$ | 单步 Knowledge 应用 |

### 4.3 过粗 — 通常 **不合格**（**CLOSED**）

| 示例 | 原因 |
| --- | --- |
| 构造法 / 代数法 / 分析法 / 几何法 | 无法回答 When / Mechanism / Skeleton |
| 利用定理 / 做变换 / 分类讨论 | 粒度过宽，非可执行 procedure |

### 4.4 Atomicity Contract（**CLOSED**）

* 一个 Method **不应** 只是某题中多个 **独立** Method 的偶然串联。
* **完整 Solution ≠ 一个 Method Object**；one Solution → may contain 0 / 1 / many Methods。
* 若组合本身具有稳定 intent + ordering + mechanism + 跨题重复 → 未来可考虑 **compound Method**。
* **3D-1 只冻结语义**；`parent_method` / `submethods` / composition 字段 → **DEFER 3D-4**。

---

## 5. Promotion Threshold

### 5.1 四项门槛（**CLOSED**）

Method Candidate **须同时** 满足：

1. **Reusability** — 数学结构具有超越当前 Problem 的适用性（见 5.2）；
2. **Stable Mathematical Intent**；
3. **Stable Operative Structure（Procedure skeleton）**；
4. **Independence from accidental details of one Problem** — 能脱离该题特定变量/数值/part 表述独立定义。

### 5.2 Reusability — Route A / Route B（**CLOSED**）

**Reusability ≠ observed frequency only**。证据可来自：

| Route | 条件 |
| --- | --- |
| **Route A — Observed Reuse** | 已在 ≥2 个不同 Problem / 题族中 **实际观察到** 复用 |
| **Route B — Intrinsic Reusability** | 当前可能只有 **一个** 仓库实例，但该 procedure 已能：脱离具体变量与数字；清楚描述适用场景、intent、skeleton；合理预期在同类其他 Problem 中复用 |

**one observed Problem → automatic rejection：NO**

但若只能描述成「本题令 $X=uv^T$」且无法脱离题面说明通用 purpose 与 mechanism → **KEEP IN BODY**。

**不在 Method source 保存** `reuse_count` 等统计（Derived，Phase 3E）。

### 5.3 Method-worthy ≠ Automatic Object Creation（**CLOSED**）

**Semantic Qualification ≠ Creation Authorization**

即使内容满足 semantic threshold，Agent **不得** 因检测到 pattern 而 **自动创建** M object。

Production promotion 须经 Candidate → Pilot / review → authorized creation（workflow → **DEFER**）。

---

## 6. Boundary with K / P / A / Derived

### 6.1 Method vs Knowledge（**CLOSED**）

| | Knowledge | Method |
| --- | --- | --- |
| 主要回答 | 是什么；为何成立；有何性质 | 面对某类目标 **如何推进**；如何组织 reasoning；如何构造中间对象 |
| Identity | propositional / conceptual | **procedural** |

**示例：** Rolle 定理 → **Knowledge**；「构造满足端点等值条件的辅助函数，再应用 Rolle 制造导数零点」→ **Method Candidate**。

Method **可以依赖** Knowledge，但 Method identity **不能** 退化为定理 identity。

### 6.2 Knowledge Application vs Method（**CLOSED** — 3D-0 Open Q1）

| 情形 | 判定 |
| --- | --- |
| 仅「在这里应用定理 T」，无稳定 scene recognition + construction + operation sequence + reasoning mechanism | **Knowledge Application** — 不独立晋升 Method |
| 含：如何识别适用情境；为何选该 Knowledge；如何构造中间对象/条件；如何稳定推进到目标 | 更可能达到 **Method Granularity** |

**示例：**

* 「使用 Rolle 定理」→ **Knowledge Application**
* 「构造辅助函数使端点函数值相等，再应用 Rolle 制造内部导数零点」→ **Method Candidate**

Knowledge「应用」节可 **描述** 相关 Method，但 procedure identity 应在 Method 对象（关系存储 → **DEFER 3D-3**）。

### 6.3 Method vs Problem Solution（**CLOSED**）

| | Problem Solution | Method |
| --- | --- | --- |
| 目标 | 完整解决 **一个** 确定 Problem | 抽取稳定、可复用的 reasoning procedure |
| 关系 | one Solution → 0 / 1 / many Methods | Solution **≠** Method |

不要把整篇证明 / 答案 / 推导直接升级为 Method。

### 6.4 Method vs Attempt（**CLOSED**）

| | Attempt | Method |
| --- | --- | --- |
| 层级 | Evidence — 一次真实历史 solving/reasoning | Static — 可复用 procedure |
| 关系 | Attempt may instantiate / use / partially discover a Method | Method identity **不属于** 该 Attempt |

**Frozen Attempt Schema v1 保持不变。** A ↔ M 物理链接 → **DEFER 3D-3**（不得 retroactive 增加 Attempt YAML 字段）。

### 6.5 Method vs Recommendation / Derived（**CLOSED**）

Recommendation（下一题练 X、优先复习 X、需重训 X）→ **Derived / Action layer**。

Method Source Object **只** 保存数学 procedure 本身；source **不得** 拥有 mastery · proficiency · success_rate · recommended · priority · review_priority · next_use · confidence · weakness 等字段。

### 6.6 Method Intent vs Problem Goal（**CLOSED**）

Method 的 mathematical intent **不必** 等于 Problem 最终目标；可以是稳定的 **intermediate mathematical effect**。

**示例（P0002）：** Problem 目标可能是「证明 $\varphi$ 有特征值 $\lambda_1-\lambda_2$」；Method intent 可以是「构造可同时利用 $A$ 与 $B$（或对偶侧）特征关系的秩一对象，使双边作用化为标量谱关系」。

---

## 7. Procedure Skeleton Contract

**CLOSED：** 可晋升 Method **必须** 能描述 **稳定 procedure skeleton**（步骤 **角色** 稳定，非固定步骤数）。

示意（非固定模板）：

1. 识别目标结构 / 适用情境  
2. 构造辅助对象或选择表示  
3. 利用稳定数学关系  
4. 把原问题转化为更标准形式并得出结论  

**完全不存在** 稳定 procedure skeleton → 通常 **不是** Method Object。

YAML / heading 表示 → **DEFER 3D-4**。

---

## 8. Real Repository Boundary Tests

### 8.1 Case A — A000002（$B^T v=\lambda v \Rightarrow v^T B=\lambda v^T$）

| 项 | 内容 |
| --- | --- |
| **Classification** | **Knowledge Application** + **Attempt Step** |
| **Reason** | 该步本质是转置特征值关系（Knowledge）的单次应用；无独立 When/Intent/Mechanism/Skeleton；无法脱离「为 P0002(a) 准备 $v^T B$ 形式」说明跨题 procedure |

### 8.2 Case B — A000001 / P0002(b)（秩一特征构造）

**抽象表述：** 利用左右（或对偶侧）特征结构构造秩一对象，使双边线性算子在秩一对象上化为标量谱关系。

| 项 | 内容 |
| --- | --- |
| **When** | 矩阵空间上形如「左乘 + 右乘」的线性算子，且左右侧有可配对谱数据 |
| **Intent** | 暴露算子谱 / 构造特征向量 |
| **Mechanism** | 张量积型 $X=u v^T$（或等价秩一表示），分别利用两侧特征关系 |
| **Skeleton** | 取两侧特征基 → 构造秩一对象 → 代入算子 → 得到标量关系 →（必要时）验证张成基 |
| **Classification** | **METHOD-WORTHY CANDIDATE**（Route B — Intrinsic Reusability） |
| **Reason** | 可脱离 P0002 独立定义四问；同类问题（Sylvester/Lyapunov/交换子谱等）合理预期复用。**未** 创建 M object |

**与 Conceptual Test 2 方案 A 同族；与 vec/Kronecker 方案 B 为 DIFFERENT METHOD。**

### 8.3 Case C — P0001 / K0001（经典 Legendre 路径）

| 项 | 内容 |
| --- | --- |
| **When** | 光滑严格凸，且梯度/导数映射在像集上可逆；需从共轭变量反求原变量 |
| **Intent** | 把共轭定义 $px-f(x)$ 在良性情形落实为可计算的 $f^*(p)$ |
| **Mechanism** | 一阶条件 $p=f'(x)$ 或 $p=\nabla f(x)$ → 反解 → 代回 |
| **Skeleton** | 识别可逆梯度映射 → 反解 $x(p)$ → 代入 $px-f(x)$ |
| **Classification** | **METHOD-WORTHY CANDIDATE**（Route A 潜力 + Route B 已满足） |
| **Reason** | 仓库内 P0001/K0001 有完整叙述；可跨凸分析/优化题复用；四问齐全。**未** 创建 M object |

### 8.4 Case D — P0001「先 sup 再经典等价」

| 项 | 内容 |
| --- | --- |
| **Classification** | **KEEP IN BODY** — research / exposition organization |
| **Reason** | 是研究叙述顺序（最高仿射下界 → 优化 → L–F → 经典写法），不是跨题 mathematical procedure |

### 8.5 Negative Granularity Example

P0001/K0001 中若仅写「**作变换**」「**代入** $p=f'(x)$」「**利用** Fenchel–Young」而不展开 construction 与 skeleton → **NOT METHOD OBJECT**（过粗或过细标签）。

### 8.6 3D-0 示例表修正说明

3D-0 M-ex-1 判 **KEEP IN BODY** 主要因「仅 1 题 + 强绑定」直觉；3D-1 用 Route B 重审后 → **METHOD-WORTHY CANDIDATE**（仍 **不** 自动创建对象）。M-ex-2 / M-ex-4 判定 **不变**。

---

## 9. Explicit Deferrals + 3D-1 Decision Summary

### 9.1 DEFER 清单

| 主题 | DEFER |
| --- | --- |
| Knowledge ↔ Method / Problem ↔ Method / Attempt ↔ Method **关系存储** | **3D-3** |
| `schema_version` · `id` · `type` · `title` · `status` · `aliases` · `knowledge` · `created` · `updated` · `tags` · `applicability` · `preconditions` · `variants` · lifecycle | **3D-4** |
| ID namespace（M0001 等） | **3D-4** |
| Method root 目录 | **3D-4** |
| Compound Method schema（parent/sub/composition） | **3D-4** |
| Method Validator | **3D-8** |
| Workspace Integration | **3D-9** |
| CommonStaticObjectSchema / shared inheritance | **禁止**（3D-0/3D-1） |

### 9.2 3D-1 CLOSED 项

| 项 | 状态 |
| --- | --- |
| Working Definition | **CLOSED** |
| Identity Core | **CLOSED** |
| Same / Different Rule | **CLOSED** |
| Variant Rule | **CLOSED** |
| Granularity | **CLOSED** |
| Atomicity | **CLOSED** |
| Promotion Threshold | **CLOSED** |
| Knowledge Boundary | **CLOSED** |
| Knowledge Application vs Method | **CLOSED** |
| Problem Boundary | **CLOSED** |
| Attempt Boundary | **CLOSED** |
| Recommendation / Derived Boundary | **CLOSED** |
| Applicability（语义） | **CLOSED** |
| Preconditions vs Prerequisites 区分 | **CLOSED** |
| Procedure Skeleton Requirement | **CLOSED** |
| Method-worthy ≠ auto creation | **CLOSED** |
| Promotion threshold 总评 | **WORKABLE** |

### 9.3 3D-1 Non-Goals（确认）

* 未创建 production Method object / M ID  
* 未设计 Method Schema / YAML  
* 未创建 Validator / Indexer / Workflow  
* 未修改 Frozen K / P / A / Attempt source  
* 未修改 Workspace production pipeline  

---

# Phase 3D-2 — Error Mode Semantic Contract

**状态：** DONE（2026-08-19）  
**范围：** 只冻结 Error Mode **语义**；不设计 YAML、ID、目录、Validator、关系存储、legacy 正式迁移。

---

## 1. Working Definition

### 1.1 正式工作定义（3D-2 CLOSED）

**Error Mode** 是数学 solving / reasoning 中，一种具有 **稳定 Failure Mechanism（Stable Failure Mechanism）** 与 **稳定可识别 Diagnostic Pattern（Stable Diagnostic Pattern）**、能够 **脱离单次 Attempt 偶然细节** 而重复出现的 **failure abstraction**。

它主要回答：

> 哪一种 **稳定的 reasoning failure mechanism**，会使解题过程以 **某类可识别方式** 偏离正确数学结构？

**3D-0 定义审查结论：** **WORKABLE**；3D-2 在 identity、granularity、evidence policy 上 **收紧**，未推翻 3D-0「mechanism 优先于 manifestation」方向。

### 1.2 什么算 Error Mode（语义层）

* 可独立回答 **Context/Trigger · Mechanism · Diagnostic Signature · Mathematical Consequence · Cross-instance recognizability**（见 §5）；
* identity 围绕 **failure mechanism**（primary）；Diagnostic Pattern 为 recognizability requirement，不是单次错误答案或 outcome 标签；
* 经 Semantic Qualification；晋升 production 还须 Promotion Evidence（见 §6）；
* **与 Method 不对称：** Error Mode 更依赖 **真实错误 Evidence**；纯 pedagogical hypothesis 不自动 production 化。

### 1.3 什么不算 Error Mode（3D-2 重申并 CLOSED）

| 不是 Error Mode | 原因 |
| --- | --- |
| **Slip / typo** | 一次性机械错误，无稳定 mechanism |
| **Knowledge gap / absence** | 「完全不知道 X」首先是缺失 Knowledge，不是 failure pattern |
| **`partial` / `unsolved` / abandoned** | 完成状态，不说明 failure mechanism |
| **`incorrect` outcome** | Attempt 标签；≠ Error Mode identity |
| **Problem defect** | 题面/数域/条件歧义 → Content Review |
| **Method execution failure（无 mechanism）** | 「Method 没做出来」≠ 自动 Error Mode |
| **assisted / 需要帮助** | 外部帮助完成 ≠ 错误机制 |
| **过细 manifestation** | 某行写错符号、一次算术错 |
| **过粗标签** | 粗心、基础不牢、不会做、思路不清 |
| **Legacy 占位 / 无 mechanism 汇总** | EM001–EM005 当前形态 |
| **Recommendation / Derived** | 复习优先级、出现频率等 |

---

## 2. Identity Contract

### 2.1 Identity Core（**CLOSED**；**3D-3 语义规范化**见下）

**3D-2 原始表述（historical）：**

$$\text{Error Mode Identity} = \text{Stable Failure Mechanism} + \text{Stable Diagnostic Pattern}$$

**3D-3 规范化（relation design 前冻结）：**

| 成分 | 角色 |
| --- | --- |
| **Error Mode Identity Core** | **Stable Failure Mechanism** — primary identity |
| **Diagnostic Pattern** | **Required Recognizability Criterion** — 用于判断不同 manifestation 是否属于 **同一** stable mechanism；**不是** 与 mechanism 并列的独立 identity key |

**规范化理由：** mechanism 相同时，manifestation 表面差异 **不应** 因 Diagnostic Pattern 表述变化而自动拆成不同 Error Mode。Diagnostic Pattern 仍 **必需**（无 recognizability → 不满足 Error Mode 语义），但不与 mechanism **平分** identity。

| 成分 | 含义 |
| --- | --- |
| **Stable Failure Mechanism** | 真正导致 reasoning **系统性偏离** 的机制 |
| **Diagnostic Pattern** | 该 mechanism 通常如何 **可重复识别**（bounded manifestation **family**） |

### 2.2 Identity 明确 **不** 依赖（**CLOSED**）

Attempt ID · Problem ID · 用户 · 文件名 · 某一次具体错误答案 · 某个具体符号 · 某个具体变量 · 出现时间 · 出现次数 · frequency · severity score · mastery · weakness · **correction strategy** · 教学顺序

### 2.3 Manifestation / Mechanism / Correction（**CLOSED**）

| 层级 | 含义 | Identity 角色 |
| --- | --- | --- |
| **Error Manifestation** | 某次 Attempt 中错误具体「长什么样」 | **不是** identity 核心 |
| **Error Mechanism** | 为何 reasoning 会 **稳定** 产生该类错误 | **是** identity 核心（与 Diagnostic Pattern 配对） |
| **Correction / Prevention** | 如何修正或预防 | **不是** identity；可有多种策略 |

**原则：**

* 同一 Error Mode → 可有 **多个** manifestation；
* 同一表面 manifestation → 可能来自 **不同** mechanism → **不同** Error Mode 或 **NOT Error Mode**（如 typo）；
* **Same symptom ≠ same Error Mode**（**CLOSED**）。

**Correction 如何保存** → **DEFER 3D-4**。

---

## 3. Same / Different

### 3.1 Same Error Mode Rule（**CLOSED**）

若两个错误事件：

* underlying **failure mechanism** 一致；
* **diagnostic signature** 基本一致；
* 差异主要来自题目、变量、符号、具体 manifestation；

→ 通常 **SAME ERROR MODE**。

**Conceptual Test 1：** 不同题中均因 **未验证 theorem applicability conditions** 而机械套用定理 → 可能 **SAME ERROR MODE**（identity 围绕「忽略适用条件的系统性误用」，非具体定理 ID）。

### 3.2 Different Error Mode Rule（**CLOSED**）

* 表面错误结果相似，但 **core failure mechanism 不同** → **DIFFERENT ERROR MODES**；
* 即使 manifestation 不完全一样，若 **稳定 mechanism 相同** → 可能 **SAME ERROR MODE**。

**Conceptual Test 2：** 两答案均出现「负号错误」：

| 事件 | Mechanism | 判定 |
| --- | --- | --- |
| A | 复合求导链式法则路径遗漏 | Error Mode candidate A |
| B | 抄写 typo | **Slip** — NOT Error Mode |

→ **DIFFERENT**（第二项可能根本不是 Error Mode）。

### 3.3 Same Symptom ≠ Same Error Mode（**CLOSED**）

相同错误结果 **≠** 相同 Error Mode。须比较 **mechanism**，不是比较最终式子是否「看起来一样错」。

---

## 4. Granularity + Atomicity

### 4.1 Minimum Useful Granularity（**CLOSED**）

一个 Error Mode **至少** 应能回答：

| # | 问题 |
| --- | --- |
| **Context / Trigger** | 哪类数学情境容易触发？ |
| **Mechanism** | reasoning 在哪里发生稳定偏离？ |
| **Diagnostic Signature** | 通常如何通过表现识别？ |
| **Mathematical Consequence** | 通常破坏哪类条件、结构或结论？ |
| **Cross-instance recognizability** | 下次出现能否识别为「同一种错误机制」？ |

不要求固定 body heading；若五问 **无法** 回答 → 通常 **不应** 晋升 Error Mode Object。

### 4.2 过细 — 通常 **不是** 独立 Error Mode（**CLOSED**）

| 示例 | 原因 |
| --- | --- |
| 某题第 3 行漏写负号 | 单次 manifestation |
| 写错一次 $2\times 3$ | slip |
| 抄错下标 | slip |
| A000002：未继续构造 $X$ | incomplete progress，非 mechanism |
| A000002：算到一半停止 | partial，非 Error Mode |

### 4.3 过粗 — 通常 **不合格**（**CLOSED**）

| 示例 | 原因 |
| --- | --- |
| 粗心 / 基础不牢 / 不会做 / 思路不清 | 无 stable diagnostic mechanism |
| 算错 / 概念混乱 / 推导有问题 | 无法回答 Mechanism + Signature |
| legacy EM005「不清楚应调用哪个定理」 | 方法选择困难，过宽 |

### 4.4 Atomicity Contract（**CLOSED**）

* 一个 Error Mode → **一个** primary stable failure mechanism；
* legacy「概念混淆、符号错误、不会选方法」混合条目 → **SPLIT CANDIDATE** 或 **REJECT AS TOO BROAD**；
* **Compound Error Mode** → **DEFER / YAGNI**（v1 优先 one EM = one primary mechanism；共现 = 多个 EM 同时出现，不建 compound schema）。

---

## 5. Slip Boundary（**CLOSED**）

**Slip：** 一次性机械错误，**无** 稳定 reasoning mechanism（如：明知规则但偶然抄错数字）。

→ 通常 **KEEP IN ATTEMPT BODY**，不升格 Error Mode。

**判定关键：** 是否存在 **稳定 failure mechanism**，不是「错了几次」。

若所谓「符号错误」反复来自 **同一** mechanism（如稳定把共轭转置当普通转置）→ 可能 **Error Mode**，不再是 slip。

---

## 6. Promotion Threshold + Evidence Policy

### 6.1 Semantic Qualification（四项门槛 · **CLOSED**）

须 **同时** 满足：

1. Stable Failure Mechanism  
2. Stable Diagnostic Pattern  
3. Independence from accidental details of one Attempt  
4. Long-term Diagnostic Value  

缺一 → 通常 **KEEP IN BODY** / legacy hypothesis。

### 6.2 Promotion Evidence — Route A / Route B（**CLOSED**）

| Route | 条件 |
| --- | --- |
| **Route A — Observed Recurrence** | 多个独立 Attempt / Problem 暴露 **同一** failure mechanism |
| **Route B — Mechanism-Generalizable Evidence** | 可能仅 **一条** 真实错误 Evidence，但 mechanism 已可脱离该题定义 trigger · signature · reasoning failure，并合理预期未来可识别 |

**one observed Attempt → automatic rejection：NO**

### 6.3 Zero Real Evidence Policy（**CLOSED — KEEP**）

**3D-2 立场：** 与 Method 的 Intrinsic Reusability **不对称**。

| 状态 | 允许 |
| --- | --- |
| 无真实错误 Evidence，仅有「理论上可能错」 | **Design Candidate · Pedagogical Note · Legacy Hypothesis** |
| 直接晋升 **Production Error Mode Object** | **NO** — 原则上 **不得** |

**zero real evidence → production promotion：recommended NO**

### 6.4 Error Mode-worthy ≠ Automatic Object Creation（**CLOSED**）

**Semantic Qualification ≠ Creation Authorization**

即使达到 semantic threshold，Agent **不得** 自动创建 EM object。须经 Candidate → Evidence/Pilot → Review → authorized promotion（workflow → **DEFER**）。

**不在 Error Mode source 保存** `frequency` · `recurrence_count` · `last_seen` 等（Derived，Phase 3E）。

---

## 7. Boundary with Attempt / Knowledge / Problem / Method / Derived

### 7.1 Error Mode vs Knowledge Gap（**CLOSED**）

| 情形 | 判定 |
| --- | --- |
| 「完全不知道什么是共轭转置」 | **Knowledge gap / absence** |
| 「稳定把共轭转置当普通转置使用」 | **Misconception / systematic misapplication** → may be Error Mode |

**Missing Knowledge ≠ Error Mode**；**Misconception / Systematic Misapplication → may be Error Mode**。

### 7.2 Error Mode vs partial / unsolved / abandoned（**CLOSED**）

`partial` · `unsolved` · abandoned 只表示 Attempt 完成/结果状态，**不** 说明 failure mechanism。

**「不会下一步」≠ 自动 Error Mode**（见 A000002）。

### 7.3 Error Mode vs incorrect（**CLOSED**）

* `incorrect` = Attempt outcome；
* one incorrect Attempt → 0 / 1 / many Error Modes；
* one Error Mode → 可出现在多个 incorrect Attempts；
* correct Attempt 的 body 中也可能先出现 Error Mode 再自行纠正。

**incorrect ≠ Error Mode identity**。

### 7.4 Error Mode vs Problem Defect（**CLOSED**）

题面定义域不清、数域歧义、条件缺失、题面矛盾 → **Problem Content Review / Source Quality**。

**P0002**（实矩阵 vs 复特征值 vs $\varphi$ 数域未明）→ **NOT learner Error Mode**，即使用户因此答错。

### 7.5 Error Mode vs Method Failure（**CLOSED**）

Method 是 stable reusable procedure；某次 Method 使用失败 **不** 自动意味着 Method 错误或形成 Error Mode。

可能原因：applicability 未满足 · Method 执行错误 · Knowledge 误用 · unrelated slip。

**「Method X 没做出来」≠ Error Mode**；须有 **稳定 failure mechanism**。

### 7.6 Misapplication as Error Mode（**CLOSED**）

若稳定模式为：**在不满足 applicability / precondition 时机械套用** Method 或 Knowledge → 可能形成 Error Mode。

Identity 围绕 **「忽略适用条件的系统性误用机制」**，**不是** 具体 Method ID。M ↔ EM 存储 → **DEFER 3D-3**。

### 7.7 Error Mode vs Attempt / assisted（**CLOSED**）

Attempt = Evidence；Error Mode = static failure abstraction。

**assisted ≠ error**；「需要帮助完成证明」**不** 自动构成 Error Mode（见 A000001）。

A ↔ EM 链接 → **DEFER 3D-3**（不得 retroactive 增加 Attempt `error_mode` 字段）。

### 7.8 Error Mode vs Derived / Recommendation（**CLOSED**）

Error Mode = static failure-pattern abstraction。

**不是** EM source：`frequency` · `recurrence_count` · `last_seen` · `severity_score` · `personal_weakness` · `mastery` · `risk_score` · `review_priority` · `recommended_drill` · `trend`

「EMxxxx 最近出现 4 次」→ **Derived Fact**。

「下次遇到复合函数先画依赖图」→ correction/prevention 或 future recommendation，**不是** Error Mode identity。

---

## 8. Real Repository Tests

### 8.1 Case A — A000002（partial；未继续构造 $\varphi$ 特征对象）

| 项 | 内容 |
| --- | --- |
| **Classification** | **NO ERROR MODE IDENTIFIED** |
| **Reason** | 用户正确得到 $v^T B=\lambda_2 v^T$ 后停止；`outcome: partial` 表示 incomplete progress，**无** 稳定 failure mechanism 证据；「没想到下一步」≠ 错误模式 |

### 8.2 Case B — A000001（assisted；ChatGPT 补全）

| 项 | 内容 |
| --- | --- |
| **Classification** | **NO ERROR MODE IDENTIFIED** |
| **Reason** | 独立阶段有实质性正确构造；后续为 **assisted** 补全，非 incorrect；body 中 **无** 稳定算错/误用 mechanism；**不得** 从「需要帮助」推导 Error Mode |

### 8.3 Case C — legacy EM003（「多元复合函数求导符号混乱」）

| 拆解 | 内容 |
| --- | --- |
| **Manifestation** | 符号/项混乱（表面） |
| **Mechanism** | **未明确** — 可能是：未建立依赖关系；链式法则层次遗漏；指标管理失败；Jacobian 方向约定混淆；… |
| **Classification** | **LEGACY HYPOTHESIS — NEEDS EVIDENCE / MECHANISM CLARIFICATION** |
| **Reason** | 仓库 **无** 对应 Attempt 错误 Evidence；「符号混乱」 alone 过表面；**不是** production Error Mode |

### 8.4 Case D — 「遗漏非零性验证」（概念 + P0002 相关）

**抽象 mechanism：** 证明对象属于特征结构时，只验证算子方程，**遗漏** 定义要求的 **非零性** 条件。

| 项 | 内容 |
| --- | --- |
| **Trigger** | 构造特征向量/矩阵后需证「特征」定义 |
| **Mechanism** | 混淆「满足 $T(v)=\lambda v$」与「$v\neq 0$」的合取条件 |
| **Diagnostic Signature** | 直接由构造式断言特征性，未证非零或线性无关 |
| **Classification** | **ERROR-MODE-WORTHY CANDIDATE**（semantic） |
| **Evidence status** | 仓库 **无** 真实错误 Attempt 实例 → **不得 production 化** |

### 8.5 Case E — P0002 数域 / scalar field 歧义

| 项 | 内容 |
| --- | --- |
| **Classification** | **Problem Content / Semantic Issue — NOT ERROR MODE** |
| **Reason** | 题面 domain/codomain/标量域 pending review；属 Source Quality，非用户独立 reasoning failure mechanism |

### 8.6 Negative Granularity Tests

| 示例 | 判定 |
| --- | --- |
| 「第 4 行把 + 写成 -」（无 mechanism） | **NOT ERROR MODE** — slip |
| legacy「粗心」「基础不牢」 | **NOT ERROR MODE** — too coarse |

### 8.7 P0001/K0001「易错点」与 Error Mode 关系

P0001/K0001 中如「混淆 $\sup$ 与 $\max$」「强行套用 $p=f'(x)$ 漏掉 $p=0$」等，是 **Knowledge/Problem 层面的 pedagogical 警示**。

其中 **可能** 抽象为 Error Mode candidate（mechanism：在需 $\sup$ 一般定义时机械套用经典换变量），但当前仓库 **无** 对应 incorrect Attempt Evidence → 仅 **hypothesis**，不 production 化。

---

## 9. Legacy Semantic Audit（EM001–EM005）

**本轮：Semantic Audit only。** 未重编号、迁移、删除或创建 production replacement。

| Legacy | 描述 | Classification | 理由 |
| --- | --- | --- | --- |
| **EM001** | 知道计算方法，但不理解为何选择 | **TOO BROAD · MECHANISM UNCLEAR · NO EVIDENCE** | 动机/理解缺口，非 stable failure mechanism；根因「待补充」 |
| **EM002** | 抽象概念几何意义理解不足 | **TOO BROAD · NO EVIDENCE** | 学习缺口描述，无可操作 diagnostic mechanism |
| **EM003** | 多元复合求导符号混乱 | **LEGACY HYPOTHESIS · MECHANISM UNCLEAR · NO EVIDENCE** | 见 Case C |
| **EM004** | 隐函数二阶求导容易漏项 | **LEGACY HYPOTHESIS · MECHANISM UNCLEAR · NO EVIDENCE** | 「漏项」可能指向链式/乘积法则层次问题，但 mechanism 与 Evidence 均未建立 |
| **EM005** | 不清楚应调用哪个定理 | **TOO BROAD · NO EVIDENCE · NOT ERROR MODE (as written)** | 方法选择困难；更接近 Knowledge/Method mapping 缺口，非 failure abstraction |

**Legacy migration** → **DEFER**（待 Semantic Contract + Candidate Schema 稳定后）。

---

## 10. Explicit Deferrals

| 主题 | DEFER |
| --- | --- |
| K ↔ EM · P ↔ EM · A ↔ EM · M ↔ EM **关系存储** | **3D-3** |
| Schema fields · mechanism/trigger/correction YAML · lifecycle · title | **3D-4** |
| ID namespace（EM0001 / E0001）· legacy EM001–EM005 正式迁移 | **3D-4+** |
| Error Mode root 目录 | **3D-4** |
| Error Mode Validator | **3D-8** |
| Workspace Integration | **3D-9** |
| Compound Error Mode schema | **YAGNI / DEFER** |

---

## 11. Decision Summary

### 11.1 CLOSED 项

Working Definition · Identity Core · Manifestation vs Mechanism · Correction vs Identity · Same/Different · Same Symptom ≠ Same EM · Granularity · Atomicity · Promotion Threshold · Evidence Policy（含 zero-evidence KEEP）· Slip · Knowledge-gap · partial/unsolved · incorrect · Problem-defect · Method-failure · Misapplication · Derived · EM-worthy ≠ auto creation

### 11.2 总评

**Promotion threshold + Evidence policy：WORKABLE**

### 11.3 Non-Goals（确认）

* 未创建 production Error Mode object / EM ID  
* 未设计 Error Mode Schema  
* 未正式迁移 legacy EM001–EM005  
* 未修改 Frozen K / P / A / Attempt source  
* 未修改 Workspace production pipeline  

---

# Phase 3D-3 — Cross-Object Relation Contract

**状态：** DONE（2026-08-19）  
**范围：** 关系 **语义** + v1 SoT 方向 + minimization gate；**不** 设计 YAML 字段、Association Layer、Relation Object、Knowledge Graph。

---

## 1. Core Principles（**CLOSED**）

### 1.1 Relation Minimization Gate

**Relation minimization > Relation completeness**

v1 目标：**最少必须长期保存** 的关系，足以支撑 Method / Error Mode Object，同时避免重复、漂移与反向污染 Frozen K/P/A。

### 1.2 Single Source of Truth

**Single Source of Truth > Bidirectional convenience**

* 禁止同一关系在 **两个** Source Object 中 **双向** 重复保存为 authoritative truth；
* Reverse lookup → Validator / Registry / Indexer / Association layer **Derived**。

### 1.3 关系类型 Taxonomy（**CLOSED**）

| 类型 | 含义 | 示例 |
| --- | --- | --- |
| **A. Intrinsic Static Relation** | 对象本身长期、稳定的数学/语义依赖；无 Attempt 也可能成立 | Method → depends on → Knowledge |
| **B. Applicability / Contextual Relation** | 情境依赖的适用性；many-to-many；随解法/上下文变化 | Problem ↔ Method 适用性 |
| **C. Evidence Relation** | 一次真实历史 Evidence 发生了什么 | Attempt used / exhibited → M / EM |
| **D. Derived / Interpretive Relation** | 由多条 Source / Evidence 统计或解释得出 | Problem 最常用 Method；用户 weak EM |

**边界：** Intrinsic static ≠ Applicability ≠ Evidence ≠ Derived。

### 1.4 五维判断（每条关系 **CLOSED**）

1. **Semantic existence** — 语义上是否真实存在？  
2. **Relation type** — Static / Applicability / Evidence / Derived？  
3. **v1 necessity** — v1 是否必须结构化保存？  
4. **Source of Truth** — 若保存，唯一 authoritative owner side？  
5. **Reverse relation** — 必须 Derived，不得双存？

**决定词：** **KEEP FOR V1** · **DEFER** · **REJECT**

### 1.5 Relation Necessity Test（**CLOSED**）

仅当以下 **全部为 YES** 才进入 v1 Source Schema：

1. 属于对象长期稳定的 intrinsic semantics（或 Frozen 已确立的 static 关系）；  
2. 不结构化保存会丢失 **无法可靠恢复** 的 source truth；  
3. 存在自然 **唯一** owner side；  
4. 有 **真实** 下游 machine 消费需求（非「以后可能方便」）；  
5. **不会** 迫使修改 Frozen K/P/A。

若仅为「以后可能方便」→ **DEFER**。

### 1.6 Relation Identity Independence（**CLOSED**）

**Relation change ≠ automatic identity change**

* Method 新增 K reference，但 Intent / Mechanism 未变 → **same Method**；  
* EM 关联更多 K，但 Failure Mechanism 未变 → **same Error Mode**。

**Knowledge / Problem / Attempt references ≠ Method / EM identity core**（supporting metadata only）。

### 1.7 Structured Relation vs Body Mention（**CLOSED**）

Markdown body 中出现 `K0001` · `P0002` · `A000001` → **documentation / example**，**不自动** 成为 structured relation。

仅未来 Schema **明确规定** 的 metadata 才是 formal source relation。

### 1.8 Reverse Lookup Policy（**CLOSED**）

若 **Method → K** 为 source → **K → Methods** **必须 Derived**（不得写入 Knowledge YAML）。

若 **EM → K** 为 source → **K → Error Modes** **必须 Derived**。

**已有 baseline（Frozen，本轮不修改）：** **Problem → Knowledge**（`Problem.knowledge`）为 SoT；**Knowledge → Problems** 由 indexer 反向派生（`元数据规范.md` §6 / §7.7）。

### 1.9 Generic Relation Object（**REJECT / YAGNI**）

**不** 创建 Relation / Edge / Graph Object（如 `source: A000001, predicate: used_method, target: M0001`）。

**理由：** 当前关系数量与真实需求不足以证明独立 relation infrastructure；Frozen K/P/A 不可改时未来再评估 Association sidecar。

**禁止：** NetworkX / Neo4j / RDF / triple store / `relations/` 目录 / Knowledge Graph。

---

## 2. Relationship Decision Table

| Relation | Semantic Type | Exists? | v1 Need | Source of Truth | Reverse | Identity Role | **Decision** | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **K ↔ M** | Intrinsic Static | YES | Optional candidate | **Method → Knowledge** | K→M **Derived** | Supporting metadata；≠ Method identity | **KEEP FOR V1**（optional field candidate） | Method 最清楚自身依赖哪些 K；不必每个 M 都有 link |
| **K ↔ EM** | Intrinsic Static（may exist） | YES | Optional；physical defer | **Error Mode → Knowledge** | K→EM **Derived** | Supporting；≠ EM identity；非 required | **KEEP FOR V1**（semantic）；physical **DEFER → 3D-4E** | 机制可跨多 K domain；EM Evidence 尚不成熟不阻塞语义 |
| **P ↔ M** | Applicability / Contextual | YES | NO for v1 core | **None in core schema** | N/A | N/A | **DEFER** | many-to-many contextual；双存 anti-pattern；未来 Association / Derived |
| **P ↔ EM** | Derived / Contextual | YES（统计意义） | NO | **None** | N/A | N/A | **DEFER** | 来自 Attempt 聚合 + 教学经验；非 Problem intrinsic |
| **A ↔ M** | Evidence | YES | NO for v1 | **None**（Attempt v1 Frozen） | N/A | Historical association | **DEFER** | body 已保真；不得改 Attempt YAML；不得 solution-similarity 自动链接 |
| **A ↔ EM** | Evidence | YES | NO for v1 | **None**（Attempt v1 Frozen） | N/A | Diagnostic association | **DEFER** | 须具体 failure mechanism evidence；不得 outcome 自动推导 |
| **M ↔ EM** | Optional semantic | MAY | NO | **None** | N/A | Misapplication 可语义相关 | **DEFER** | 非一一对应；无 v1 必要 |

**Bidirectional duplicated source relations recommended：NONE**

---

## 3. Per-Relation Contracts

### 3.1 Knowledge ↔ Method（**CLOSED**）

* **Semantic：** Method procedure 常 **depends on / uses** Knowledge（定理、定义、性质）；Method ≠ Knowledge。  
* **Type：** Intrinsic Static。  
* **Required?** **NO** — Method 语义自洽时可无 formal K link。  
* **SoT：** **Method-side** references Knowledge。  
* **禁止：** `Knowledge.methods` 作为 source；`Problem.methods` + `Method.problems` 双存。  
* **v1：** **KEEP FOR V1** — optional Method → K list（字段名 **DEFER 3D-4M**）。

### 3.2 Knowledge ↔ Error Mode（**CLOSED**）

* **Semantic：** EM 常 **concerns / relates to** Knowledge misunderstanding 或 cross-domain proof obligation；**非** 每个 EM 都是 K misunderstanding。  
* **Type：** Intrinsic Static（when present）。  
* **Required?** **NO**。  
* **SoT：** **Error Mode-side** → Knowledge。  
* **禁止：** `Knowledge.error_modes` 作为 source。  
* **v1：** 语义 **KEEP FOR V1** candidate；physical YAML **DEFER → 3D-4E**（无 production EM Pilot 前不阻塞）。

### 3.3 Problem ↔ Method（**CLOSED**）

* **Semantic：** Problem 可适用多 Method；Method 可服务多 Problem — **many-to-many contextual**。  
* **Type：** Applicability / Contextual — **非** purely intrinsic static。  
* **Anti-pattern：** `Problem.methods` + `Method.problems` 双存。  
* **Body example：** Method body 写「见 P0002」= documentation example ≠ authoritative P↔M mapping。  
* **Decision：** **DEFER** — 未来 Association Layer 或 Derived Applicability Mapping。

### 3.4 Problem ↔ Error Mode（**CLOSED**）

* **Semantic：** 「某题高发某 EM」多来自 Attempt 统计 + 教学判断。  
* **Type：** Derived / Contextual。  
* **禁止：** `Problem.error_modes` · `ErrorMode.problems` 作为 core source。  
* **Decision：** **DEFER**。

### 3.5 Attempt ↔ Method（**CLOSED**）

* **Semantic：** Attempt **used / attempted / discovered / partially used** Method — **Evidence Relation**。  
* **Attempt Schema v1 Frozen：** **不得** 增加 `method` / `methods`。  
* **Governance：** 不得由最终答案与 Method 表面一致而 **自动** 断言 used；须真实 process evidence。  
* **Decision：** **DEFER** physical storage（Association / sidecar / future schema version — 3D-4+ / 3E）。

### 3.6 Attempt ↔ Error Mode（**CLOSED**）

* **Semantic：** Attempt **exhibited** Error Mode — **Evidence Relation**。  
* **保守原则：** `partial` · `incorrect` · `assisted` · `unsolved` **均不** 自动 → EM link。  
* **Attempt Schema v1 Frozen：** **不得** 增加 `error_mode` / `error_modes`。  
* **Decision：** **DEFER**；Assessment / diagnostic provenance 存储 **DEFER**。

### 3.7 Method ↔ Error Mode（**CLOSED**）

* **Semantic：** EM 可能是某类 Method 的 **stable misapplication**（如忽略 applicability）；非一一对应。  
* **Decision：** **DEFER** — 禁止 v1 `Method.common_errors` / `ErrorMode.method` core fields。

### 3.8 Knowledge ↔ Problem（Reference Baseline — **不修改**）

**Frozen：** `Problem.knowledge` = Problem → Knowledge **唯一** source side；反向 K→P **Derived**（indexer scan）。  
**Consistency lesson：** 单侧 SoT + Derived reverse — 3D-3 对 M/EM 沿用同一模式。

---

## 4. Semantic Cardinality（semantic only；**DEFER** 字段）

| Relation | Cardinality |
| --- | --- |
| M → K | 0..n |
| EM → K | 0..n |
| P ↔ M | many-to-many contextual |
| P ↔ EM | many-to-many derived/contextual |
| A ↔ M | 0..n evidence associations |
| A ↔ EM | 0..n evidence associations |
| M ↔ EM | 0..n optional |

**不** 因此建立 list fields / relation tables / database。

---

## 5. Real Repository Relation Tests

### 5.1 Legendre Method candidate（P0001 / K0001 / K0002）

| 问题 | 结论 |
| --- | --- |
| Method → K 是否有稳定意义？ | **YES** — 可能依赖 K0001（Legendre）、K0002（凸函数） |
| Formal K link 对 machine 是否有价值？ | **YES**（navigation / validation）；但 Method body 已可自说明 |
| v1 是否 required？ | **NO — optional** |
| P0001 是否进入 Method source relation？ | **NO** — P0001 为 **application example**，非 intrinsic Method metadata |

### 5.2 Rank-one spectral construction（P0002 / A000001）

| 问题 | 结论 |
| --- | --- |
| M → K？ | **Optional** — 特征值/特征向量相关 K（未来具体 ID 待定） |
| P0002 是否 Method source relation？ | **NO** — Problem 是 **explanatory example**；A000001 为 historical evidence，非 M↔P structured link |
| 无 A↔M link 是否损害 Attempt 保真？ | **NO** — Attempt body 完整 |

### 5.3 Omitted nonzero verification（EM candidate）

| 问题 | 结论 |
| --- | --- |
| 是否必须绑定单一 K ID？ | **NO** — 跨特征向量/函数/矩阵/核构造；**0..n optional** |
| K relation 是否 identity？ | **NO** — mechanism 跨 domain |

### 5.4 A000001 / A000002

| 问题 | 结论 |
| --- | --- |
| 无 A↔M / A↔EM structured link 是否损坏 Frozen Attempt？ | **NO** |
| A↔M / A↔EM 是否 3D-4M/E Schema blocker？ | **NO — DEFER** |

---

## 6. Legacy EM001–EM005 Governance

**3D-3 结论（不修改 `09_长期记忆/错题与错误模式.md` 文件）：**

* Legacy EM001–EM005 = **LEGACY NON-AUTHORITATIVE HYPOTHESES**；  
* **≠** Formal Error Mode Objects；  
* **不得** 作为 production EM source、relation SoT 或 migration 依据；  
* 正式 migration → **DEFER**（3D-4E+ / post-Pilot）。

**RECOMMEND（未执行）：** 未来可在 legacy 文件顶栏加一句 non-authoritative warning（需明确授权）。

---

## 7. Method / Error Mode Track Split（**CLOSED**）

| Track | Next | Status |
| --- | --- | --- |
| **Method** | **3D-4M** Minimal Candidate Schema | **READY** — 有 Method-worthy candidates（Legendre path；rank-one spectral） |
| **Error Mode Schema** | **3D-4E** Minimal Candidate Schema | **DONE** — 6-field Candidate；**NOT FROZEN** |
| **Error Mode Pilot** | **3D-5E** Real Object Pilot | **WAITING FOR REAL ERROR EVIDENCE** |

**不要** 为流程对称强行制造 EM Pilot。

---

## 8. Relation Requirements for 3D-4（非 YAML）

### 8.1 Method v1（3D-4M 输入）

若保存 K relation：

* **Owner：** Method-side only；  
* **Optional：** yes；not required for every Method；  
* **Not identity：** K mapping 变化 ≠ new Method identity；  
* **Reverse：** K→Methods **Derived only**；  
* **Field names：** **DEFER 3D-4M**。

### 8.2 Error Mode v1（3D-4E 输入）

若保存 K relation：

* **Owner：** Error Mode-side only；  
* **Optional：** yes；0..n；  
* **Not identity：** ≠ EM identity core；  
* **Reverse：** K→EM **Derived only**；  
* **Field names：** **DEFER 3D-4E**。

### 8.3 Explicitly DEFER from v1 core

P↔M · P↔EM · A↔M · A↔EM · M↔EM · Generic Relation Object · Knowledge Graph · Association files · ID · directory · lifecycle · Validator · Indexer integration。

---

## 9. Decision Summary

### 9.1 CLOSED 项

Relation type taxonomy · K↔M semantics & SoT · K↔EM semantics & SoT · P↔M · P↔EM · A↔M · A↔EM · M↔EM · Static/Evidence/Derived boundary · Relation identity independence · Reverse lookup policy · No bidirectional duplicated SoT · Generic Relation Object **REJECT** · Frozen K/P/A safety · Method/EM track split · EM identity normalization

### 9.2 Frozen K/P/A Safety（**CONFIRMED**）

Knowledge v1 · Problem v1 · Attempt v1 — **未修改**；本 Contract **可在不修改 Frozen Schema** 前提下推进 3D-4M/E。

### 9.3 Non-Goals（确认）

* 未创建 M/EM production object · Relation object · Knowledge Graph  
* 未设计 relation YAML 字段名 · 未创建 Association Layer  
* 未修改 Workspace / Validators · 未迁移 legacy EM  

---

# Phase 3D-4M — Method Minimal Candidate Schema

**状态：** CANDIDATE · **NOT FROZEN**（2026-08-19）  
**范围：** Method Schema v1 **Minimal Candidate** 字段与 identity / body / relation 表示。  
**正式 Method Schema authority：** 尚不存在。不得写入 `元数据规范.md`。

---

## 1. Design Principles（**CLOSED**）

Semantic necessity > metadata completeness  
Machine-readable necessity > documentation convenience  
YAGNI > future speculation  
Body content > unnecessary YAML  
Single Source of Truth > duplicated relation convenience  
Consistency with Frozen K/P/A > inventing a new convention without reason

**Candidate 不是 Frozen。** 3D-5M Pilot 可暴露缺口；Freeze 前允许 Candidate 修订。

---

## 2. Existing Static-Object Conventions Reviewed

| Object | Identity | Required core | Lifecycle | Relation |
| --- | --- | --- | --- | --- |
| **Knowledge v1 Frozen** | `^K\d{4}$`；sentinel `K0000`；YAML `id` 权威 | `schema_version` · `id` · `type` · `title` · `status` · `created` · `updated` | `draft` / `reviewed` / `archived` | `prerequisites` / `related`（K↔K） |
| **Problem v1 Frozen** | `^P\d{4}$`；sentinel `P0000` | 上列 + `knowledge`（lifecycle-dependent）· `parts`（optional） | **同一 enum** | `knowledge` = Problem → K SoT |
| **Attempt v1 Frozen** | `^A\d{6}$`；sentinel `A000000` | `schema_version` · `id` · `type` · `problem` · `outcome` · `attempted_at` | **无** `status`（Evidence） | `problem` + optional `part` |

**共享 Static convention（K/P）：** `schema_version: 1`（整数）· YAML `id` 权威 · `type` 字面量 · `title` 非空 · `status` 三值 lifecycle。  
**Attempt 例外合理：** Evidence ≠ Static；Method **跟随 K/P Static**，不跟随 Attempt 的 no-title / no-status。

**COMMON CONVENTION OBSERVED：** `schema_version` · `id` · `type` · `title` · `status`。  
**CommonStaticObjectSchema：** **不创建**（等 3D-4E 后再判断是否提炼）。

---

## 3. Candidate Identity Contract

| 项 | Candidate |
| --- | --- |
| **Format** | `M` + 4 位数字（与 K/P 一致；Method 是 curated static object，预期规模接近 K/P，不采用 Attempt 六位） |
| **Regex** | `^M\d{4}$` |
| **Sentinel** | `M0000` — 仅模板 / schematic；**不得**分配给真实 Method |
| **First real** | `M0001` |
| **Authority** | YAML `id` 为 **authoritative identity**；filename 为 operational convention，**不是**第二份 identity |
| **Stability** | 正式分配后原则上永久；改 title / 文件名 / 目录 / Knowledge 列表 **不**改 ID |
| **禁止编码** | Knowledge、domain、category、Problem、difficulty、数学领域（禁止 `LA-M001` 等） |

**Method identity（语义，非 YAML）：** Stable Mathematical Intent + Stable Reasoning / Operative Mechanism（3D-1）。  
YAML `id` 是机器身份句柄；**title / knowledge 不是 identity core**。

---

## 4. Candidate Field Decision Table

| Field / Concept | Decision | Required? | Type candidate | Reason | SoT role | Body alternative? | Pilot needed? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `schema_version` | **KEEP** | yes | integer `1` | K/P/A 统一 schema evolution | Schema version | no | no |
| `id` | **KEEP** | yes | `^M\d{4}$` | 稳定 opaque identity | Identity | no | uniqueness in Pilot |
| `type` | **KEEP** | yes | literal `method` | structured-object consistency | Discriminator | no | no |
| `title` | **KEEP** | yes | 非空 string（trim） | 人类/索引导航；无 title 只能猜 filename/heading | Human navigation；**≠ identity** | heading 不够稳定 | title 改写是否误拆 ID |
| `status` | **KEEP** | yes | `draft`/`reviewed`/`archived` | Static curated；复用 K/P lifecycle | Object lifecycle | no | draft→reviewed 摩擦 |
| `knowledge` | **KEEP** | **optional** | `list[str]` of `^K\d{4}$` | 3D-3 M→K intrinsic static；复用 Problem 字段名 | Method-side SoT | body mention ≠ structured | mapping 有用性 |
| `aliases` | **DEFER** | — | — | 无真实多名称检索需求；Problem 亦 DEFER aliases | — | body | 若 Pilot 出现稳定别名再评 |
| `created` | **DEFER** | — | — | K/P 有治理意义，但 Method 尚无 indexer/审计消费；不机械复制撑字段数 | — | git / 正文 | Freeze 前可再评 K/P 一致性 |
| `updated` | **DEFER** | — | — | 同上；mtime ≠ source field | — | git | 同上 |
| `tags` / `category` / `domain` | **DROP** | — | — | taxonomy 垃圾桶；K 已排除 tags；P `domain` DEFER（可由 K 派生） | — | Knowledge relation / Derived | no |
| `difficulty` | **DROP** | — | — | 非 Method 固有；易滑向 Derived | — | — | no |
| `applicability` | **BODY ONLY** | — | — | 3D-1 语义重要；当前消费是人类理解，无机器查询需求 | body | **yes** | body 能否写清 When |
| `preconditions` | **BODY ONLY** | — | — | 数学条件自由文本；难稳定枚举 | body | **yes** | 同上 |
| knowledge prerequisites（第二字段） | **DROP** | — | — | 与 `knowledge` 重复真相 | — | — | no |
| `intent` | **BODY ONLY** | — | — | identity core ≠ YAML；无机器消费者；Validator 不能判数学同一性 | body | **yes** | Content Review |
| `mechanism` | **BODY ONLY** | — | — | 多行公式/图示；单行 YAML 错误层级 | body | **yes** | Content Review |
| `procedure` / `steps` | **BODY ONLY** | — | — | skeleton 在 Markdown 列表自然；无逐步 machine 需求 | body | **yes** | Content Review |
| `variants` | **BODY ONLY** | — | — | 3D-1 variant 不新 identity；无独立 machine identity | body | **yes** | no |
| `examples` | **BODY ONLY** | — | — | body 可提 P0001；≠ structured P↔M | body | **yes** | 勿误当成 relation |
| `problems` / `applies_to` / `example_problems` | **DEFER** | — | — | 3D-3 P↔M DEFER | — | body mention | no |
| `attempts` / `used_in` | **DEFER** | — | — | 3D-3 A↔M DEFER | — | Attempt body | no |
| `error_modes` / `common_errors` | **DEFER** | — | — | 3D-3 M↔EM DEFER | — | EM body | no |
| `mastery` / `proficiency` / `success_rate` / `usage_count` / `last_used` / `weakness` / `review_priority` / `recommendation` / `confidence` / `personal_score` / `difficulty_for_user` | **DROP** | — | — | Phase 3E Derived；禁止进入 Method source | — | — | no |

---

## 5. Required / Optional / Body / Excluded / Deferred

**Required（5）：** `schema_version` · `id` · `type` · `title` · `status`

**Optional（1）：** `knowledge`

**Total Candidate top-level fields：6**

**BODY ONLY（语义重要，不进 YAML）：** Applicability · Intent · Mechanism · Procedure Skeleton · Mathematical Preconditions · Variants · Examples（含 Problem 文档引用）

**DROP：** tags · category · domain · difficulty · knowledge_prerequisites（第二套）· 全部 Derived/personal 字段

**DEFER：** aliases · created · updated · P↔M / A↔M / M↔EM structured fields · filename-equals-id Validator 规则 · CommonStaticObjectSchema · Error Mode 目录

---

## 6. Field Contracts

### 6.1 `schema_version`

整数 `1`。不使用 `v1` / `"1"` / `1.0`。与 Frozen K/P/A 一致。

### 6.2 `id`

见 §3。改 title **不**产生新 Method。Intent/Mechanism 实质变化才考虑新 M ID（Content Review，非 Validator）。

### 6.3 `type`

字面量 `method`。不得使用 `procedure` / `technique` / `方法`。

### 6.4 `title`

* **required** 非空（trim 后）  
* **≠ identity**；改 title 保留 M ID  
* 人类可读短名（如「Legendre 经典反解代回」），完整机制不放 title

### 6.5 `status` — 复用 K/P enum，**不**发明 Method-only 状态

| 值 | 含义（Candidate） |
| --- | --- |
| `draft` | 内容/Metadata 可调整；非正式引用基线 |
| `reviewed` | Content Review 已确认 Method-worthy；Metadata 满足 Candidate 规则；可作为稳定参考 |
| `archived` | 历史保留；M ID 不回收 |

**不使用：** `candidate` / `stable` / `deprecated` / `verified`。  
**不是** Attempt outcome，不是使用次数。

Validator **不能**判断 Intent/Mechanism/Reusability；那是 Content Review。

### 6.6 `knowledge` — Method → Knowledge

* **表示：** supporting Knowledge（depends on / uses）；**不是** Method identity  
* **SoT：** Method-side only（3D-3）  
* **Reverse：** K → Methods **Derived only**  
* **Cardinality：** 0..n  
* **Lexical：** 复用 Frozen Knowledge ID `^K\d{4}$`；字段名 **`knowledge`**（与 Problem 同一 relation vocabulary；不另造 `knowledge_refs` / `depends_on`）  
* **Semantic vs Problem：** Problem `knowledge` = directly engaged；Method `knowledge` = procedure 所依赖的 supporting Knowledge。**同一字段名、同一 ID 词法；语义 owner 不同。** 不得因此改 Frozen Problem Schema。  
* **Knowledge 列表变化 ≠ 新 Method**（Intent + Mechanism 未变）

#### Optional omission semantics（Canonical）

| 写法 | 含义 |
| --- | --- |
| **省略 `knowledge`** | **canonical** — 当前 **未断言** Method→K source relation |
| `knowledge:` 含 ≥1 合法 K ID | 已断言 supporting Knowledge |
| `knowledge: []` | **不允许** |
| 空键 `knowledge:` / `null` | **不允许** |

**与 Problem 的差异（有意的）：** Problem `reviewed` 必须写出 `knowledge`（`[]` 表示 mapping 已审核且 inventory 无合适 target）。Method 的 K relation **永不 required**；「无关系」用 **omit**，不必用空数组表达「mapping 已完成」。  
draft / reviewed **同一** omission 规则（避免 lifecycle 耦合制造第二套空值语义）。

---

## 7. Empty-value / Unknown-field Policy（Candidate）

**Empty-value：** 禁止 `title: ""`、`status: null`、`knowledge: []`、无意义空键。Optional 无数据 → **omit**。

**Unknown-field：** Candidate top-level = **closed set**（上述 6 字段）。未知 key → **未来 Schema violation**。本轮 **不**实现 Validator。不允许「先写着以后用」。

---

## 8. Markdown Body Convention

Body = 自然 curated 数学内容（可含 LaTeX、矩阵、图、例题）。**不得**为机器解析把机制压成单行 YAML。

**推荐（非强制）轻量 headings：**

```text
## 适用场景
## 数学意图
## 核心机制
## 操作骨架
## 数学前提
## 典型例子
## 变体 / 边界
```
**Fixed headings required：NO。** 未来 Validator **不得**要求固定标题。

**Content Review 应能识别**（语义成分，非 YAML key）：Applicability · Intent · Mechanism · Procedure Skeleton。

Body 提及 P/A ID = documentation example，**≠** structured relation。

---

## 9. File / Directory Recommendations（**不创建**）

| 项 | Recommendation |
| --- | --- |
| **Filename** | operational：`<M-ID>.md`（如 `M0001.md`） |
| **Identity** | YAML `id` 权威；filename mismatch **不**自动 = identity mismatch（吸取 P0001 legacy） |
| **filename == id Validator-required** | **DEFER** |
| **Future root** | **`12_方法库/`** |
| **Error Mode 目录** | **不在本轮决定**（3D-4E） |

**为何不是 `03_方法库/`：** `03_参考资料/` **已被占用**；不得插入打乱现有编号职责。  
**为何 `12_`：** 现有编号根至 `11_学习证据/`；下一空位；与 Knowledge / Problem / Evidence / 参考资料 区分；中文可读；不移动已有目录。

**本轮不创建该目录、不创建任何 Method 文件。**

---

## 10. Schematic Candidate YAML

> **SCHEMATIC EXAMPLE — NOT A REAL METHOD OBJECT**  
> `id: M0000` 为 sentinel。**不得**据此创建 `M0001.md` 或任何 production Method。

**Draft · 无 Knowledge relation：**

```yaml
---
schema_version: 1
id: M0000
type: method
title: （示意标题，非真实 Method）
status: draft
---
```

**Draft · 有 Knowledge relation：**

```yaml
---
schema_version: 1
id: M0000
type: method
title: （示意标题，非真实 Method）
status: draft
knowledge:
  - K0001
  - K0002
---
```

---

## 11. Validator vs Content Review（Candidate 边界）

**未来 Validator 可检查：** ID shape · sentinel · field set · status enum · Knowledge ID 词法与存在性 · uniqueness  

**Validator 不能检查：** Intent / Mechanism 是否稳定且可复用；两 Method 是否数学同一；Applicability 是否写对。

---

## 12. Pilot Readiness

### 12.1 PRIMARY PILOT CANDIDATE

**P0001 / K0001 — 经典 Legendre：反解梯度/导数映射后代回 $px-f(x)$**

* 四问（When/Intent/Mechanism/Skeleton）已在仓库正文完整存在  
* 跨凸分析/优化的 Intrinsic Reusability 清晰  
* M→K 自然（K0001、可能 K0002）  
* body 可独立成篇，不依赖单题偶然细节  

### 12.2 SECONDARY PILOT CANDIDATE

**A000001 / P0002(b) — 左右特征结构的秩一对象构造**

* 3D-1 已判 METHOD-WORTHY（Route B）  
* 适用族（Sylvester / 交换子谱）可叙述，但仓库仅一题实例  
* Knowledge inventory 尚无对应线性代数条目 → 预期 **omit `knowledge`**（合法 optional）  
* 不宜作为 **第一个** Pilot：勿为填 `knowledge` 字段而硬绑不存在的 K  

**禁止：** 为 Schema coverage 制造 Method。

### 12.3 Reality Checks（3D-5M 运行，本轮不执行）

1. Expressiveness  
2. Ambiguity  
3. Redundancy  
4. Recording Friction  
5. Body-vs-Metadata boundary  
6. Knowledge relation usefulness  
7. Identity stability（改 title / 增 K ≠ 新 ID）  
8. Future Validator usability  
9. Future Workspace usability  

### 12.4 Track status

**3D-5M Real Method Object Pilot → READY**（await 授权；不自动开始）

Error Mode Track：**不变** — 3D-4E READY；3D-5E WAITING FOR REAL ERROR EVIDENCE。

---

## 13. Decision Summary

| 项 | 状态 |
| --- | --- |
| Identity Contract | **CLOSED**（Candidate） |
| Required / Optional | **CLOSED** |
| M→K representation | **CLOSED**（optional `knowledge`；omit ≠ `[]`） |
| Body vs YAML | **CLOSED** |
| Derived / P / A / EM fields | **DROP / DEFER** as table |
| Candidate Freeze | **NOT FROZEN** |
| Production Method objects | **NO** |
| CommonStaticObjectSchema | **NO** |

---

# Phase 3D-5M — Real Method Object Pilot

**状态：** DONE（2026-08-19）  
**性质：** Controlled Real-Object Pilot；**Candidate Schema fixed during experiment**（未修改 6-field Candidate）。  
**Method Schema：** CANDIDATE · **NOT FROZEN** · 非 Validated Registry · 未进入 Workspace。

---

## 1. Pilot Infrastructure

| 项 | 结果 |
| --- | --- |
| **Method root created** | YES — `12_方法库/`（`12_` 未被占用；`03_` 已被 `03_参考资料/` 占用） |
| **Sub-workflow dirs** | **未创建**（status 仅 YAML） |
| **Candidate fields modified** | **NO** |

---

## 2. Pilot 1 — M0001（Primary）

### 2.1 Source & Qualification

| 项 | 内容 |
| --- | --- |
| **Source** | P0001 研究叙述 + K0001 §5 经典 Legendre 写法 |
| **Promotion re-check** | When ✓ Intent ✓ Mechanism ✓ Skeleton ✓ Reusability ✓ Independence ✓ |
| **Decision** | **PRIMARY PILOT QUALIFIED** → **KEEP AS PILOT** |

**抽象：** 在光滑严格凸且导数/梯度映射可逆的像集内，由 $p=f'(x)$ 或 $p=\nabla f(x)$ 反解 $x(p)$，再代回 $p\cdot x-f(x)$ 计算 $f^{\ast}(p)$。

### 2.2 Object

| 项 | 值 |
| --- | --- |
| **Path** | `12_方法库/M0001.md` |
| **title** | 经典 Legendre 反解代回 |
| **status** | `draft` |
| **knowledge** | `[K0001]` |
| **Extra YAML** | **NONE** |

**K0001 理由：** 经典 Legendre 写法是 K0001 内嵌 procedure；无 K0001 则 Method 失去所操作的变换对象。K0002 为 K0001 前置，非本 procedure 的直接 intrinsic 依赖 → **未写入**。

**未盲抄 P0001.knowledge：** P0001 含 K0001+K0002（directly engaged）；Method 只链 procedure 核心 K0001。

### 2.3 Reality Review（7 项）

| 项 | 结论 |
| --- | --- |
| **A. Expressiveness** | PASS — body 可独立表达 When/Intent/Mechanism/Skeleton |
| **B. Metadata Boundary** | PASS — 5 required + optional `knowledge` 足够；数学在 body |
| **C. Knowledge Relation** | PASS — 单 K 链有价值；非 identity |
| **D. Identity Stability** | PASS — 改 title / 增 K0002 / 换 example 不改变 M0001 identity |
| **E. Recording Friction** | **NONE** — 无信息必须进 YAML 而 Candidate 无法表达 |
| **F. Redundancy** | PASS — 不复制 K0001 全文或 P0001 解答 |
| **G. Schema Pressure** | **NONE actionable** |

### 2.4 Schema Pressure（M0001）

| 概念 | Class | 证据 | 3D-6M |
| --- | --- | --- | --- |
| `created` / `updated` | **P4 Symmetry** | draft 可表达「未 review」；无 provenance 丢失 | 继续 omit |
| `status: draft` | — | 自然表达 Pilot 未 Content Review | 保留 |
| `title` | — | 稳定导航；改 wording 仍同一 Method | 保留 |

---

## 3. Pilot 2 — M0002（Secondary）

### 3.1 Source & Re-qualification

| 项 | 内容 |
| --- | --- |
| **Source** | A000001 / P0002(b) 构造 $X_{ij}=u_i v_j^{\mathsf T}$ |
| **Promotion re-check** | When ✓ Intent ✓ Mechanism ✓ Skeleton ✓ Reusability (Route B) ✓ Independence ✓ |
| **Decision** | **SECONDARY PILOT QUALIFIED** → **KEEP AS PILOT** |

3D-1 METHOD-WORTHY 判断 **经 Pilot 确认**；非自动 PASS。

### 3.2 Object

| 项 | 值 |
| --- | --- |
| **Path** | `12_方法库/M0002.md` |
| **title** | 左右特征结构的秩一对象构造 |
| **status** | `draft` |
| **knowledge** | **omit**（无正式特征值/特征向量 K；不得为填 relation 新建 K） |
| **Extra YAML** | **NONE** |

### 3.3 Reality Review（7 项）

| 项 | 结论 |
| --- | --- |
| **A. Expressiveness** | PASS |
| **B. Metadata Boundary** | PASS — **omit `knowledge`** 合法且自然 |
| **C. Knowledge Relation** | N/A presence；**omission case 已验证** |
| **D. Identity Stability** | PASS |
| **E. Recording Friction** | **NONE** |
| **F. Redundancy** | PASS — 不复制 A000001 历史叙述 |
| **G. Schema Pressure** | **NONE actionable** |

---

## 4. Cross-Pilot Review

| 主题 | 结论 |
| --- | --- |
| **6-field fit** | **PILOT SUPPORTS CURRENT CANDIDATE** |
| **Body boundary** | Intent/Mechanism/Skeleton 均在 body；YAML 仅 identity + lifecycle + optional K |
| **K relation** | M0001 presence；M0002 omission；均符合 3D-4M omit 语义 |
| **Identity stability** | title/K/example 变化 ≠ 新 ID；mechanism 实质变化 = 新 Method |
| **Same/Variant** | M0001 一元/多元 = body variant，同一 M0001 |
| **Atomicity** | 两 Pilot 均为单一 stable procedure，非 Solution 串联 |
| **Workspace** | Pilot **未** 进入 Indexer/Check/Validator |

### Schema Pressure Summary

| Class | Count |
| --- | --- |
| **P1 Source Truth Loss** | 0 |
| **P2 Machine Need** | 0 |
| **P3 Convenience** | 0 |
| **P4 Symmetry** | 1（`created`/`updated` — 非阻塞） |
| **P5 Speculative** | 0 |

**Candidate outcome:** **PILOT SUPPORTS CURRENT CANDIDATE**（仍 **NOT FROZEN** → 3D-6M）

### Objects Kept / Rejected

| ID | Decision |
| --- | --- |
| **M0001** | KEEP AS PILOT |
| **M0002** | KEEP AS PILOT |

**Rejected:** NONE

**Next real ID if authorized:** `M0003`

---

# Phase 3D-6M — Method Final Review

**状态：** DONE（2026-08-20）  
**性质：** Pre-Freeze Decision Gate；**不**修改 Candidate 字段集合；**不** Freeze Schema。  
**输入：** 3D-1 Semantic · 3D-3 Relation · 3D-4M Candidate · 3D-5M Pilot Evidence（`M0001` · `M0002`）

---

## 1. Review Inputs

| 来源 | 用途 |
| --- | --- |
| **3D-1** | Method identity · granularity · atomicity（**CLOSED**，不重开） |
| **3D-3** | M→K optional SoT · P↔M / A↔M / M↔EM **DEFER**（**CLOSED**） |
| **3D-4M** | 6-field Candidate baseline |
| **3D-5M** | `12_方法库/M0001.md` · `M0002.md`；P0001 · P0002 · A000001 · K0001 复核一致 |
| **元数据规范.md** | Frozen K/P/A authority（**未修改**） |

**Pilot 复核：** M0001/M0002 YAML 仅含 Candidate 6 字段；body 独立可读；与 3D-5M 报告 **一致**。

---

## 2. Final Field Decisions

| Field / Concept | v1 Decision |
| --- | --- |
| `schema_version` | **KEEP** — integer `1` |
| `id` | **KEEP** — `^M\d{4}$` · `M0000` sentinel · YAML authoritative |
| `type` | **KEEP** — literal `method` |
| `title` | **KEEP** — required · non-empty · **≠ identity** |
| `status` | **KEEP** — `draft` / `reviewed` / `archived`（复用 K/P Static lifecycle） |
| `knowledge` | **KEEP** — optional · 0..n · omit = no formal M→K · `knowledge: []` **invalid** |
| `created` | **DROP FROM v1** — 3D-5M 无 source-truth loss；`status` 足够；P4 only |
| `updated` | **DROP FROM v1** — 同上；filesystem mtime ≠ source semantic |
| `aliases` | **DEFER TO FUTURE VERSION** — 无真实多名称需求 |
| `tags` / `category` / `domain` / `difficulty` | **DROP FROM v1** |
| Applicability · Intent · Mechanism · Skeleton · Preconditions · Variants · Examples | **BODY ONLY** |
| `problems` / `attempts` / `error_modes` / … | **DEFER TO RELATION / DERIVED LAYER**（3D-3） |
| Derived / personal fields | **DROP FROM v1**（Phase 3E） |

**6-field Candidate：** **KEEP AS-IS** — **CHANGE REQUIRED：NO**

**Unknown top-level field：** closed set → future Schema violation。  
**Fixed body headings：** **NOT REQUIRED**。

---

## 3. Pilot Evidence Summary

| Pilot | 验证分支 |
| --- | --- |
| **M0001** | `knowledge` **present** `[K0001]` · `status: draft` · rich body · 一元/多元 variant 同 ID |
| **M0002** | `knowledge` **omitted** · 不同数学机制 · 无 formal K 时合法 omit |

**Pilot sufficiency：** **YES** — 覆盖 presence + omission · title · status · body · identity；**不**需 synthetic `reviewed`/`archived` Pilot。

**Structural compatibility（Freeze 后）：** M0001/M0002 **compatible** — 3D-7M 仅需 formal normalization/review，不应大改 source。

---

## 4. Schema Pressure Resolution

| Class | 3D-5M | 3D-6M Resolution |
| --- | --- | --- |
| **P1 Source Truth Loss** | 0 | **0 unresolved** |
| **P2 Machine Need** | 0 | **0 unresolved** |
| **P3 Convenience** | 0 | non-blocking |
| **P4 Symmetry** | 1 (`created`/`updated`) | **CLOSED** → **DROP FROM v1** |
| **P5 Speculative** | 0 | non-blocking |

**knowledge omission semantics：** **CLOSED** — omit = 未断言 formal M→K；≠ unknown · ≠ validator gap · ≠ `[]`。

**created/updated：** 从 3D-4M **DEFER** → 3D-6M **DROP FROM v1**（非永久禁止；Schema v2 可再评）。

---

## 5. Freeze Readiness Checklist

| 项 | Result |
| --- | --- |
| Semantic Contract CLOSED | **YES** |
| Relation Contract CLOSED | **YES** |
| Candidate minimal | **YES** |
| Real Pilot count ≥1 | **YES**（2） |
| Structural branches useful | **YES** |
| P1 Schema Pressure = 0 | **YES** |
| P2 Schema Pressure = 0 | **YES** |
| Body-vs-metadata boundary stable | **YES** |
| Knowledge relation stable | **YES** |
| Identity stable | **YES** |
| Frozen K/P/A unaffected | **YES** |
| Validator path clear | **YES** |
| Authority transition clear | **YES** |

---

## 6. Final Decision

**FREEZE-READY**

| 项 | 状态 |
| --- | --- |
| **Method Schema** | CANDIDATE · **NOT FROZEN** |
| **Candidate modified this phase** | **NO** |
| **Candidate outcome** | **PILOT SUPPORTS CURRENT CANDIDATE** |
| **Method Track next** | **3D-7M Method Schema v1 Freeze → READY**（await 授权） |
| **M0001 / M0002 modified** | **NO** |

**Validator future scope（不创建）：** 可检 ID · field set · enum · K ID 词法/存在 · uniqueness；**不可**检 Intent/Mechanism/数学正确性/reusability。

**Workspace future path：** Freeze + Validated Registry 后可支撑 ID · Title · Status · Knowledge · Source Path 描述性视图 — **CLEAR**。

**Authority transition：** 3D-7M 迁入 `元数据规范.md`；本文件降为 design history / rationale — **路径清楚**。

---

# Phase 3D-7M — Method Schema v1 Freeze

**状态：** DONE（2026-08-20）  
**性质：** Schema Freeze + Authority Transition + Governance Propagation。

| 项 | 结果 |
| --- | --- |
| **Final Candidate** | **AS-IS accepted**（6-field closed set） |
| **Method Schema v1** | **FROZEN** |
| **Normative authority** | `元数据规范.md` §9 |
| **Design history** | 本文件（3D-0–3D-6M + 本 section） |
| **Source root** | `12_方法库/` |
| **Real sources** | `M0001.md` · `M0002.md`（`status: draft`；structurally compatible） |
| **Source modified** | **NO** |
| **Method Validator** | **NOT YET IMPLEMENTED** |
| **Validated Registry** | **NOT YET AVAILABLE** |
| **Workspace integration** | **NOT YET ENABLED** |
| **Next** | **3D-8M Method Validator v1 → READY** |

**Pilot → Frozen transition：** M0001/M0002 由 Candidate Pilot 转为 **Frozen-Schema Method Source Objects**；**不是** Validated Registry entries（须等 3D-8M）。

完整 Frozen contract 见 **`元数据规范.md` §9**（不在此复制）。

---

# Phase 3D-8M — Method Validator v1

**状态：** DONE（2026-08-20）  
**性质：** Frozen §9 的 mechanical validation layer；read-only。

| 项 | 结果 |
| --- | --- |
| **Authority** | `元数据规范.md` §9 + §9.12A/B |
| **Implementation** | `tools/method_validator/` |
| **CLI** | `python -m tools.method_validator check` · `check-file` |
| **Dependency** | Knowledge Validator → Validated Knowledge Registry |
| **Registry** | `dict[str, MethodDocument]`；**仅 project PASS 时 AVAILABLE** |
| **Validated ≠ reviewed** | M0001/M0002：`Validator PASS` + `status: draft` |
| **Real sources** | M0001 · M0002 — project check **PASS** |
| **Workspace** | **NOT YET ENABLED**（3D-9M） |
| **Next** | **3D-9M Method Workspace Integration → READY** |

**Validator 边界：** 只检 Schema + K reference integrity；**不**检数学正确性、可复用性、body headings。

---

# Phase 3D-9M — Method Workspace Integration

**状态：** DONE（2026-08-20）  
**性质：** Validated Method Registry → WorkspaceSnapshot → Derived Views。

| 项 | 结果 |
| --- | --- |
| **Workspace version** | v1.1 → **v1.2**（Validated Method Source Integration） |
| **Input** | Method Validator project PASS documents only |
| **Raw parse of `12_方法库/`** | **NO** |
| **Generated** | `09_长期记忆/自动索引/方法索引.md` |
| **Stats** | Method total + draft/reviewed/archived counts |
| **K→Methods reverse render** | **DEFER**（知识索引无既有 reverse-navigation 列） |
| **P↔M / A↔M** | **not created** |
| **Learning / usage** | **not created** |
| **Method Track** | **COMPLETE** |
| **Phase 3D** | **IN PROGRESS**（Error Mode pending） |
| **Next** | **3D-5E**（WAITING FOR REAL ERROR EVIDENCE） |

**Orchestration order：** Knowledge → Problem → Attempt → Method → snapshot（≠ semantic graph；Method 语义只依赖 Knowledge）。

---

# Phase 3D-4E — Error Mode Minimal Candidate Schema

**状态：** CANDIDATE · **NOT FROZEN**（2026-08-20）  
**范围：** Error Mode Schema v1 **Minimal Candidate** 字段、identity / body / relation 表示、Production Promotion Gate（governance，非 YAML）。  
**正式 Error Mode Schema authority：** 尚不存在。不得写入 `元数据规范.md`。

**输入：** Phase 3D-2 Error Mode Semantic Contract · Phase 3D-3 Cross-Object Relation Contract · Frozen Method Schema §9（**对照 only，非机械复制**）。

---

## 1. Design Principles（**CLOSED**）

Semantic necessity > metadata completeness  
Machine-readable necessity > documentation convenience  
YAGNI > future speculation  
Body content > unnecessary YAML  
Single Source of Truth > duplicated relation convenience  
Static Object vs Evidence Event boundary > diagnostic database convenience  
Consistency with Frozen K/P/M observed conventions > inventing Error-Mode-only lifecycle without reason

**Candidate 不是 Frozen。** 3D-5E Pilot 可暴露缺口；Freeze 前允许 Candidate 修订。

### 1.1 Schema Eligibility vs Production Object Eligibility（**CLOSED**）

| 层次 | 3D-4E 解决？ | 含义 |
| --- | --- | --- |
| **A. Schema Eligibility** | **YES** | 哪些 metadata **适合** Error Mode static object（Candidate field set） |
| **B. Production Object Eligibility** | **NO — 3D-5E** | 是否 **允许创建** 第一个 formal Error Mode source object |

两者 **完全不同**。Candidate Schema 存在 **不** 授权 production 创建。

### 1.2 Candidate Governance Rule：`draft` ≠ hypothesis（**CLOSED**）

`status: draft` **绝不能** 表示「这只是猜测，先建 EM 看看」。

**规则：** 正式 Error Mode source object **一旦创建**，必须 **已经通过 Production Promotion Gate**（Semantic Qualification + ≥1 真实 failure Evidence）。`status` **只** 描述一个 **已经 qualified** 的正式 Error Mode 处于何种 **Content Review lifecycle**。

| 值 | **不是** | **是** |
| --- | --- | --- |
| `draft` | unverified hypothesis · 尚无 Evidence | qualified EM 的内容/metadata 仍可调整 |
| `reviewed` | evidence 首次变真实 | Content Review 已确认 EM-worthy |
| `archived` | Error Mode 被证伪 | 历史保留；EM ID 不回收 |

**禁止** Error-Mode-only lifecycle：`suspected` · `confirmed` · `observed` · `frequent` · `active` · `inactive` · `evidence_status` · `confidence_status`。

Production Object 是否允许创建 → **3D-5E Promotion Gate**（creation governance），**不由** `status` 表达。

### 1.3 Zero-Evidence Production Rule（**CLOSED**）

Zero real failure Evidence → **永远不得** 进入 3D-5E production Pilot；不得分配 `EM0001+`；不得创建 source file。

可保留为：**Legacy Hypothesis** · **Pedagogical Note** · **Error-Mode-Worthy Candidate**（semantic only）。

---

## 2. Existing Static-Object Conventions Reviewed

| Object | Identity | Required core | Lifecycle | Relation |
| --- | --- | --- | --- | --- |
| **Knowledge v1 Frozen** | `^K\d{4}$`；sentinel `K0000` | `schema_version` · `id` · `type` · `title` · `status` · `created` · `updated` | `draft` / `reviewed` / `archived` | `prerequisites` / `related` |
| **Problem v1 Frozen** | `^P\d{4}$`；sentinel `P0000` | 上列 + `knowledge`（lifecycle-dependent）· `parts`（optional） | **同一 enum** | `knowledge` = Problem → K SoT |
| **Method v1 Frozen** | `^M\d{4}$`；sentinel `M0000` | `schema_version` · `id` · `type` · `title` · `status` · `knowledge`（optional） | **同一 enum** | `knowledge` = Method → K SoT |
| **Attempt v1 Frozen** | `^A\d{6}$`；sentinel `A000000` | Evidence fields；**无** `status` | **无** static lifecycle | `problem` + optional `part` |

**共享 Static convention（K/P/M）：** `schema_version: 1`（整数）· YAML `id` 权威 · `type` snake_case 字面量 · `title` 非空 · `status` 三值 lifecycle。

**Attempt 例外合理：** Evidence ≠ Static；Error Mode **跟随 K/P/M Static**，不跟随 Attempt。

**Independent EM decision：** Error Mode **独立审查** 每一字段；与 Method 同为 6-field 结果是 **收敛**，不是机械复制。关键差异：EM identity core（Stable Failure Mechanism + Diagnostic Pattern recognizability）**全部 BODY ONLY**；Production 创建 **必须** 有真实 failure Evidence（Method 无此硬性 gate）。

**COMMON CONVENTION OBSERVED：** `schema_version` · `id` · `type` · `title` · `status`。  
**CommonStaticObjectSchema：** **不创建**（YAGNI；3D-4E 后仍 DEFER）。

---

## 3. Candidate Identity Contract

| 项 | Candidate |
| --- | --- |
| **Format** | `EM` + 4 位数字 |
| **Regex** | `^EM\d{4}$` |
| **Sentinel** | `EM0000` — 仅模板 / schematic；**不得**分配给真实 Error Mode |
| **First real** | `EM0001`（须通过 Production Promotion Gate 后才可分配） |
| **Authority** | YAML `id` 为 **authoritative identity**；filename 为 operational convention |
| **Stability** | 正式分配后原则上永久；改 title / Knowledge 列表 / 文件名 **不**改 ID |
| **禁止编码** | Knowledge、domain、Problem、Attempt、severity、频率（禁止 `LA-EM001` 等） |

**Legacy ID isolation（**CLOSED**）：**

| Legacy | Formal v1 ID? | 机制 |
| --- | --- | --- |
| `EM001`–`EM005`（`09_长期记忆/错题与错误模式.md`） | **NO** | legacy `EM` + **3 位**数字 **不符合** `^EM\d{4}$`；仅为 **LEGACY NON-AUTHORITATIVE HYPOTHESES** |
| 未来 rename legacy → `EM0001.md` | **禁止** | rename **≠** production promotion；须 Semantic Qualification + Real Evidence + Pilot Gate |

**Error Mode identity（语义，非 YAML）：** Stable Failure Mechanism（primary identity core）；Diagnostic Pattern = Required Recognizability Criterion（**不是**并列第二 identity key）。  
YAML `id` 是机器身份句柄；**title / knowledge 不是 identity core**。

---

## 4. Candidate Field Decision Table

| Field / Concept | Decision | Required? | Type candidate | Reason | Identity role | Evidence leakage? | Body alt? | Pilot? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `schema_version` | **KEEP** | yes | integer `1` | K/P/A/M 统一 schema evolution | Schema version | no | no | no |
| `id` | **KEEP** | yes | `^EM\d{4}$` | 稳定 opaque identity；legacy 天然隔离 | Identity handle | no | no | uniqueness in Pilot |
| `type` | **KEEP** | yes | literal `error_mode` | structured-object snake_case 一致 | Discriminator | no | no | no |
| `title` | **KEEP** | yes | 非空 string（trim） | 人类/索引导航 | **≠ identity** | no | heading 不够稳定 | title 改写是否误拆 ID |
| `status` | **KEEP** | yes | `draft`/`reviewed`/`archived` | curated static；复用 K/P/M lifecycle；**≠ Evidence gate** | Content Review lifecycle | **NONE** | no | draft→reviewed 摩擦 |
| `knowledge` | **KEEP** | **optional** | `list[str]` of `^K\d{4}$` | 3D-3 EM→K intrinsic static；navigation / ref integrity / future K→EM Derived | Supporting metadata；**≠ identity** | no | body mention ≠ structured | mapping 有用性 |
| `aliases` | **DEFER** | — | — | 无真实多名称冲突 | — | no | body | 若 Pilot 出现稳定别名再评 |
| `created` | **DROP** | — | — | EM static semantics **不依赖** timestamp 作不可恢复 source truth；无 indexer/审计 consumer；**独立理由**，非因 Method DROP 而跟随 | — | no | git / 正文 | no |
| `updated` | **DROP** | — | — | 同上；mtime ≠ source field | — | no | git | no |
| `mechanism` | **BODY ONLY** | — | — | identity core ≠ YAML；需公式/推理链；Validator 不能判 mechanism 稳定性/同一性 | **Semantic core**（非 YAML） | no | **yes** | Content Review |
| `diagnostic_pattern` | **BODY ONLY** | — | — | Required recognizability；无自动 EM classifier | Recognizability criterion | no | **yes** | Content Review |
| `context` / `trigger` | **BODY ONLY** | — | — | 高度数学化；无 machine taxonomy consumer | — | no | **yes** | no |
| `manifestations` | **BODY ONLY** | — | — | instance-level symptom family；**≠ identity** | — | no | **yes** | no |
| `consequence` | **BODY ONLY** | — | — | 数学后果；自然 Markdown | — | no | **yes** | no |
| `correction` / `prevention` | **BODY ONLY** | — | — | 可有多种策略；**≠ identity** | — | no | **yes** | no |
| `examples` | **BODY ONLY** | — | — | body 可匿名化 manifestation 或 mention A ID；≠ structured relation | — | mention only | **yes** | 勿误当成 A↔EM |
| `attempts` | **DEFER** | — | — | 3D-3 A↔EM Evidence relation DEFER；EM source ≠ Evidence log | — | **YES if in YAML** | Attempt body | no |
| `evidence` / `evidence_count` / `observed_in` / `first_seen` / `last_seen` | **DROP** | — | — | historical Evidence；污染 static object | — | **YES** | Attempt / future Association | no |
| `problems` | **DEFER** | — | — | 3D-3 P↔EM DEFER；derived/contextual | — | no | body mention | no |
| `methods` / `common_errors` | **DEFER** | — | — | 3D-3 M↔EM DEFER | — | no | body | no |
| `frequency` / `recurrence_count` / `times_seen` / `occurrence_count` | **DROP** | — | — | Derived dynamic state | — | **YES** | — | no |
| `severity` | **DROP** | — | — | 依赖题目/上下文/用户；非 stable EM identity | — | no | body contextual | no |
| `confidence` | **DROP** | — | — | interpretive / personal | — | **YES** | — | no |
| `weakness` / `mastery` / `risk_score` / `probability` | **DROP** | — | — | Phase 3E Derived Learning State | — | **YES** | — | no |
| `review_priority` / `recommendation` | **DROP** | — | — | Action / Recommendation layer | — | no | Derived action | no |
| `tags` / `category` / `domain` | **DROP** | — | — | taxonomy 垃圾桶；K relation 可部分覆盖 navigation | — | no | Knowledge / body | no |

---

## 5. Required / Optional / Body / Excluded / Deferred

**Required（5）：** `schema_version` · `id` · `type` · `title` · `status`

**Optional（1）：** `knowledge`

**Total Candidate top-level fields：6**

**BODY ONLY（语义重要，不进 YAML）：** Mechanism · Diagnostic Pattern · Context/Trigger · Manifestations · Consequence · Correction/Prevention · Examples

**DROP FROM v1：** `created` · `updated` · tags · category · domain · severity · confidence · frequency · recurrence_count · last_seen · first_seen · evidence* · weakness · mastery · risk · review_priority · recommendation · 全部 Derived/personal 字段

**DEFER TO FUTURE VERSION：** `aliases`

**DEFER TO EVIDENCE / ASSOCIATION LAYER：** `attempts` · `evidence` · A↔EM · P↔EM · M↔EM structured fields · Generic Relation Object

**DEFER TO DERIVED / ACTION LAYER：** （已在 DROP 中拒绝进入 source 的 weakness / recommendation 等若未来需要，只在 Derived/Action 层实现）

---

## 6. Field Contracts

### 6.1 `schema_version`

整数 `1`。与 Frozen K/P/A/M 一致。

### 6.2 `id`

见 §3。Mechanism 实质变化 → Content Review 考虑 **新 EM ID**（非 Validator 职责）。

### 6.3 `type`

字面量 `error_mode`。不得使用 `error-mode` · `ErrorMode` · `EM`。

### 6.4 `title`

* **required** 非空（trim 后）  
* **≠ identity**；改 title 保留 EM ID  
* 人类可读短名；完整 mechanism 不放 title

### 6.5 `status`

复用 K/P/M enum（**独立审查后** exact reuse）：

| 值 | 含义（Candidate） |
| --- | --- |
| `draft` | **已 qualified** 的 EM；内容/metadata 可调整 |
| `reviewed` | Content Review 已确认 EM-worthy |
| `archived` | 历史保留 |

**Evidence role：** **NONE** — `status` 不表达 Evidence 有无或确认程度。

### 6.6 `knowledge` — Error Mode → Knowledge

* **表示：** formal related Knowledge；**不** 断言「错误一定来自 Knowledge misunderstanding」  
* **SoT：** Error Mode-side only（3D-3）  
* **Reverse：** K → Error Modes **Derived only**  
* **Cardinality：** 0..n（EM003 类跨多 K；「遗漏非零性」类亦可 0 或多 K）  
* **Lexical：** 字段名 **`knowledge`**；ID `^K\d{4}$`（复用 Method/Problem vocabulary）  
* **Knowledge 列表变化 ≠ 新 Error Mode**（Stable Failure Mechanism 未变 → same EM）

#### Optional omission semantics（Canonical）

| 写法 | 含义 |
| --- | --- |
| **省略 `knowledge`** | **canonical** — 当前 **未断言** EM→K source relation |
| `knowledge:` 含 ≥1 合法 K ID | 已断言 related Knowledge |
| `knowledge: []` | **不允许** |
| 空键 / `null` | **不允许** |

与 Method 相同：**永不 required**；无 relation 时 **omit**，不用空数组表达「mapping 已完成」。

---

## 7. Empty-value / Unknown-field Policy（Candidate）

**Empty-value：** 禁止 `title: ""` · `status: null` · `knowledge: []` · 无意义空键。Optional 无数据 → **omit**。

**Unknown-field：** Candidate top-level = **closed set**（上述 6 字段）。未知 key → **未来 Schema violation**。本轮 **不** 实现 Validator。

---

## 8. Markdown Body Convention

Body = 自然 curated 数学诊断内容。**不得** 为机器解析把 mechanism / diagnostic pattern 压成单行 YAML。

**推荐（非强制）轻量 headings：**

```text
## 出现场景
## 核心失败机制
## 可识别诊断模式
## 数学后果
## 典型表现
## 纠正与预防
## 示例与边界
```

**Fixed headings required：NO。** 未来 Validator **不得**要求固定标题。

Body 中 mention `A000123` / `P0002` / `K0001` = documentation example，**≠** structured relation。

**Validator semantic responsibility（future）：** 可检 Schema · ID · enum · K ref integrity；**不可**检 Stable Failure Mechanism 是否真实稳定 · Diagnostic Pattern 是否可重复识别 · 数学正确性。

---

## 9. Candidate YAML Schematic（**NOT REAL OBJECT**）

**SCHEMATIC ONLY · EM0000 RESERVED · NO PRODUCTION OBJECT CREATED**

Minimal（无 K relation）：

```yaml
---
schema_version: 1
id: EM0000
type: error_mode
title: "示意标题"
status: draft
---
```

With optional `knowledge`（仍 **NOT REAL**）：

```yaml
---
schema_version: 1
id: EM0000
type: error_mode
title: "示意标题"
status: draft
knowledge:
  - K0001
---
```

**禁止** 使用 legacy EM003 标题或「遗漏非零性」等真实候选作为 schematic 示例（避免暗示已 production promoted）。

---

## 10. File / Directory Recommendations（**不创建**）

| 项 | Recommendation |
| --- | --- |
| **Filename** | operational：`<EM-ID>.md`（如 `EM0001.md`） |
| **Identity** | YAML `id` 权威；filename mismatch **不**自动 = identity mismatch |
| **Future root** | **`13_错误模式库/`** — `13_` 当前 **未占用**（`12_方法库/` 已用于 Method） |
| **Directory created this phase** | **NO** |
| **Production EM object created** | **NO** |

首个真实 root / 首个 `EM0001.md` → **等 3D-5E** Production Promotion Gate 通过后再创建。

---

## 11. Production Promotion Gate（3D-5E 输入；**非 YAML**）

创建 **第一个** formal Error Mode source object **必须同时** 满足：

| # | 要求 |
| --- | --- |
| 1 | **Stable Failure Mechanism** — 可命名、可脱离单次 Attempt |
| 2 | **Stable Diagnostic Recognizability** — bounded manifestation family |
| 3 | **Independence from one Attempt accidental details** |
| 4 | **Long-term Diagnostic Value** |
| 5 | **≥1 条真实 failure Evidence** — incorrect Attempt 或 body 中可确认的 stable failure mechanism（**不是** partial · assisted · hypothetical） |

**One real failure sufficient in principle：** **YES** — 若 mechanism-generalizable 且满足 trigger · mechanism · diagnostic pattern · cross-instance recognizability（3D-2 Route B）。

**Zero evidence sufficient：** **NO** — hard gate for 3D-5E。

**Promotion Gate ≠ `status`：** 创建前 gate；创建后 `status` 只管 Content Review。

**Production Promotion Evidence ≠ YAML `evidence` field：** gate 属于 creation governance；不进入 EM source YAML。

---

## 12. Real Repository Case Audit（**无 production 动作**）

| Case | Classification | Production promoted? |
| --- | --- | --- |
| **A000001** | **NO ERROR MODE IDENTIFIED** — assisted ≠ error | **NO** |
| **A000002** | **NO ERROR MODE IDENTIFIED** — partial / 未继续 ≠ failure mechanism | **NO** |
| **Legacy EM003** | **LEGACY HYPOTHESIS · MECHANISM UNCLEAR · NO REAL EVIDENCE** | **NO** |
| **Omitted nonzero verification** | **ERROR-MODE-WORTHY CANDIDATE**（semantic）；zero real failure Evidence | **NO** |
| **P0002 scalar/domain ambiguity** | **Problem Content / Semantic Issue — NOT ERROR MODE** | **NO** |

**Same / Different test：** Candidate **不** 创建 `symptom:` identity key；surface symptom 相似但 mechanism 不同 → different EM 或 NOT EM。

**Atomicity：** One EM → one primary stable failure mechanism；**不** 创建 `mechanisms:` YAML list。

---

## 13. 3D-5E Readiness & Roadmap

| 项 | 状态 |
| --- | --- |
| **Error Mode Schema** | **CANDIDATE · NOT FROZEN** |
| **3D-5E Real Pilot** | **WAITING FOR REAL ERROR EVIDENCE**（**不是 BLOCKED**） |
| **P0 Blocker** | **NONE** — 等待 natural evidence，非架构失败 |
| **Method Track** | **COMPLETE**（不变） |

**RECOMMEND ROADMAP DECISION（不自动执行）：** 若无真实 failure Evidence，**不** 自动进入 3D-5E；用户可后续选择先推进 **Phase 3E 非-Error-Mode 部分**，或继续等待 natural evidence。

**Cross-phase（3E-0 CLOSED）：** 3D-5E WAITING **does not block** non-EM Phase 3E baseline。Phase 3E authority：`派生学习状态架构.md`。

---

## 14. Non-Goals（确认）

* 未创建 `13_错误模式库/` · 任何 EM source file · EM0001  
* 未创建 Error Mode Validator / Registry / Index  
* 未修改 Workspace v1.2 · Frozen K/P/A/M · `元数据规范.md` · `AGENTS.md` · `项目规则.md`  
* 未迁移 legacy EM001–EM005 · 未创建虚假 incorrect Attempt  
* 未创建 A↔EM / P↔EM / M↔EM YAML fields · Association Layer  

---

## 附录：仓库 Inventory（3D-0 只读）

| 位置 | 与 Method/EM 相关内容 | 性质 |
| --- | --- | --- |
| `01_知识库/` K0001/K0002 | 定义、定理、联系 | **Knowledge** |
| `02_题目库/` P0001/P0002 | 题面、解答、研究过程 | **Problem** body |
| `11_学习证据/` A000001/A000002 | 推理步骤、Assessment | **Attempt** body |
| `09_长期记忆/错题与错误模式.md` | EM001–EM005 占位 | **非正式汇总**（非 Schema object） |
| `学习证据架构.md` §4–§6 | Phase 3A 四层架构摘要 | **设计历史**（Attempt 详述以 §19–§24 为准） |
| `元数据规范.md` §9–§10 | Method/EM 待设计草案 | **非 Frozen** |
