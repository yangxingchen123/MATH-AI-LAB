# MATH-AI-LAB 文档智能与证据链规范

**状态：** Candidate
**上位契约：** [博士级数学研究工作台总架构](2026-08-20-doctoral-research-workbench-design.md)
**对应版本：** v1.2 Document Intelligence、v1.3 Literature Evidence

---

## 1. 目标与边界

本子系统把原始研究资料转成“可搜索、可精选、可回到原页复核”的派生材料。它不把 OCR 文本当原文，不自动创建 Knowledge，也不把 AI 摘要标为文献结论。

目标输入：PDF、扫描 PDF、图片、DOCX、PPTX、XLSX，后续增加网页资料。目标内容包括标题、段落、列表、公式到 LaTeX、表格到结构化格式、图片、图注、脚注、页码、阅读顺序和版面坐标。

---

## 2. MinerU Sidecar

MinerU 是首选解析引擎，但不是永久能力本身。

- 使用独立环境、容器或已配置服务；
- 不复制 MinerU 源码到本仓库；
- 不把其重型依赖加入根 `requirements.txt`；
- 支持本地 CLI 和 API 两种后端；
- API 地址、凭据和模型路径不得写死；
- v1.2 初始兼容目标为 MinerU `3.4.5`，实施时锁定精确版本并保存兼容 fixture；
- 引擎升级必须重跑输出契约、版面、公式和表格回归；
- 记录上游许可证、模型许可、必要归属和再分发限制。

Sidecar Adapter 对上层暴露稳定的 Parse Request / Parse Result，不向上泄漏引擎私有路径。

---

## 3. 稳定消费契约

v1.2 的稳定消费集合为：

- 主 Markdown：`*.md`；
- 有序内容块：`content_list.json`；
- 版面复核：`layout.pdf`；
- 提取图片：`images/`；
- 诊断时可读取 `middle.json`。

仍可能变化的 `content_list_v2.json` 不得作为唯一生产契约。Adapter 必须将引擎输出正规化为项目内部 Derived Package，并在 manifest 中保存原始输出类型和版本。

```text
原始文件
→ 身份、数据等级、SHA-256
→ 隔离解析
→ Derived Package
→ 公式/表格/版面抽查
→ 面向研究问题的精选
→ 原页复核
→ Reviewed Evidence Pack
→ Research Dossier 导航
```

---

## 4. Derived Package

每次解析形成不可变 run 目录，至少包含：

```text
derived/<source-id>/<run-id>/
├── manifest.json
├── document.md
├── content_list.json
├── layout.pdf
├── images/
├── qa_report.json
└── logs/
```

`manifest.json` 扩展总架构 Provenance Envelope，并记录：

- source URI / path、source SHA-256、文件大小、MIME；
- 数据等级；
- Adapter、MinerU、模型及配置版本；
- 页数与已成功/失败页范围；
- 输出文件及 hash；
- 缓存键；
- `QUEUED / RUNNING / SUCCEEDED / PARTIAL / FAILED / CANCELLED`；
- 运行耗时、硬件类别和诊断摘要。

缓存键至少由 `source_sha256 + engine_version + model_version + config_sha256 + adapter_contract_version` 构成。命中缓存时仍须验证 manifest 与产物 hash。

---

## 5. 精确 Source Anchor

每条准备进入 Evidence Pack 的材料必须拥有精确定位：

```yaml
source_anchor:
  source_ref: "stable source id or URI"
  source_sha256: "64 lowercase hex characters"
  pdf_page_index: 0
  printed_page_label: "12 or null"
  bbox: [x0, y0, x1, y1]
  coordinate_space: "page_points | normalized_0_1"
  section_title: "section path or null"
  block_type: "paragraph | formula | table | figure | caption | footnote"
```

规则：

- `pdf_page_index` 固定为 0-based；显示给用户时可以同时给 1-based 阅读页码；
- `printed_page_label` 不得替代文件页索引；
- `bbox` 缺失时只能降级为页级定位，并明确 `anchor_precision: page`；
- source hash 改变后旧 Anchor 失效，必须重新定位；
- 多栏、跨页表格或跨页公式必须允许多个 Anchor；
- 精选稿不得只保存截断文本而丢失上下文定位。

---

## 6. 引用、转述与推断

Evidence Pack 中的陈述必须标记：

| 类型 | 含义 | 必要要求 |
| --- | --- | --- |
| `QUOTE` | 与来源逐字一致的短引用 | 精确 Anchor、引号、版权限制 |
| `PARAPHRASE` | 忠实转述来源含义 | 精确 Anchor，不得扩大原意 |
| `INFERENCE` | 研究者/AI 基于材料作出的推断 | 列出推理链、假设和支持来源 |

不得把 `INFERENCE` 写成“文献证明了”。关键数学主张使用转述时仍需回查定义、量词、条件和符号。直接引用遵守版权和合理使用限制，优先采用短引文加自主分析。

