# 测试

## 命令

```text
npm test
npm run typecheck
npm run build
npm run e2e
PLAYWRIGHT_VISUAL=1 npm run e2e:visual
python -m pytest -q tests/ui_operations
python -m tools.problem_validator check
python -m tools.knowledge_validator check
python -m tools.method_validator check
python -m tools.verification core
python -m pytest -q tests/studio tests/lean_formalization tests/qt_workbench
```

## 分层

| 层 | 位置 | 覆盖 |
| --- | --- | --- |
| Domain | `packages/domain/tests` | mapping、ID、resolveContentRef |
| Domain-math | `packages/domain-math/tests` | Entity / Relation / Evidence / Candidate / Graph（合成对象，不测真实数学） |
| Qt workbench | `tests/qt_workbench` | 无端口、三柱导航、P0002 StatusPair、阅读页 HTML 非源码；无 PySide6 时跳过窗口测试 |
| Content | `packages/content/tests` | golden、Python 对齐、search、关系、Lean、不可变 hash |
| Math | `packages/math-renderer/tests` | 公式隔离、语义块、broken-ref |
| Operations | `tests/ui_operations` | preview / persist / invalid / 全流程（仅 tmp_path） |
| Web | `apps/web/tests` | 导航、404 语义、TOC、origin 白名单 |
| E2E | `e2e/core.spec.ts` | 路由、键盘搜索、Attempt 预览（不 persist）、Lean |
| Visual | `e2e/visual.spec.ts` | 少量 layout baseline（默认跳过） |

## 黄金对象

真实仓库：P0001、P0002、K0001、K0002、M0001、M0002、`07_项目/美赛2026-A`、`03_参考资料/竞赛/美赛/2026-A`、Lean ALG-001 manifest。

不要把假对象复制进生产目录。

## 不可变

`packages/content/tests/phase2.test.ts` 在投影前后 hash：

`01_知识库` `02_题目库` `07_项目` `12_方法库`

## CI

- `core-verification.yml`：Python Core。Web 失败 ≠ Core FAIL。
- `web.yml`：`web` job（test / typecheck / build）+ `web-e2e` job。
- `lean.yml`：Lean sidecar。
