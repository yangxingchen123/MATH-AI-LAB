# Human Interface v1 — 开发者架构

本文给后续 Agent：如何扩展而不把架构搞乱。

## 已经实现

只读本地数学工作台：知识 / 题目 / 方法 / 研究 Dossier / 参考 / 成果 / 学习状态 / 收件箱 / 提示词 / 仓库浏览 / Lean 证据 / Lab Candidate / 诊断 / 搜索 v2 / 最近浏览与固定（localStorage） / 关系投影 / 数学阅读。

## 没有实现（不要写成完成）

账号、云同步、数据库事实源、向量库、WebGL 图谱、厂商绑定 AI、自动写 canonical、AI 提交 Attempt、Zotero 克隆、把 Lab 升级成 Source。

## 架构边界

```text
Markdown / YAML / repo
        ↓
packages/content          只读 Adapter
        ↓
packages/domain           UI projection，不是新 Schema
        ↓
apps/web                  App Router；页面禁止 fs.readFile
        ↓
Python Core / Validator   Schema 与写入权威
```

冲突时改 UI / Adapter，不改 Frozen Schema，不改用户数学结论。

## 新增一个 Domain Object

1. 确认它**不是** Frozen K/P/M/A。不要造 `R0001`。
2. 在 `packages/domain/src/projections.ts` 加投影类型。
3. 在 `packages/content` 写只读扫描函数。
4. 把方法挂到 `ContentRepository`。
5. 加黄金测试：真实仓库对象 + 缺失字段不制造。
6. 不要把字段写进 `KNOWLEDGE_FIELDS` / `PROBLEM_FIELDS` / `METHOD_FIELDS`。

## 新增一个页面

1. 只从 `getRepository()` 取数。
2. 非法 / 哨兵 ID 走 `rejectBadId` / `requireObject` → `notFound()`。
3. 导航改 `apps/web/features/shell/nav.ts`，中文统一。
4. Empty / Loading / 404 必须有。
5. 交互状态才 `"use client"`。

## 新增一种 Content Adapter

1. 只读。`writes: false`。
2. 跳过模板、`_模板`、`derived/`、`自动索引` 按现有语义。
3. 未知 YAML 进 `unknownFields`，不升级为字段。
4. 路径用 `resolveSafeRel`，禁止 `..`。
5. Python Frozen 字段变了：`packages/content/tests/python-align.test.ts` 必须红。

## 新增 SearchProvider

当前是 `LocalSearchProvider` + 可重建内存索引（`getSearchProvider`）。

1. 实现 `SearchProvider.search(query, filters?)`。
2. 过滤器只能用真实字段：`type` / `objectStatus` / `domain`。
3. 不要加 difficulty / 假 tags。
4. 索引是派生数据，可删掉重建，不是事实源。

## 未来新增 AIProvider

1. 不要写死 OpenAI / Anthropic / Gemini。
2. 只有仓库里已有真实 integration 才做 UI。
3. 禁止 Coming Soon 空壳大面板。
4. AI 解答 ≠ User Attempt。不得自动写知识库。

## 新的 math component

1. 改 `packages/math-renderer`，不要在 React 里解析 `$`。
2. 语义块只增强**明确标记**的段落（定义/定理/证明…）。认不出就当普通 Markdown。
3. 公式错误必须隔离，不能炸整页。

## 加入 Lean evidence

1. 读 `06_LEAN形式化/correspondence.yaml` + `manifests/*.yaml`。
2. `Verified` **只**能来自 `build.status: SUCCEEDED`。
3. `.lean` 存在 → `source_exists`，不是 Verified。
4. UI 不是 verifier 权威。

## 启动与测试

```text
npm test
npm run typecheck
npm run build
npm run e2e
python -m tools.verification core
```
