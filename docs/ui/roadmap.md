# 路线、风险、Fumadocs 取舍

Phase 1（S1–S10）与 Human Interface v1（Phase 1.1 + 2 + 3A）已落地，见 [human-interface-v1.md](human-interface-v1.md)。未做：账号、云、厂商 AI、图谱 WebGL。

---

## Phase 0 — 理解与设计（本目录）

已完成：扫描仓库与 Frozen Schema；写出架构 / IA / 设计系统 / 本路线。  
出口：你确认 Adapter 方案、研究路由范围、studio 是否过渡保留。

---

## Phase 1 — MVP（确认后）

**已完成（2026-09-09）。** 只读 Human Interface 可日常使用。未做账号、图谱、写 YAML、假 Verified、难度筛、文献管理器。

---

## Phase 2 / Workbench v2 Alpha

已完成只读模块，以及受控写入：RecordAttempt、MoveProblemWorkflow、CreateProblem / Knowledge / Method、PromoteInboxItem。  
写入仍仅经 Domain Operation，不经通用文件 API。

---

## Phase 3A

已完成本地：Lean 证据 UI、Dossier timeline/evidence、Lab Candidate、Diagnostics、派生搜索索引。  
未做：绑定外部 AI、语义向量检索、WebGL 关系图。

---

## Mathematical Universe Foundation v0.1

已完成：`packages/domain-math` 投影、Evidence / Candidate / Timeline、只读 `/universe`。  
未做：Candidate 写入 canonical、真 AI、图数据库、新 YAML 对象类型。

---

## 风险

| 风险 | 对策 |
| --- | --- |
| 把工作流目录当成 YAML status | `StatusPair`；测试锁定 P0002 |
| 为 UI 加 tags/difficulty | 拒；过滤只用 Frozen 字段 |
| 把美赛做成 P | `/research` 无「加入题库」 |
| Fumadocs 内容目录绑架仓库 | 不用其 content source |
| TS Adapter 与 Python 漂移 | 黄金文件测试 |
| 公式炸页 | ErrorBoundary + fixture |
| 前端 CI 拖垮 Core | 独立 workflow |
| Attempt 被 AI 写入 | Phase 1 只读；写入走 Ledger API |
| 过早 packages 爆炸 | 组件先放 apps/web |

---

## 参考 Fumadocs 的

Docs 三栏、侧栏层级、TOC、命令搜索、面包屑、正文宽度、主题、响应式、MDX 组件化 **思路**。

## 绝对不照搬的

- 核心对象是 Document / `content/docs`
- 把 `01_知识库` 改造成 Fumadocs 文件夹约定
- 用其默认博客/文档首页
- 依赖其 i18n/版本 tabs 当数学领域树
- 复制其品牌与组件源码当自己的设计系统

MATH-AI-LAB 的核是：**Knowledge、Problem、Proof、Dossier、Artifact、Learning State**，其上再投影 **Mathematical Entity**。

---

## 现有 `tools.studio` 怎么处置

保留为无 Node 回退。`打开旧版工作台.bat` 与 `python -m tools.studio launch` 仍可用。正式数据层不是 studio JSON。
