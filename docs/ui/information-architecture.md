# 信息架构

产品对象是 Knowledge / Problem / Method / Research Dossier / Artifact，不是「一篇 Document」。

---

## 1. 三类状态（界面硬规则）

| 名称 | 权威 | 例子 | 禁止 |
| --- | --- | --- | --- |
| 对象生命周期 | YAML `status` | draft / reviewed / archived | 写成「已做对」 |
| 工作流目录 | `未解决/` `研究中/` `已解决/` | P0002 在已解决 | 与 reviewed 合成一枚徽章 |
| Attempt | Ledger | partial / unsolved | 写入 Problem YAML |

种类分流（习题 / 建模 / 文献 / 实验 / 批改 / infra）是 **对话策略**，不是 Frozen `problem_type`，**不写 YAML**。UI 只在起草与首页提示。

---

## 2. App Shell

Desktop 三栏（Fumadocs 的架子，自己的对象）：

```text
┌ Top: 标识 · 搜索/命令盘 · 主题 · 设置 ┐
├ Sidebar ┬ Content（~70–90ch）┬ TOC/Meta ┤
```

| 宽度 | 布局 |
| --- | --- |
| ≥1280 | 三栏 |
| 768–1279 | 侧栏 + 正文；TOC 抽屉 |
| <768 | 单栏；侧栏抽屉；公式/表横向滚，页面不横溢 |

顶栏不放营销 Hero。左侧按 **Human Interface v1** 三柱浏览，不是文件夹。

```text
MATH-AI-LAB
  Human Interface v1
    学习     知识 · 题目 · 方法
    研究     研究 · 参考 · 成果
    个人     记忆 · 收件箱 · 提示词
    高级     Lean · Lab · 仓库 · 诊断 · 设置
         Search / Relations / Math
                   ↓
           packages/content
                   ↓
           Markdown Repository
                   ↓
      Python Core / Validator / Lean
```

### 左侧导航

| 柱 | 导航 | 路由 | 仓库 | v1 |
| --- | --- | --- | --- | --- |
| — | 工作台 | `/` | 派生 | 已开 |
| 学习 | 知识 | `/knowledge` | `01_知识库/` | 已开 |
| 学习 | 题目 | `/problems` | `02_题目库/` | 已开 |
| 学习 | 方法 | `/methods` | `12_方法库/` | 已开 |
| 研究 | 研究 | `/research` | `07_项目/` | 已开 |
| 研究 | 参考 | `/references` | `03_参考资料/` | 已开 |
| 研究 | 成果 | `/outputs` | `08_成果输出/` | 已开 |
| 研究 | 猜想 | — | Research Intelligence | **未开** |
| 研究 | 实验 | — | Research Intelligence | **未开** |
| 研究 | 时间线 | — | Research Intelligence | **未开** |
| 个人 | 记忆 | `/memory` | `09_长期记忆/` | 已开 |
| 个人 | 收件箱 | `/inbox` | `00_收件箱/` | 已开 |
| 个人 | 提示词 | `/prompts` | `10_提示词/` | 已开 |
| 高级 | Lean | `/lean` | `06_LEAN形式化/` | 已开 |
| 高级 | Lab | `/lab` | `tools.research_lab` | 已开 |
| 高级 | 宇宙 | `/universe` | domain-math 投影 | 已开（只读原型） |
| 高级 | 仓库 | `/repository` | 白名单树 | 已开 |
| 高级 | 诊断 | `/advanced/diagnostics` | Adapter 只读 | 已开 |
| 高级 | 设置 | `/settings` | 本机健康探测 | 已开 |

共享能力（不是第三套对象树）：Search、Relations、Math → 只读 `packages/content` → 仓库 Markdown。写入 → Domain Operation → Python Validator。

二级随路由变：题目按工作流目录；知识按 `domain`；研究按项目名。普通人第一眼不看文件系统。

模式 AUTO / STUDY / REVIEW / RESEARCH：只改题目阅读（折叠解答、先原解、未决单列），不改 Schema。

---

## 3. URL（稳定 ID，不绑路径）