---

## 7. 内容精选

精选是“围绕研究问题选择与组织证据”，不是通用摘要。每份重要资料至少记录：

- 资料身份、版本、出版状态与来源；
- 当前阅读目的和研究问题；
- 定义、假设、定理、模型、算法；
- 关键公式、表格、图和实验；
- 结论适用边界；
- 冲突、局限、负面或相反证据；
- 与当前问题的关系；
- Source Anchor；
- `QUOTE / PARAPHRASE / INFERENCE`；
- 解析置信和人工核对状态。

精选输出先是 `DERIVED`。只有关键段落、公式、表格和引用完成原页复核后，才可成为 `REVIEWED` Evidence Pack。

---

## 8. 文献身份与版本

文献记录至少支持：

- 标题、作者、年份、venue；
- DOI、ISBN、arXiv 或其他稳定标识；
- 预印本、accepted manuscript、version of record 的区分；
- BibTeX / CSL 可用元数据；
- 原始论文优先；
- 更正、撤稿、版本更新和失效状态；
- 访问时间、来源 URL 和本地 source hash。

同一工作多个版本不得静默合并。引用哪个版本，证据就必须锚定到哪个版本；版本替换后重新执行 Claim 影响分析。

---

## 9. Claim–Evidence 与 Novelty

第一阶段在项目级 `evidence.md` 中表达，不提前冻结新的全局 Claim Schema。每个核心主张至少包含：

- 稳定的项目内 Claim ref；
- 主张正文、范围和可证伪条件；
- 支持 Evidence refs；
- 反对、限制或未决 Evidence refs；
- 证据类型与信任级；
- 当前判断和待完成验证；
- 影响该主张的模型 run、figure、Lean theorem 或 review。

博士级项目必须维护 Novelty Matrix：

| 维度 | 既有工作 | 当前工作 | 可验证新增 |
| --- | --- | --- | --- |
| 问题 | 来源与范围 | 当前定义 | 差异 Evidence |
| 假设 | 既有假设 | 当前假设 | 放宽/加强及代价 |
| 方法 | 已有方法 | 当前方法 | 新步骤与必要性 |
| 数据 | 已有数据 | 当前数据 | 新数据或新测量 |
| 理论 | 已有结论 | 当前结论 | 新定理/界/反例 |
| 实验 | 已有实验 | 当前实验 | 新对照或尺度 |
| 结果 | 已知结果 | 当前结果 | 新增及局限 |

无法在“可验证新增”列给出 Evidence 时，不得使用“首次”“创新”“显著领先”等表述。

---

## 10. QA 与失败语义

### 10.1 固定 QA 抽样

每份重要文档至少抽查：首尾页、随机正文页、每类公式、每类表格、含图注页、双栏/脚注等复杂版面页。关键证据必须 100% 原页复核，不适用抽样。

质量指标至少包括：

- 页面完成率；
- 阅读顺序错误数；
- 关键公式字符/结构错误数；
- 表格行列结构错误数；
- Anchor 命中率；
- 关键证据原页复核覆盖率。

阈值由 v1.2 实施计划基于固定 fixture 明确，不得用单一 OCR 平均分掩盖关键数学错误。

### 10.2 失败处理

- 原始资料始终保留；
- 解析失败不创建 Reviewed 结果；
- 部分页失败标为 `PARTIAL` 并列出缺失页；
- Adapter 不可用只降级文档能力，不修改正式 Source；
- 低置信公式/表格进入人工复核队列；
- 重试产生新 run，不覆盖失败历史或上次成功包；
- 下游只消费明确允许的成功产物，禁止把缺失块当空内容。

---

## 11. 验收 Gate

v1.2 必须至少使用以下 fixture：原生数字 PDF、扫描 PDF、双栏论文、含复杂公式论文、跨页表格文档。每个 fixture 固定 source hash。

强制 Threshold：

- 成功 run 的 manifest 与产物 hash 完整率 `100%`；
- `PARTIAL` 缺失范围报告率 `100%`；
- 精选关键证据 Source Anchor 覆盖率 `100%`；
- 关键证据人工原页复核覆盖率 `100%`；
- source hash 改变后的陈旧 Anchor 检出率 `100%`；
- 未授权自动 Knowledge creation 次数 `0`。

v1.3 另要求：核心 Claim citation coverage `100%`、unsupported attribution `0`、已知更正/撤稿 fixture 检出率 `100%`。

---

## 12. 外部参考

- [MinerU 中文说明](https://github.com/opendatalab/MinerU/blob/master/README_zh-CN.md)
- [MinerU 输出文件说明](https://opendatalab.github.io/MinerU/zh/reference/output_files/)
- [MinerU 许可证](https://github.com/opendatalab/MinerU/blob/master/LICENSE.md)

外部文档只说明引擎能力；项目内稳定契约仍以本文和版本化 Adapter 测试为准。
