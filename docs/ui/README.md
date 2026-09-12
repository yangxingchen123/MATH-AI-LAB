# MATH-AI-LAB Human Interface

**状态：** Qt Desktop Shell v0.1（主入口）+ Interactive Workbench v2 Alpha（可选网页）  
**权威：** Frozen Schema（`元数据规范.md`）> `项目规则.md` > 本文  
**禁止：** 为 UI 改 Schema；把 Markdown 迁进数据库后删源；把产品做成 Fumadocs / Notion / 博客

产品柱：**学习** · **研究** · **个人** · **高级**。读路径：Python catalog → 仓库 Markdown。写路径：Domain Operation → `tools.ui_operations` → Python Validator。

已落地：

1. 主入口 = Qt 窗口（`tools.qt_workbench`，进程内读取，无 localhost）。
2. Adapter = `packages/content`（网页）；Qt 复用 `tools.studio.catalog`（同一批 Validator parser）。
3. `/research` 只映 `07_项目/`。研究中的题仍是题目对象。
4. 写入：RecordAttempt / MoveProblemWorkflow / Create* / PromoteInboxItem / **UpdateMarkdownBody**（只改正文，YAML 不动）。Qt **操作**页与网页表单走同一网关。预览后确认。
5. `打开工作台.bat` → Qt 窗口。可选：`打开网页工作台.bat`。旧入口：`打开旧版工作台.bat`。

| 文档 | 内容 |
| --- | --- |
| [human-interface-v1.md](human-interface-v1.md) | 开发者架构：加对象 / 页面 / Adapter / Search / Lean |
| [architecture.md](architecture.md) | 分层、技术栈、目录树 |
| [information-architecture.md](information-architecture.md) | 导航、路由、页面 |
| [design-system.md](design-system.md) | 视觉原则、组件 |
| [interactive-workbench-v2.md](interactive-workbench-v2.md) | v2 Alpha 工作台 |
| [desktop-qt.md](desktop-qt.md) | Qt 桌面窗口（无端口） |
| [../research/mathematical-universe.md](../research/mathematical-universe.md) | Mathematical Universe Foundation v0.1 |
| [operations.md](operations.md) | Domain Operation 契约 |
| [security-boundaries.md](security-boundaries.md) | 写接口边界 |
| [testing.md](testing.md) | 单测 / 集成 / E2E / 不可变断言 |
| [roadmap.md](roadmap.md) | Phase 0–3 与未做项 |
| [phase-1.md](phase-1.md) | S1–S10 记录 |
| [phase-1-acceptance.md](phase-1-acceptance.md) | Phase 1.1 真验收 |
| [adr/](adr/) | 长期决策 |

启动：

```text
打开工作台.bat
python -m tools.qt_workbench launch
```

可选网页：`打开网页工作台.bat` → http://127.0.0.1:3000/
