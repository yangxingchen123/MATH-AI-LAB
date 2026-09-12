# MATH-AI-LAB Studio UI 路线

**状态：** Candidate  
**上位契约：** [博士级数学研究工作台总架构](2026-08-20-doctoral-research-workbench-design.md)  
**实现入口：** `tools.studio`（与 `tools.workbench` 竞赛编排分开）  
**双击入口：** 仓库根目录 `打开工作台.bat` / `打开工作台.vbs`  
**演示地址：** http://127.0.0.1:8765/  
**触发：** 2026-09-09 先做只读 Notebook 壳，再按本文件升级；禁止另起平行 Source 树。

本文是 **UI 产品与成熟度路线**，不是 Frozen Schema，不授权改 `元数据规范.md`。权威仍是：Frozen Schema → `项目规则.md` → `项目进度.md` → 本文。

---

## 1. 「非常完美」在这里指什么

完美不是仪表盘、动画或第二套笔记软件。对 MATH-AI-LAB，界面完美当且仅当：

1. **判断先于版式。** 打开任何对象前，种类已经可见：习题 / 建模 / 文献 / 实验 / 批改 / infra。
2. **一篇对象就是一篇笔记。** 顶栏换库，左侧换对象，中间读全文，右侧看本页与协议。不把证明切成五个 App 页。
3. **目录 ≠ YAML。** `未解决 / 研究中 / 已解决` 是工作流位置；`status` 是对象生命周期。两套徽章永远分开。
4. **证据分层可见。** 启发式、数值、人可读证明、Lean、文献标题不能显示成同一种「已完成」。
5. **写入极窄。** 默认只读仓库。任何写入必须走已有授权语义，且不得从 UI 伪造 Attempt。
6. **公式与长文达到阅读质量。** KaTeX、表格、引用、callout 稳定；P0001 千行级文件仍可滚动、可定位。
7. **关掉窗口就停止。** 本机 loopback，无账号，无云同步，无第二数据库。

做不到以上任一条，就不许宣称 Studio 完成。

---

## 2. 锁定的信息架构

```text
顶栏 tabs     今日 | 题目 | 知识 | 方法 | 项目 | 实验室     模式 AUTO/STUDY/REVIEW/RESEARCH
左侧树        只列当前库的对象（工作流分组 / domain / 项目文件）
中间长文      一篇 Markdown；题目按题面→重构→解答→验证→分流阅读，但不拆路由
右侧栏        本页大纲 · 种类 · 障碍 · 反向链接 · 源路径
```

