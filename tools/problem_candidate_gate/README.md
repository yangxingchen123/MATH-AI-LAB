# Problem Candidate Gate v0.1

> **DEPRECATED** — superseded by [`tools/problem_validator/`](../problem_validator/) (Problem Validator v1, Frozen Problem Schema v1, 2026-08-19). Retained as migration regression oracle only.

Problem Candidate Gate v0.1 is a **temporary pre-freeze quality gate** for Problem Schema v1 Candidate. **It is not the formal Problem Validator v1.**

中文：这是 Problem Schema v1 Candidate 冻结前的临时机械门禁，不是正式 Problem Validator v1。Schema Frozen 后请使用 `python -m tools.problem_validator check`。

## 用途

检查当前 Candidate 已足够明确、可以机械检查的规则：

- YAML 解析
- P ID 合法性与唯一性
- 禁止真实对象使用 `P0000`
- 基础字段与日期
- `knowledge` Candidate 规则（含 reviewed 允许 `[]`）
- Knowledge target 存在性（依赖 Knowledge Validator v1.1）
- `parts` 结构（Candidate v0.1 **PROVISIONAL** 规则）
- Legacy filename / Content Review marker（WARNING）

不检查题面数学正确性、证明完整性或 mastery。

## 原则

- Read-only
- Deterministic
- **no `--fix`**
- **no ID allocation**（`--next-id` / `--allocate-id` 不提供）
- **no status mutation**（不会 `draft` → `reviewed`）
- **no Knowledge creation**
- **no Schema mutation**
- **no `--strict-warnings`**（Candidate 阶段允许合理 WARNING）

## CLI

```text
python -m tools.problem_candidate_gate check
python -m tools.problem_candidate_gate check-file <PATH>
python -m tools.problem_candidate_gate status
```

公共参数：

- `--root <PATH>`
- `--format text|json`
- `--summary`（仅 text）
- `--verbose`

扫描范围：`02_题目库/**/*.md`。  
**按路径排除** `02_题目库/题目模板.md`（不按 `P0000` skip）。真实对象使用 `P0000` 为 ERROR。

`check-file` 使用全库 Candidate 上下文（可发现重复 P ID），并依赖 Knowledge registry。

## check vs status

| 命令 | 职责 | 退出码 0 |
| --- | --- | --- |
| `check` | 仅机械 Candidate validation | 无 ERROR |
| `check-file` | 单文件 + 全库上下文 | 无 ERROR |
| `status` | check + readiness + **Manual Review** 清单 | `READY_FOR_FINAL_REVIEW` 或 `READY_WITH_WARNINGS` |

WARNING 默认不导致 `check` 失败。

`status` 的 Automated Gates 与 Manual Review Items **分开**。机器不能自动关闭人工项。即使输出 `READY_FOR_FINAL_REVIEW`，也 **不是** Schema Frozen。

Readiness 枚举：

- `READY_FOR_FINAL_REVIEW`
- `READY_WITH_WARNINGS`
- `NOT_READY`

没有 `FROZEN_READY`。

## Candidate-only 规则

例如 `parts` 至少 2 项属于 **Candidate v0.1 provisional**，不是 Frozen Schema contract。Final Review 可能调整。

## Knowledge 依赖

Gate 调用 Knowledge Validator v1.1 公共 API。若 Knowledge 本身 ERROR，Gate 报告 `PCG-KNOW-E010`（DEPENDENCY FAILED），不再把 Knowledge 关系当可靠数据。

## JSON

`--format json` 顶层包括 `gate_version`、`candidate_schema`（`status: candidate`）、`summary`、`automated_gates`、`issues`。`status` 另含 `manual_review_items` 与 `result`（readiness）。
