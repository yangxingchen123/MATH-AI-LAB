# Domain Operations

## 为什么不能直接写 Markdown

页面和 React 不拥有 Frozen Schema。直接 `PUT` 一个 `.md` 会绕过 uniqueness、reserved ID、Attempt ledger、workflowDir ≠ objectStatus、Method `knowledge: []` 非法等规则。

写入必须是具名 Domain Operation，由 Python 分配 ID、渲染 Frozen 字段、跑 Validator。

## Web 如何调用 Python

```text
POST /api/operations
  { version: 1, operation, preview, requestId, payload }
        ↓
apps/web/src/lib/python-bridge.ts
        ↓
python -m tools.ui_operations run --root <server-resolved>
        ↓
tools/ui_operations/gateway.py
```

`--root` 只由服务器 / 测试设置，来自 `MATH_AI_LAB_ROOT` 或仓库发现。客户端 payload 不得带 `root` / `path` / `command`。

## Preview / Persist

高价值写入先 `preview: true`。Create* 会把候选写入目标路径、跑 Validator、再删除候选。`UpdateMarkdownBody` 在 preview 时同样写完即还原。Persist 才保留文件。

`UpdateMarkdownBody` 只替换 Markdown 正文，原样保留 YAML Front Matter。payload 只有 `objectType` + `objectId` + `body`，不得带 `path` / `file`。

UI 必须先预览再「确认写入」。不得单击即 persist。

## Operation Result

至少包含：`success` `operation` `affected_objects` `validation` `warnings` `changed_files` `planned` `issues` `error`。

`validation` 为 `FAIL` 时不得显示保存成功。Create* 失败会删掉候选文件。

## 新增 Operation

1. 先确认已有 Python Layer 2 / Validator 能表达该行为。
2. 加入 `tools/ui_operations/constants.py` 与 `packages/domain/src/operations.ts` 白名单。
3. payload 只收稳定对象 ID 与 Frozen 字段。
4. 在 `tests/ui_operations/` 用 **tmp_path** 测 preview / persist / invalid / changed files。
5. 不要为此改 Frozen Schema。
