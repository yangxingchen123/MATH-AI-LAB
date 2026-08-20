# MATH-AI-LAB 制图与研究成果规范

**状态：** Candidate
**上位契约：** [博士级数学研究工作台总架构](2026-08-20-doctoral-research-workbench-design.md)
**对应版本：** v1.5 Figure & Visualization Framework、v1.8 Artifact Consistency

---

## 1. 目标

制图能力必须把研究结果变成可解释、可复核、可重新生成且可发表的视觉成果。正式图不是手工截图：它必须能回到 Claim、数据、run、源程序、配置和生成环境。

---

## 2. 完整能力范围

- 函数与数学对象图像；
- 几何示意图；
- 网络和路径图；
- 热力图、等高线、三维曲面；
- 误差、收敛和敏感性图；
- 情景与组间比较；
- 算法流程和架构图；
- 交互式探索；
- 出版级静态图；
- 数学动画；
- 明确标记为非精确的概念插图。

上述能力全部保留，按[能力成熟度路线](2026-08-20-doctoral-workbench-capability-roadmap.md)分别升级，不因某个引擎不可用而删除。

---

## 3. 候选引擎分工

| 场景 | 首选候选 | 约束 |
| --- | --- | --- |
| 数值和统计图 | Matplotlib / Seaborn | 必须由数据和脚本生成 |
| 交互探索 | Plotly | 正式成果同时保留可归档静态版本 |
| 网络与路径 | NetworkX / Graphviz | 拓扑、方向和权重来自规范数据 |
| 精确数学图 | TikZ / PGFPlots | 与 LaTeX 字体和符号一致 |
| 工作流和架构 | Mermaid | 节点和关系需与规范一致 |
| 数学动画 | Manim | 保存脚本、时间参数和渲染版本 |
| 非精确信息插图 | AI 图像生成 | 明示概念性，不承担数据或证明 |

AI 图像禁止用于精确坐标、数值数据、几何证明、拓扑关系、误差展示或任何读者可能误认为测量结果的场景。

---

## 4. Figure Manifest

每张正式图和动画扩展总架构 Provenance Envelope，并至少记录：

```yaml
figure_id: "project-local immutable id"
claim_refs: ["claim-ref"]
run_refs: ["run-id"]
source_code:
  ref: "script or source path"
  sha256: "64 lowercase hex characters"
inputs:
  - ref: "data or upstream artifact"
    sha256: "64 lowercase hex characters"
config:
  ref: "config path"
  sha256: "64 lowercase hex characters"
environment_ref: "locked environment or container manifest"
engine:
  name: "exact renderer"
  version: "exact version"
outputs:
  - format: "pdf | svg | png | html | mp4"
    ref: "artifact path"
    sha256: "64 lowercase hex characters"
semantic_checks:
  units: true
  legend: true
  uncertainty: "present | not_applicable"
  grayscale: true
  color_vision: true
review_ref: "review evidence path or null"
```

Figure 不得只引用“最新一次运行”。必须引用不可变 run ID 和数据 hash。

---

## 5. 生成与发布流程

```text
Reviewed Run / Evidence
→ Figure specification
→ 隔离渲染
→ 数据与语义检查
→ 视觉 QA
→ Reviewed Figure
→ 04_LATEX 项目引用
→ P9 检查与原子发布
→ 08_成果输出
```

- 探索图可以是 `DERIVED`，但进入论文或正式讲义前必须 `REVIEWED`；
- 渲染失败不得覆盖上一次正式图；
- `04_LATEX` 保存受控引用与必要 source，不复制无追溯的临时截图；
- 正式 PDF 仍由现有 P9 `check/build` 和 atomic publish 语义管理；
- 交互成果需要同时提供可归档静态快照及其来源。

---

## 6. 精确性与语义检查

每张正式图必须回答：

