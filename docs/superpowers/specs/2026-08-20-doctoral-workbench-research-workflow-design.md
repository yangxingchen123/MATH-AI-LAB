# MATH-AI-LAB 研究工作流、审稿与写作规范

**状态：** Candidate
**上位契约：** [博士级数学研究工作台总架构](2026-08-20-doctoral-research-workbench-design.md)
**对应版本：** v1.1、v1.7、v1.8

---

## 1. 目标

本规范定义从研究问题到可发布成果的人工可审计工作流，重点解决事实重复、负结果丢失、AI 草稿越权晋升和论文各产物不一致。

它不创建新的 Frozen Research Schema。第一阶段使用项目内 Markdown、manifest 和明确引用；只有真实使用证明稳定后，才另行讨论是否需要新 Schema。

---

## 2. 项目目录与单一事实源

```text
07_项目/<项目>/
├── research_dossier.md     # 摘要、导航、当前态势
├── assumptions.md          # 假设唯一事实源
├── evidence.md             # Claim–Evidence 唯一事实源
├── decisions.md            # append-only 决策唯一事实源
├── reviews/                # 审稿、处置与复核 Evidence
├── documents/              # Source refs 与精选包导航
├── runs/                   # 模型、解析、检索等 run manifest 导航
└── artifacts/              # Figure、Lean、LaTeX、补充材料导航
```

### 2.1 `research_dossier.md`

Dossier 只保留：

- 研究问题与范围摘要；
- 当前阶段和阻断项；
- 最重要的已审核发现；
- canonical assumptions/evidence/decisions 的链接；
- 模型、实验、Figure、Lean、review 和成果导航；
- 当前贡献、局限和下一步。

Dossier 不复制完整假设、证据或决策。自动生成摘要必须能重建；人工摘要与 canonical 事实冲突时，以 canonical 文件为准并修正 Dossier。

### 2.2 `assumptions.md`

每条假设记录项目内 ref、正文、范围、来源/理由、可证伪条件、状态、影响的 Claim/Model 和审查记录。假设变化不删除历史版本，应记录替代关系及影响分析。

### 2.3 `evidence.md`

每个核心 Claim 记录支持、反对、限制、Source Anchor、运行或证明 Evidence，以及 `QUOTE / PARAPHRASE / INFERENCE` 分类。不得用 Dossier 中的叙述替代 Evidence。

### 2.4 `decisions.md`

决策记录 append-only，至少包括：日期、问题、可选方案、选择、依据、反对意见、代价、可逆性、触发重新评估的条件和关联 Evidence。错误决策通过追加 superseding entry 修正，禁止覆盖历史。

---

## 3. 研究状态不是对象 Schema

项目级研究态势可使用：

```text
FRAMING → EVIDENCE_GATHERING → MODELING_OR_PROVING
        → VALIDATION → REVIEW → WRITING → RELEASED
```

这是导航状态，不得与 Problem YAML `status`、目录 workflow、Attempt outcome、run status 或能力成熟度混同。状态变化只汇总真实 Source，不自动触发 Frozen 对象 lifecycle。

---

## 4. 研究循环

```text
界定问题
→ 建立假设与可证伪条件
→ 收集支持和反对证据
→ 推理 / 建模 / 形式化
→ 设计验证与反例
→ 记录失败和决策
→ 严格审稿
→ 修订或推翻
→ 写作与成果一致性检查
→ 授权发布 / 知识沉淀
```

每轮必须明确“当前结论会被什么证据推翻”。没有反对证据搜索或边界分析的“完成”不满足博士级标准。

---

## 5. 负结果与失败路线

必须保留：

- 未找到证明及失败的关键步骤；
- 被反例推翻的猜想；
- 不可行、不可识别或数值不稳定的模型；
- 不优于基线的结果；
- 无法复现的实验；
- 相互冲突的文献；
- 被拒绝的设计方案及理由；
- 超出数据、许可证或伦理边界而终止的路线。

负结果不等于垃圾输出。只有明确无研究价值且不属于审计记录的临时缓存，才按治理策略清理。

---

## 6. 严格审稿角色

v1.7 可以由同一 AI 按角色顺序执行；角色分离是检查清单分离，不等于已启用多 Agent。

| 角色 | 核心问题 | 典型阻断缺陷 |
| --- | --- | --- |
| Proof Reviewer | 量词、条件、逻辑、边界、反例是否正确 | 证明跳步、条件缺失、循环论证 |
| Evidence Reviewer | Claim 是否被来源准确支持 | 错引、版本错、推断冒充原文 |
| Model Reviewer | 假设、单位、求解、敏感性是否合理 | 单位错、不可识别、错误最优性解释 |
| Reproducibility Reviewer | 第三方能否重建结果 | 无锁定环境、缺数据 hash、手工步骤 |
| Formalization Reviewer | Lean statement 是否等价 | 弱化命题、遗漏假设、虚假 axiom |
| Editor | 论文、图、表、引用和贡献是否一致 | 数字漂移、过度声称、图文矛盾 |

每个 review 产出：审查范围、使用版本、发现、严重度、Evidence、要求动作、作者回复、处置状态和复核结论。

---

## 7. 缺陷严重度与门禁

