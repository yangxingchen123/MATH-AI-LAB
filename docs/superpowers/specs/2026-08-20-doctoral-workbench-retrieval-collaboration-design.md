# MATH-AI-LAB 检索、RAG 与多角色协作规范

**状态：** Candidate
**上位契约：** [博士级数学研究工作台总架构](2026-08-20-doctoral-research-workbench-design.md)
**对应版本：** v2.0 Hybrid Retrieval & Cited RAG、v2.1 Controlled Multi-Agent Research

---

## 1. 进入条件

检索和多 Agent 都是最终能力，不能删除；但它们不是 Foundation Closure 的前置条件。

进入 v2.0 前必须已有：

- 稳定的 Source / Derived / Reviewed 分离；
- 精确 Source Anchor；
- 可靠文献身份和版本；
- 数据等级与权限过滤；
- 固定检索评测集；
- 证据表明 Metadata / FTS / BM25 已不能单独满足真实规模需求。

进入 v2.1 前还必须已有：

- 稳定单角色工作流；
- 六类审稿清单；
- Candidate 输出和 Source Mutation 门禁；
- 任务、成本、工具调用和失败审计；
- 单角色质量基线。

---

## 2. 检索阶梯

```text
Metadata filter
→ Full-text search
→ BM25 lexical retrieval
→ Vector semantic retrieval
→ Hybrid retrieval + reranking
→ Cited RAG
```

每一级只有在固定评测上证明增益后才增加复杂度。向量数据库不是目的；可回溯的有效检索才是目的。

### 2.1 Metadata

按对象类型、项目、作者、年份、版本、数据等级、信任级、标签和状态过滤。权限与数据等级过滤必须在召回前执行，不能先检索 Restricted 内容再在回答阶段遮盖。

### 2.2 FTS / BM25

保留精确术语、符号、定理名、引用和变量名的词法召回。数学文本分词必须测试公式、Unicode 符号、LaTeX 和中英文混合文本。

### 2.3 Vector / Hybrid

向量索引只消费允许进入索引的内容；embedding 模型、版本、chunk 规则和 source hash 进入 provenance。Hybrid 结合 metadata、词法、向量和 reranking，不能用语义相似度覆盖来源权威等级。

---

## 3. 索引单元与失效

索引项至少保存：

- stable source/object ref；
- source hash 和版本；
- chunk range / Source Anchor；
- `SOURCE / DERIVED / REVIEWED / FORMAL`；
- `PUBLIC / PERSONAL / RESTRICTED`；
- 解析、chunk、embedding 和 index 版本；
- 允许访问的 scope；
- stale / retracted / superseded 状态。

source hash、权限、版本或信任级变化后，相关索引项必须失效并可重建。Generated index 不是事实源，不允许手工修补。

---

## 4. Cited RAG 回答契约

RAG 输出默认是 Candidate，并必须：

1. 为每个核心外部事实提供具体引用；
2. 引用定位到原始对象或精确 Source Anchor；
3. 区分原文、转述和模型推断；
4. 披露来源版本、信任级和冲突；
5. 同时检索支持与反对证据；
6. 证据不足时明确拒绝下结论；
7. 不把检索排名解释为来源可靠性；
8. 不把 Derived OCR 片段冒充 Source；
9. 不绕过 Knowledge / Problem / Method 的现有 validator；
10. 不自动将回答写入正式 Source。

引用应指向实际支持该句的材料，而不是只列一个泛化书目。

---

## 5. 检索评测集

评测集从真实研究问题抽取，并覆盖：

- 精确术语/定理名；
- 同义改写；
- 公式或符号查询；
- 跨语言查询；
- 多版本文献；
- 相互冲突的证据；
- 否定查询与无答案查询；
- 权限隔离；
- 更正、撤稿和 stale 内容；
- 需要多跳证据的问题。

至少测量：

| 指标 | 含义 |
| --- | --- |
| `Recall@k` | gold Evidence 是否进入前 k |
| `MRR` / `nDCG` | 相关结果排序质量 |
| Citation coverage | 核心主张有引用的比例 |
| Citation precision | 引用实际支持主张的比例 |
| Unsupported attribution | 无来源却声称来源支持的次数 |
| Conflict coverage | 反对/冲突证据被召回的比例 |
| Permission leakage | 越权内容被召回或输出的次数 |
| No-answer accuracy | 证据不足时正确拒答的比例 |

v2.0 的具体 Recall@k / nDCG 阈值由实施计划在 Baseline 后固定；Citation coverage 和 precision 对核心主张必须为 `100%`，unsupported attribution 和 permission leakage 必须为 `0`。

