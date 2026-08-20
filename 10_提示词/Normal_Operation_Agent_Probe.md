# Normal Operation v1 — Agent Contract Probe

本文件记录 **AI semantic layer** 入口与 **deterministic operation layer** 的对应关系。  
不是 Prompt Test Framework；供 Agent 与人工验收参照。

---

## Probe A — AUTO existing Problem

**输入语义：** 「直接解答 P0002(a)」

**期望：**

- Mode: AUTO
- Operation: `persist_canonical_solution_op(problem_id="P0002", part="a", ...)`
- Attempt: NONE
- Finalizer: 仅当 `persistence=WRITTEN` 时自动 `changed=["problem"]`；NO_OP 不触发 finalizer

---

## Probe B — REVIEW / User

**输入：** 「这是我自己写的 P0002(a)，帮我检查」

**期望：**

- Mode: REVIEW
- Authorship: user（语义层判定）
- Operation: `record_user_attempt_op(...)` → exactly one Attempt
- AI correction: 不创建第二个 Attempt

---

## Probe C — REVIEW / Reference

**输入：** 「这是参考答案，帮我看看」

**期望：**

- Mode: REVIEW（数学批改）
- Attempt: NONE（不调用 `record_user_attempt_op`）

---

## Probe D — REVIEW / Unknown Source

**输入：** 来源不明确

**期望：**

- Attempt: NONE（默认不记录）

---

## Probe E — STUDY

**输入：** 「我自己做，先别给答案」

**期望：**

- Mode: STUDY
- 不泄露完整答案；episode 结束前不 persist Attempt

---

## Probe F — STUDY → AUTO

**多轮 solving 后输入：** 「算了，直接告诉我答案」

**期望：**

- Operation: `study_to_auto_op(...)` 
- Attempt delta: +1
- Solution: canonical upsert
- Finalizer: `changed=["attempt","problem"]`（按实际 mutation）
- AI full solution: 不创建第二个 Attempt

---

## Probe G — Temporary Question

**输入：** 「这个怎么做？」（无 P ID、无建档授权）

**期望：**

- 完整数学回答
- **不**调用 `persist_*` / `record_*` / `finalize`

---

## Probe H — Explicit PDF

**输入：** 「解答并整理成 PDF」（已含 artifact 授权）

**期望：**

- 不再二次确认
- Operation: `publish_pdf_op(...)`（P9 reuse）
- Artifact: COMPLETE on success

---

## RESEARCH Boundary

- 可更新 Problem research body + finalize
- **MUST NO** 自动创建 K / M / Error Mode