| 严重度 | 定义 | 发布动作 |
| --- | --- | --- |
| `BLOCKER` | 结论错误、数据/隐私违规、伪造证据或不可恢复成果 | 立即阻断 |
| `MAJOR` | 可能改变核心结论或复现性 | 修复并复核后才可发布 |
| `MINOR` | 不改变核心结论但影响清晰度/完整性 | 记录并在发布前处理或获明确接受 |
| `NOTE` | 改进建议 | 不阻断，保留决策 |

AI 不能自行把 `BLOCKER/MAJOR` 降级。作者回复不能替代 reviewer 复核。

---

## 8. 写作与成果一致性

正式写作必须建立以下连接：

| 论文元素 | 必须回到 |
| --- | --- |
| 核心主张 | Reviewed Claim–Evidence |
| 公式/定理 | 推导、来源或 Lean artifact |
| 数值 | 不可变 run、指标定义和输出 hash |
| 图 | Figure manifest、Claim、run、代码和数据 |
| 表 | 生成脚本/数据、单位和统计定义 |
| 引用 | 已核对的文献身份和版本 |
| 方法 | 代码版本、配置、假设和适用范围 |
| 补充材料 | 与主文版本和 commit 一致 |
| PDF | P9 build 记录和发布 hash |

禁止手工把结果数字复制到多处后独立维护。能够生成的表格和指标应从同一 Reviewed artifact 生成；无法自动生成时执行逐项 consistency review。

---

## 9. 学术写作要求

- 摘要和结论只包含正文已支持的结果；
- “首次”“显著”“证明”“最优”等强词必须满足相应 Evidence；
- 相关工作不只列举，还比较问题、假设、方法、数据、理论、实验和结果；
- 方法写到独立研究者可复现的程度；
- 限制和负结果不得藏在内部记录而从论文删除；
- 统计结果报告效应量、不确定性和样本量，不只报告显著性；
- 图表和表格在正文中解释其研究含义，而不是只描述视觉现象；
- AI 辅助范围按治理规范披露，最终作者承担正确性和署名责任。

---

## 10. 知识晋升协议

研究项目的 Reviewed 内容不自动等于 Formal Knowledge。唯一允许路线是：

```text
DERIVED research material
→ 原文/模型/证明复核
→ REVIEWED project evidence
→ 人工确认可复用性与边界
→ 用户明确说“开始知识沉淀”
→ 按现有 Knowledge authoring / validator / indexer 工作流
→ FORMAL Knowledge
```

“审核通过”只表示内容审核通过，不授权 Knowledge creation、正式归档、LaTeX/PDF 发布或大规模长期记忆修改。任何晋升继续服从 `AGENTS.md` 的权限语义。

### 10.1 知识图谱与跨项目复用

跨项目复用优先连接已有 P/K/M ID、Reviewed Evidence ref、代码 run、Figure 和 Lean artifact，不创建第二套身份。关系视图由已验证 Source 派生，可重建且不得人工编辑。

复用时必须带出原始适用条件、反例、数据范围、版本和 review Evidence；不得只复制结论。至少多个真实项目出现稳定查询需求后，才允许为 Research Question、Claim、Evidence、Paper 或 Source 提出候选 Schema；任何候选设计都不得反向修改现有 Frozen Schema。

知识图谱能力首先表示“可追溯关系与跨项目查询”，不强制某个图数据库引擎。图数据库是否进入生产，必须由查询规模、性能 Baseline 和迁移成本共同证明。

---

## 11. 长期研究记忆

长期记忆保存高价值状态，不复制所有原始输出：

- 当前项目阶段与阻断项；
- 已验证能力及 Gate Evidence；
- 关键决策和被推翻路线的导航；
- 可复用方法与已正式沉淀知识；
- 研究者能力成长的真实 Evidence；
- 最近测试基线和下一步。

生成索引仍属于 Generated，不得人工编辑。研究摘要与 filesystem 冲突时，以 Source 为准。

---

## 12. 权限与 Source Mutation

未经明确授权，不得：

- 正式归档、创建 Knowledge 或修改 Frozen Schema；
- 覆盖正式成果；
- 删除原始资料、失败 Evidence 或历史决策；
- 让 review、RAG 或 Agent 直接修改正式 Source；
- 将外部服务输出直接写入 `01_知识库/` 或 `08_成果输出/`；
- 因生成摘要而改变 Problem / Attempt / Method 的身份或 lifecycle。

所有候选修改先写隔离位置，通过 validator/review 后按已有 atomic mutation 协议处理。

---

## 13. v1.1、v1.7、v1.8 Gate

### v1.1

- Dossier 与 assumptions/evidence/decisions 的重复事实检出率 `100%`；
- decisions 历史覆盖修改次数 `0`；
- 一个真实项目能够记录假设替代、负结果和决策反转；
- 无明确授权创建 Formal Knowledge 的次数 `0`。

### v1.7

- 六类 reviewer 均有固定缺陷 fixture；
- `BLOCKER/MAJOR` 检出率 `100%`；
- 未复核的 `BLOCKER/MAJOR` 进入发布候选次数 `0`；
- review、作者回复、处置和复核 provenance 完整率 `100%`。

### v1.8

- 核心主张、数字、图、表和引用 provenance 覆盖率 `100%`；
- 故意制造的数字/图文/版本漂移检出率 `100%`；
- 正式 PDF 均由 P9 发布，旁路发布次数 `0`；
- AI 贡献披露和作者责任记录完整率 `100%`；
- 未经 `开始知识沉淀` 授权创建 Knowledge 的次数 `0`。
