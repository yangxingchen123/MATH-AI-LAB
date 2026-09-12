# Entity 模型（投影）

`MathematicalEntity` 在 `packages/domain-math`。**不是数据库表，不是 Frozen YAML。**

## 字段

`id` `title` `type` `description` `source` `status` `created` `updated`

`id` 形如 `question:problem:P0002`，稳定、可编码进 URL。

`source` 指向既有对象：`knowledge` / `problem` / `method` / `attempt` / `lean` / `lab` / `research` / `output`。

`status` 是投影状态，不是 YAML `draft|reviewed|archived`：

- `projected` — 从正式 KM 对象映出
- `candidate` — Lab / Mock AI 等非正式源
- `supported_by_evidence` — 有人类或计算证据，**仍不是 Theorem**
- `formal_verified` — 仅 FormalProof 且 Lean manifest SUCCEEDED

## 类型与当前映射

| type | 当前源 | 备注 |
| --- | --- | --- |
| definition | Knowledge | 不升级为 theorem |
| object | Method | 可复用程序，不是集合论对象声明 |
| question | Problem | workflowDir 不改数学真值 |
| formal_proof | LeanTheorem | Verified 需要证据 |
| conjecture | Lab kind=conjecture | 永远 candidate |
| experiment | Lab 非 conjecture 记录 | 永远 candidate |
| artifact | OutputArtifact | 文件存在 |
| theorem / lemma / proof / counterexample / statement | 占位 | v0.1 不从正文自动抽取 |

禁止：把 `knowledge: []` 显示成「尚未定义」。
