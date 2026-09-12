# AI 边界

本阶段 **不实现 LLM**。只有 `AIResearchProvider` mock。

## AI 可以

- read 投影（Entity / Relation / Evidence 的只读视图）
- analyze（在 mock 里返回固定结构）
- suggest → **Candidate**（status=`idea`）
- critique / search / formalize → 同样只返回 Candidate 或评语字符串

## AI 不可以

- modify canonical Markdown / YAML / Lean
- declare theorem
- 写 Attempt ledger
- delete history
- change evidence
- 把 confidence 写成数学真值
- 绕过 Domain Operation

## 未来接入

```text
AI Action → Candidate → Human Review → Domain Operation → Validator → Canonical
```

任何真实 Provider 必须实现同一接口；默认实现是 `MockAIResearchProvider`。
