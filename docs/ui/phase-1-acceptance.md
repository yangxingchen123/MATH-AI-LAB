# Phase 1.1 验收

**日期：** 2026-09-09

## 修复

| 项 | 结果 |
| --- | --- |
| HTTP 404 | 哨兵 ID / 非法路径走 middleware rewrite 404；缺失对象 `notFound()` |
| Python Core | `workspace_indexer/renderer.py` f-string 改为 3.11 兼容；`python -m tools.verification core` 为正式环境目标 |
| Playwright | `e2e/core.spec.ts` 覆盖核心路由、404、搜索、移动导航、Lean 文案 |
| Visual | `e2e/visual.spec.ts` 需 `PLAYWRIGHT_VISUAL=1`，避免 CI 因 OS 像素差随机失败 |
| Launcher | 检查 Node / 依赖 / build / 端口 3000 复用；失败回退 studio |

## 未再当作「旧问题」的项

- Core verification 语法
- 404 语义
- 导航中英混用（现已中文分组）
