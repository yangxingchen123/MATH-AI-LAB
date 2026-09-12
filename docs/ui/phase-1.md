# Phase 1 实施阶段

**状态：** Phase 1 **完成**（2026-09-09）  
**决策：** Adapter = TypeScript `packages/content` · `/research` 只映 `07_项目/` · 工作台入口已切到 `apps/web`，studio 保留回退

权威：Python Validator / Frozen Schema。TS 冲突时改 TS。Phase 1 只读。写入见 [interactive-workbench-v2.md](interactive-workbench-v2.md)。

| 阶段 | 状态 | 实现 | 测试 / 验收 |
| --- | --- | --- | --- |
| S1 | 完成 | `packages/domain` + `packages/content` | golden + Frozen 字段对齐 |
| S2 | 完成 | `packages/math-renderer`（KaTeX + 公式级错误隔离） | 11 fixture 测试 |
| S3 | 完成 | `apps/web` App Shell、顶栏、侧栏、TOC、主题 | 首页 200；无 Hero |
| S4 | 完成 | `/knowledge` `/methods` | K0001/K0002/M0001/M0002；YAML 不进正文 |
| S5 | 完成 | `/problems` + parts + Attempt ledger | P0002 三问；`knowledge: []` 文案正确 |
| S6 | 完成 | `/research` ← `07_项目/` | 美赛2026-A；无 R Schema |
| S7 | 完成 | `LocalSearchProvider` + Ctrl/Cmd+K + `/search` | 中英检索；排除模板 |
| S8 | 完成 | 首页真实计数 | 无假 KPI |
| S9 | 完成 | 深色/系统主题、抽屉、公式/表横滚、error/404 | 生产构建通过 |
| S10 | 完成 | `.github/workflows/web.yml`；launcher 切换 | `npm test` / `typecheck` / `next build` |

**已知限制（Phase 1 当时；1.1 已修）**

见 [phase-1-acceptance.md](phase-1-acceptance.md)。
