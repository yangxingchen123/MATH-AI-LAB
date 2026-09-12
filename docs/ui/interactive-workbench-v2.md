# Interactive Workbench v2 Alpha

把 Human Interface v1 的只读阅读面，接上受控写入。

一个人可以：打开题目 → 记录 Attempt → 移动 workflowDir → 创建 K/P/M → 从 Inbox 提升 → 看到 validation 与 changed files。

权威不变：

- 仓库 Markdown / YAML 是事实源
- Python Validator / Layer 2 是 Schema 与写入权威
- `packages/content` 仍是只读投影
- Web 不得 `fs.writeFile` canonical 数据
- 禁止通用文件 CRUD API

写入路径：

```text
UI form
  → Preview
  → POST /api/operations（白名单）
  → python -m tools.ui_operations
  → 已有 Layer 2 或薄 create wrapper
  → Validator
  → 确认后 persist
```

六个 Domain Operation：

`RecordAttempt` `MoveProblemWorkflow` `CreateProblem` `CreateKnowledge` `CreateMethod` `PromoteInboxItem`

网页表单与 Qt **操作**页都调用同一 Python 网关。Inbox 提升成功后**不移动、不删除**原文件。现有规则没有 promote-archive operation。

Attempt 只接受用户作答；append-only。v2 Alpha 不做 canonical delete，也不做通用 Markdown 编辑器。