1. 支持哪个 Claim；
2. 数据来自哪个 run；
3. 变量、单位、归一化和变换是什么；
4. 误差、不确定性或样本量如何表达；
5. 基线和比较对象是否公平；
6. 坐标范围、截断和对数轴是否可能误导；
7. 如何用固定命令重新生成；
8. 图注是否足以在脱离正文时理解；
9. 视觉编码是否与数据类型匹配；
10. 这张图展示的是证据、示意还是概念。

三维图不得作为掩盖二维关系的装饰；双轴图默认禁用，只有审查证明不会误导时才允许；误差条必须说明统计含义。

---

## 7. 可访问性与出版质量

- 优先 PDF / SVG；需要位图时按目标尺寸提供足够分辨率；
- 字体、数学符号和字号与 LaTeX 成果一致；
- 颜色不是唯一区分手段，同时使用线型、标记、纹理或直接标签；
- 检查常见色觉缺陷和灰度打印；
- 图例不遮挡数据，单位进入轴标签或表头；
- 图注说明数据、方法、误差、样本量和必要限制；
- 所有面板有稳定标签，并可从正文引用；
- 动画提供静态关键帧或文字替代；
- 概念插图提供 alt text，并明确“非数据图”。

---

## 8. 可重复性边界

同一脚本不一定产生逐字节相同的 PDF/SVG/PNG：时间戳、字体子集、压缩或渲染器元数据可能改变 binary hash。确定性声明分为：

| 等级 | 含义 |
| --- | --- |
| `BYTE_EXACT` | 输出字节 hash 相同 |
| `NORMALIZED_EXACT` | 去除非语义元数据后 hash 相同 |
| `SEMANTIC_EXACT` | 数据、坐标、图元、文本和样式清单一致 |
| `TOLERANCE` | 像素或数值差异在预设容差内 |

Figure manifest 必须声明采用哪个等级和比较方法。不能在未控制字体、引擎和元数据时承诺 `BYTE_EXACT`。

---

## 9. 图形专项验证

| 图形家族 | 专项检查 |
| --- | --- |
| 函数图 | 定义域、奇点、采样、参数与解析性质 |
| 统计图 | 样本量、聚合、误差、异常值和不确定性 |
| 收敛图 | 误差定义、参考斜率、网格/迭代尺度 |
| 热力/等高线 | 色标范围、插值、缺失值、等值线级别 |
| 三维曲面 | 视角之外提供切片或等高线辅助 |
| 网络图 | 节点/边身份、方向、权重和布局是否混同 |
| 几何图 | 构造关系与定理条件一致 |
| 流程/架构图 | 与当前规范和实际依赖一致 |
| 动画 | 帧率、时间尺度、状态转移和关键帧 |
| 概念插图 | 不含伪数据、伪公式或暗示性精确关系 |

---

## 10. 失败与回滚

- 渲染使用隔离目录；成功验证后才更新可发布候选；
- 缺字体、引擎或 GPU 时报告明确诊断和 fallback；
- fallback 改变渲染语义时必须重新审查，不得只替换文件；
- 输入 run 已陈旧或被撤销时，相关图标记 stale 并阻断发布；
- Claim 被推翻时保留历史图，但从当前正式成果移除；
- 人工编辑正式图后必须把修改固化到源程序，禁止只改导出文件。

---

## 11. v1.5 Gate

固定 Pilot 至少包含：

1. 一张由模型 run 生成、含不确定性的数值图；
2. 一张由规范节点/边数据生成的网络图；
3. 一张精确数学或几何图；
4. 一张流程或架构图。

强制 Threshold：

- 四个 Pilot 的 Claim、run/来源、代码、配置、环境和输出 hash 覆盖率 `100%`；
- 固定命令重建成功率 `100%`；
- 单位/图例/图注专项检查通过率 `100%`；
- 灰度与色觉检查通过率 `100%`；
- 人工修改仅存在于导出文件的次数 `0`；
- 无 provenance 的图进入正式 LaTeX/PDF 的次数 `0`；
- AI 概念插图被误用为精确图的次数 `0`。

其他图形家族保持 `TARGET` 并按路线升级，不得以四个 Pilot 宣称制图全集完成。
