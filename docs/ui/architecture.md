# UI 总体架构

**状态：** Interactive Workbench v2 Alpha + Mathematical Universe Foundation v0.1  
**原则：** Content First。仓库里的 `.md` / `.yaml` / `.tex` / `.lean` / `.pdf` 仍是事实源。UI 是视图。

---

## 1. 当前仓库结论（扫描摘要）

| 事实 | 含义 |
| --- | --- |
| 已有 `apps/web` + `packages/*` | 正式 UI；写入走 Domain Operation |
| 根依赖只有 PyYAML + pytest | Node 必须隔离，不得进根 `requirements.txt` |
| Frozen：K / P / A / M | UI 只能 Adapter 映射，不能加 `difficulty` / `tags` / `research_status` 到 YAML |
| Problem `status` ≠ 目录 `未解决/研究中/已解决` ≠ Attempt | 界面必须三列，禁止合并成一枚徽章 |
| Research / Ordinary 共用 `type: problem` | `/research` 不是新 Schema 类型 |
| 竞赛整卷在 `07_项目/` | 不是一道 P |
| `tools.studio` | stdlib 只读原型（S0/S1）；可保留为无 Node 回退 |
| `tools.workbench` | 竞赛实验编排，与 Web UI 模块名不得混用 |
| CI | Python Core + 各 sidecar smoke；尚无前端 CI |
| 真实对象很少 | P0001/P0002、K0001/K0002、M0001/M0002、美赛2026-A、PROB-SF-001 |

Validator / Indexer / Normal Operation / Lean / Retrieval 已存在。UI **复用**它们的语义，不重写一套解析器当权威。

---

## 2. 分层（必须）

```text
仓库 Source（01/02/07/12/03/08/09 …）
        ↓
Content Adapter          ← 只读；认识 Frozen 字段与工作流目录
        ↓
Domain Model             ← UI 用的 K/P/M 对象；≠ 改 Schema
        ↓
domain-math Projection   ← Mathematical Entity / Relation / Evidence（只读，不写回）
        ↓
Application Query        ← list / get / search
        ↓
Human Interface          ← 含 /universe 原型

Human Interface
        ↓
Domain Operation Request
        ↓
POST /api/operations（白名单）
        ↓
tools.ui_operations → Layer 2 / Validator
        ↓
Canonical Repository
```

禁止组件直接读文件系统。禁止把 OpenAI / 向量库写进 Frozen Schema、Domain Operation 或正式 Source。本机 GPT 接入是 sidecar：密钥只在 gitignore 的 `.mathailab/credentials.json`，由 `tools.qt_workbench.gpt_client` 用标准库调用 Chat Completions。

### Domain Model（视图层，不是新 Schema）

共用 `ContentRef`：`id`、`title`、`type`、`objectStatus`、`sourcePath`、`createdAt`、`updatedAt`。

| UI 类型 | 仓库权威 | 额外只读投影 |
| --- | --- | --- |
| `Knowledge` | K YAML + 正文 | `domain`、`aliases`、`prerequisites`、`related` |
| `Problem` | P YAML + 正文 | `workflowDir`、`parts`、`knowledge[]`；**无** difficulty/tags |
| `Method` | M YAML + 正文 | `knowledge[]` |
| `Attempt` | Ledger（用户） | 只展示，UI 不伪造 |
| `ResearchProject` | `07_项目/` Dossier | `kind`：research / literature / contest_modeling |
| `Reference` | `03_参考资料/` | 身份文件；不做成完整文献管理器 |
| `Artifact` | `08_成果输出/` + LaTeX 工程 | Preview / Download |
| `LearningState` | `09_长期记忆/` | 派生页，不手改 GENERATED |
| `InboxItem` | `00_收件箱/` | 浏览；写入另议 |
| `LabRecord` | `tools.research_lab` | 校准，非正式 Source |

用户清单里的 `idea / exploring / formalizing / verified` **不得**写成 Problem YAML。研究进度只从 Dossier 文件是否存在、决策记录、Lean sidecar、工作流目录 **投影**。对不上的状态显示为「未记录」，不准编。