```text
/
/knowledge
/knowledge/new
/knowledge/K0001
/problems
/problems/new
/problems/P0002
/problems/P0002#a
/methods
/methods/new
/methods/M0002
/research
/research/mei-sai-2026-a          # slug 来自目录名，展示名仍是「美赛2026-A」
/references
/outputs
/memory
/inbox
/search
/settings
/settings/repository              # 高级文件树
```

永久链接用 `P0001` / `K0001`，不用 `02_题目库/已解决/P001_....md`。文件搬家 URL 不变。

---

## 4. 首页 `/` — 下一步做什么

不是 Landing Page。块只在有数据时出现（无则省略，不画空 KPI）。

当前仓库真实可做的块：

- **继续：** 最近打开的 P/K（本地 recent，不进 YAML）
- **当前项目：** 美赛2026-A（Dossier，不是 P）
- **题目工作流：** 未解决 / 研究中 / 已解决的 **目录计数**（现在已解决=2）
- **知识 / 方法：** K0001、K0002、M0001、M0002
- **收件箱：** 若有未分类则入口
- **系统：** Core / Lean sidecar 健康（DEGRADED 如实）

禁止：Unsolved 34 这种假数；巨大 Banner；把美赛「加入题库」。

核心任务 ≤ 3 次点击：首页→题；搜索→K；题目→P0002→小问。

---

## 5. 各表面

### 知识 `/knowledge` `/knowledge/K0001`

浏览：树（按 Frozen `domain`）与列表（按 `updated`）。  
**没有** Schema 里的 tags。筛选只用：domain、status、prerequisites 深度、日期。

页：面包屑、标题、objectStatus、domain、aliases、正文、前置、related、来源题（反查 `knowledge` 含此 K 的 P）、方法指针。  
不强制拆 Definitions/Theorems 节——**按正文真实标题**。没有的节不生成空壳。

### 题目 `/problems` `/problems/P0002`

列表极密：ID、标题、**工作流目录**、**YAML status**、parts 个数、`updated`。  
筛选：工作流目录、objectStatus、是否有 parts。无 difficulty 字段则 **不做难度筛**。

详情 **按 parts 分块**（有 `parts` 时），不要一整条 Markdown 糊上：

1. 面包屑 `题目 / 已解决 / P0002`
2. 题面（共享题设一次）
3. 每个 part：题干锚点 + 解答 + 验证（有则显示）
4. Knowledge 列表；`[]` 用正确文案
5. 相关 Method（正文指针或后续关系投影）
6. Artifacts：仅当路径真实存在（Lean / PDF / 代码）

STUDY：折叠「解答/证明」类节，不拒绝已归档正文。  
Attempt ≠ AI Solution：分区标题写死。

### 方法 `/methods`

适用 / 意图 / 杀掉（来自正文）。不把本题附录当 Method。

### 研究 `/research`

**只映 Dossier。** 竞赛建模、文献精读、开放研究项目。  
页结构跟文件走：`problem` / `assumptions` / `model_selection` / `decisions` / `evidence` / `negative_results`。  
证据旁标 kind（COMPUTATION ≠ 证明）。无「加入题库」主按钮。

开放研究若仍是一道 `type: problem`，放在题目库，用 RESEARCH 模式阅读，不伪造 `R0003`。

### 参考 / 成果 / 记忆 / 收件箱

Phase 2 为主。Phase 1 可做只读列表 + 打开源路径。记忆页不编辑 `09_长期记忆/自动索引/**`。

---

## 6. 搜索与命令盘

`Ctrl/Cmd+K`：先搜对象，再列命令（打开知识库、切主题、最近）。

`SearchProvider`：Phase 1 本地全文（标题+正文+ID）。结果含 type、title、snippet、id。失败合法。  
未来 `SemanticSearchProvider` 替换实现，不改结果列表组件。

---

## 7. 关系与 Lean / AI（预留，少写代码）

- `KnowledgeRelation`：prerequisites / related / used-by（反查 P）。Phase 1 文本列表。
- Lean：只显示 sidecar 已有声明；Verified 仅当 gate/build 证据存在。
- `AIProvider`：Phase 1 可以没有实现；右侧不放假「已验证」。