参考：[Fumadocs Notebook](https://github.com/fuma-nama/fumadocs) 的架子，[Quartz](https://github.com/jackyzha0/quartz) 的读文节奏。只借版式，不把 Fumadocs / Quartz / Obsidian 装进仓库当正式前端。

| 库 | 树的分组 | 中间读什么 | 右侧多什么 |
| --- | --- | --- | --- |
| 今日 | 进行中 / 最近 | 索引短文，禁止 KPI 墙 | 跳转到对象 |
| 题目 | 研究中 / 未解决 / 已解决 / 起草 | Problem 全文 | 协议、parts、Attempt ≠ Solution |
| 知识 | domain | 概念 / 定理本身 | 前置、来源题、Method |
| 方法 | status | 适用 / 意图 / 杀掉 | 来源题、绑定 Knowledge |
| 项目 | 每个 Dossier 的文件 | dossier / decisions / evidence | 决策可逆、证据 kind |
| 实验室 | 运行条件 / 校准 | operate 禁令或 PROB 校准 | 不宣称四大 |

今日不是第三个工作区。它只是跳板。

---

## 3. 六条界面禁令

1. 不把美赛 / 国赛整卷做成一道 `Pxxxx`。
2. 不把 `tools.workbench`（竞赛实验编排）和 Studio 混成同一个模块。
3. 不用图谱、KPI、热力图冒充研究进度。
4. 不在根 `requirements.txt` 加 React / Next / 向量库 / 求解器。
5. 不把 UI 状态写进 Problem YAML（mastery、tags、last_opened 等 Derived 字段仍然禁止）。
6. 用户说「优化系统 / 运行条件」时，UI 只许停在实验室 operate，不许诱导「再写一题」。

---

## 4. 视觉与阅读质量

| 项 | 规定 |
| --- | --- |
| 密度 | 学术笔记本，不是 Admin |
| 正文宽 | 约 680–720px |
| 颜色 | 一种 accent；YAML / 目录 / 证据层用中性字，不用彩虹徽章 |
| 公式 | 行内 `$...$` 与块 `$$...$$` 均 KaTeX；失败时回退源码，不吞掉 |
| Markdown | 标题、列表、表格、代码、脚注、GFM 引用；YAML front matter 不进正文 |
| 主题 | 跟随系统浅色 / 深色 |
| 动效 | 无渐变、无阴影、无装饰 emoji |
| 大文件 | P0001 级长文：右侧大纲可点，主栏保留滚动位置 |
| 无障碍 | 键盘可到树、tabs、大纲；对比度达标 |

KaTeX 只许 **vendor 进 `tools/studio/static/vendor/`**，或纯 stdlib 退化。不进根依赖。

---

## 5. 模式如何改界面

| 模式 | 题目页 | 禁止 |
| --- | --- | --- |
| AUTO | 全文可见，标明 AI Solution ≠ Attempt | 把 AUTO 解答写入 Attempt Ledger |
| STUDY | 解答节可折叠；提示「先写你的 Attempt」 | 为了保护 Evidence 而拒绝打开已归档正文 |
| REVIEW | 优先用户原解区块（若有 Ledger） | 先给标准答案再批改 |
| RESEARCH | 未决 / 证伪单独成节，不得混进本题证明 | 把拓展写进本题解答 |

模式是对话策略的镜子，不是新的 YAML 字段。

---

## 6. 分阶段与关闭门（必须按序）

每一阶段先写失败测试，再改 UI。阶段没关，不准开始下一阶段的「好看」。

### S0  可打开的只读壳

**已关闭：** Notebook 壳、真实对象目录、loopback 只读 HTTP、双击启动、路径穿越 404、POST 405。

**关闭条件：**

- `pytest tests/studio` 全过；
- 双击 `打开工作台.bat` 能打开 http://127.0.0.1:8765/ ；
- 目录含 P0001 / P0002 / K0001 / K0002 / M0001 / M0002 / 美赛2026-A / PROB-SF-001，不含 P0000；
- 服务只绑 127.0.0.1。

### S1  阅读质量

**已关闭（2026-09-09）：** vendor KaTeX v0.18.4、正文去 front matter、大纲来自真实 `h2`、源路径可复制。没有公式的数学工作台不算完成。

**做：**

- vendor KaTeX；
- 正文去掉 front matter；
- GFM 表格 / 引用 / 围栏代码；
- 右侧大纲来自真实 `h2`，点击滚动；
- 源路径可一键复制。

**关闭条件：**

- P0002 题面中的 `\\varphi` / `AX-XB` 以公式渲染，而不是裸 `$`；
- P0001 打开后大纲可跳到分节；
- 无网离线仍能渲染（vendor，不 CDN）。

### S2  题目工作区（产品主表面）

**做：**

- 面包屑：`题目 / 已解决 / P0002 / a·b·c`；
- YAML status 与目录分列；
- 右侧固定：种类、当前障碍（来自正文「重构」或研究记录，不编造）、反向链接；
- multipart 小问锚点；
- STUDY 只折叠「解答 / 证明」类节。

**关闭条件：**

- P0002 三小问可从右侧点到；
- `knowledge: []` 显示为「mapping 已完成」，不是「还没关联」；
- 不出现「已解决 = reviewed」的合并徽章。

### S3  关系与分流

**做：**

- Problem → Knowledge / Method 反向链接（只读，来自既有 YAML 与分流段落）；
- 知识页显示前置；
- 方法页显示适用 / 杀掉。

**关闭条件：**

- P0001 能跳到 K0001 / K0002 / M0001；
- P0002 能跳到 M0002；
- 不自动创建 K/M。

### S4  项目 Dossier（建模表面）

**做：**

- 美赛文件树：dossier / decisions / model_selection / evidence / problem；
- 决策表保留「可逆 / 再访条件」；
- 计算事实旁标注证据 kind（COMPUTATION ≠ 证明）。

**关闭条件：**

- 打开 美赛2026-A 不会出现「加入题库」主按钮；
- DEC-0001 与 known-answer 15 Wh / 3 W → 5 h 分层可见。

### S5  实验室

**做：**

- operate 页：分层表 + infra 禁令；
- PROB-SF-001：阶段、已知界、Lean 声明只读；
- 不提供「再跑一遍 P001」的默认大按钮。

**关闭条件：**

- 文案写明校准 ≠ 新定理；
- `paper_ready` 不得在 UI 标成已发表。

### S6  检索

**做：**

- 顶栏搜索从「过滤当前树」升级为调用既有 `tools.retrieval`（若 Gate 可用）；
- 命中按对象类型分组；查询必须能显示「这是工作命题检索」的提示。

**关闭条件：**

- 检索失败合法，不编造命中；
- 向量库未装时 DEGRADED，Core 仍可打开文档。

### S7  受控写入（最后，默认仍只读）

只在用户明确授权后做，且复用现有 Layer 2 操作，不在 JS 里改 YAML。

| 用户说 | UI 可以 |
| --- | --- |
| 对话里解答 | 复制提示词（已有） |
| 加入题库 | 调已有 creator / 交给 Agent，不得分配 P0000 |
| 审核通过，请归档 | 才允许 close 类操作 |
| 开始知识沉淀 | 才允许 Knowledge authoring |
| 未授权 | 任何 PUT/POST 仍 405 |

**关闭条件：**

- 写入测试证明：未授权请求不改仓库；
- Attempt 仍只能来自用户真实作答；
- 没有「保存到浏览器 localStorage 当正式稿」。

---

## 7. 技术边界

| 允许 | 禁止 |
| --- | --- |
| `tools/studio` + `static/` + vendor | 根目录 Next/Vite 工程当正式 Source |
| stdlib `http.server` | 把 UI 做成必须联网的 SaaS |
| 复用 problem/knowledge/method parser | UI 自己 parse 出一套新 Schema |
| 只读 JSON API | UI 直写 `02_题目库/` |
| 双击 bat/vbs | 安装成 Windows 服务、开机自启 |

引擎可换（以后可以换成别的静态壳），**能力**不能换：只读目录、种类分流、证据分层、授权写入。

---

## 8. 现在到下一步

当前 = **S0 / S1 已关，S2 未开**。

下一刀：S2 题目工作区（parts 锚点、协议栏、STUDY 折叠解答、目录与 reviewed 分列）。不要跳去做图谱或写入。

验收口令：打开 P0002，公式是公式，右侧点「题目」会滚到那一节，关掉服务器窗口界面就停。