`reviewed` + `knowledge: []` 的文案必须是：「mapping 已完成，当前没有直接对象」。禁止写成「还没关联」。

---

## 3. Content Adapter

职责：扫允许的根、解析 YAML Front Matter、丢掉未知字段（或标 non-schema）、拆 `parts` 正文、抽标题、抽公式、解析内部 ID 链接。

权威规则复制自 Frozen Schema + 现有 Python parser，并用 **同一批真实文件做黄金测试**（P0001、P0002、K0001）。Adapter 与 Validator 冲突 → 改 Adapter。

**已确认 Adapter A：** `packages/content` 直接读仓库。不经过 `tools.studio` JSON。

职责只有：Repository → Parse → 投影到 `packages/domain`。  
不是新 Schema 权威。未知 YAML 键进入 `unknownFields`，不得变成正式字段。  
与 Python Validator 冲突 → 改本 Adapter。

写入不得从 JS 改 YAML。只许 Domain Operation → `tools.ui_operations` → 已有 Layer 2（如 `record_user_attempt_op`、`move_problem_to_workflow`）或经 Validator 的薄 create wrapper。详见 [operations.md](operations.md)。

---

## 4. 技术栈（推荐，待确认）

| 层 | 选择 | 不选 |
| --- | --- | --- |
| 应用 | Next.js App Router + TypeScript | 把 Fumadocs 当产品框架 |
| 样式 | Tailwind + 自己的 token | 营销风组件库 |
| 数学 | KaTeX（可继续 vendor）+ `MathErrorBoundary` | 无容错的全局 MathJax |
| 内容 | 自研 MD 管线（GFM + math + callout） | 把仓库迁成 Fumadocs `content/docs` |
| 搜索 | `SearchProvider`；Phase 1 本地索引 | 组件写死 FlexSearch 细节 |
| 主题 | light / dark / system | 仅靠 CSS 滤镜倒公式颜色 |
| 测试 | Vitest + 黄金 MD fixture；Python 仍测 Schema | 只在浏览器里肉眼看公式 |

不在根 `requirements.txt` 加 Node。`apps/web` 自有 `package.json`。

**不锁死：** 以后 Adapter 可改读 SQLite / API，Shell 不必重写。

---

## 5. 建议目录树（确认后才建）

不机械铺 `packages/*`。第一刀只建用得上的：

```text
MATH-AI-LAB/
  00_收件箱/ … 12_方法库/     # 不动；仍是 Source
  tools/                      # Python 权威：validator / studio / retrieval …
  apps/
    web/                      # 正式 Human Interface（确认后创建）
      app/                    # 路由
      features/
        shell/
        home/
        knowledge/
        problems/
        research/
        search/
      components/             # 纯 UI
      src/providers/          # Search / Theme / 未来 AI
  packages/
    content/                  # Adapter + 黄金测试
    domain/                   # 纯类型与映射函数，无 React
    domain-math/              # Mathematical Entity 投影；不写仓库
    math-renderer/            # KaTeX + ErrorBoundary
  docs/ui/                    # 本设计
```

`tools/studio` 保留：无 Node 时的只读回退。不把 Studio 和 `tools.workbench` 合并。

暂不建：`packages/ui` 独立包（Phase 1 组件先放 `apps/web/components`，稳定再拆）。

---

## 6. 与现有脚本 / CI

- Core CI 继续只跑 Python。前端另加 `apps/web` workflow，失败 **不得** 标 Core FAIL。
- Lean Verified 只认 `tools.lean_formalization` / lake 证据，禁止 UI 用模型输出点绿灯。
- 检索以后接 `tools.retrieval`，向量未装则为 DEGRADED，页面仍能打开。

---

## 7. 已确认决策

1. Adapter **A**：`packages/content`。`tools.studio` 仅 fallback / 原型。
2. `打开工作台.bat`：Qt 桌面窗口。可选 `打开网页工作台.bat`。`打开旧版工作台.bat` 仍打开 studio。
3. `/research` **只** 映 `07_项目/`。`研究中/` 里的题仍是 Problem。