---

## 6. 多角色能力

最终支持以下逻辑角色：

| 角色 | 产出 | 不得做 |
| --- | --- | --- |
| Solver | 解法、模型或证明 Candidate | 自行宣称审核通过 |
| Skeptic | 反例、漏洞、边界和替代解释 | 无 Evidence 地否定 |
| Verifier | 推导、数值、条件和不变量核查 | 把测试通过等同于证明正确 |
| Literature | 来源、比较、版本和证据包 | 编造引用 |
| Modeling Reviewer | 假设、单位、识别性、求解状态和解释审查 | 只检查代码能否运行 |
| Formalizer | Lean statement / proof Candidate | 以编译替代语义审核 |
| Reproducer | 环境重建、运行和差异报告 | 覆盖原 run |
| Editor | 一致性、结构和表达修订 | 改变结论而不留记录 |

角色可以由同一模型顺序执行，也可以由多个受控 Agent 执行。能力定义不绑定某个编排框架或模型供应商。

---

## 7. 编排协议

每个多角色任务必须记录：

- task ID、研究目标、范围和停止条件；
- 输入 refs、hash、数据等级和授权 scope；
- 各角色模型/引擎版本、提示或策略 hash；
- 工具调用、检索结果和引用；
- 输出、状态、耗时和成本；
- 角色间依赖与分歧；
- reviewer 结论和最终人工决定；
- 取消、超时、重试和 fallback。

状态使用总架构长任务协议。子任务失败时，编排器不得把整体标为无条件成功；必须标 `PARTIAL` 或 `FAILED` 并列缺失角色和影响。

---

## 8. 安全边界

- Agent 输出一律是 Candidate；
- Agent 不直接修改 Frozen Source、正式 Knowledge 或发布成果；
- Source Mutation 只能经过已有授权、validator 和 atomic workflow；
- Restricted 数据只交给获明确许可的本地/服务引擎；
- 每个角色遵循最小工具权限；
- 不允许 Agent 自行扩大任务、复制凭据、邀请外部参与者或改变数据等级；
- 多角色共识不等于事实，多数投票不替代 Evidence；
- 高影响结论和发布仍需人工审查。

---

## 9. 分歧处理

角色意见冲突时：

1. 保留每个独立输出和 provenance；
2. 将争议拆成可验证 Claim；
3. 请求 Skeptic 列出能区分方案的 Evidence；
4. 优先运行可判定验证、反例、实验或 source check；
5. 无法裁决时记录为未决，不强行合并；
6. 人工决定进入 append-only `decisions.md`。

编排器不得通过删除少数意见制造“共识”。

---

## 10. 单角色基线与收益证明

多 Agent 只有在真实指标上优于单角色时才值得增加成本。对照必须使用相同任务、可比模型能力、工具权限、预算和时间约束。

至少比较：

- 核心错误检出率；
- 证据覆盖和引用精度；
- 可复现成功率；
- 严重幻觉/错误率；
- 完成时间和计算/调用成本；
- 人工修订量。

如果只增加输出长度或成本而不提高质量，则保留角色清单但默认使用单角色顺序执行。

---

## 11. 失败与 fallback

- 检索引擎失败时降级到前一级：Hybrid → BM25/FTS → Metadata；
- embedding 或 reranker 升级失败时继续使用上次验证版本；
- RAG 无充分证据时返回证据不足，不调用无来源自由生成作为假 fallback；
- 多 Agent 超时、成本超限或角色失败时回退为单角色流程；
- fallback 必须显式显示，不得伪称完整能力；
- 失败任务和部分输出保留审计，但不写正式 Source。

---

## 12. v2.0 / v2.1 Gate

### v2.0

- 固定评测集中核心回答 citation coverage `100%`；
- citation precision `100%`；
- unsupported attribution `0`；
- permission leakage `0`；
- stale / retracted fixture 未经说明进入正式答案次数 `0`；
- Hybrid 至少在一个预先指定质量指标上高于 BM25 基线；
- 索引可由 Source 和版本化配置完全重建。

### v2.1

- 所有角色输入、输出、模型/策略、工具调用、成本和状态 provenance 完整率 `100%`；
- Agent 直接修改正式 Source 次数 `0`；
- 固定缺陷任务上至少一项质量指标高于单角色基线，严重错误率不得升高；
- 超时、取消和单角色 fallback 成功率 `100%`；
- 分歧被静默丢弃次数 `0`；
- Restricted 数据越权发送次数 `0`。

未通过收益 Gate 时，多角色能力保留为 `PILOT`，不得为了路线表好看而升为 `STABLE`。
