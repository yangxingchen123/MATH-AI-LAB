# Mathematical Universe 分析（v0.1）

**状态：** 设计 / Foundation  
**不是：** Frozen Schema、不是新 YAML 对象、不是数据库事实源

---

## 当前模型限制

现有正式对象是 **Information Management Model**：

| 对象 | 职责 | 能表达 | 不能表达 |
| --- | --- | --- | --- |
| Knowledge | 审核后的知识条目 | 定义/笔记式知识点、prerequisites/related | 定理 vs 定义 vs 对象；证明对象 |
| Problem | 如何被研究/解决 | 题面、parts、workflowDir、knowledge 映射 | 猜想、反例、开放问题语义（目录 ≠ 数学状态） |
| Method | 可复用程序 | 标题、可选 knowledge | 一般化 / 特例 / 等价 |
| Attempt | 用户作答证据 | outcome、append-only ledger | 不是 Proof，更不是 Theorem |
| ResearchProject | Dossier | 项目过程文件 | 不是数学实体类型 |
| LabRecord | Research Lab Candidate | 实验/猜想草稿 | **永远不是**正式 Source |
| LeanTheorem | correspondence + manifest | Source Exists ≠ Verified | 只有 SUCCEEDED 才是形式证据 |
| Artifact | `08_成果输出/` | 文件存在 | 不是命题为真 |

关系目前只有：

- Explicit：YAML `prerequisites` / `related` / `knowledge`
- Derived：反向 used-by、共享 knowledge 的方法/题目

缺：`proves`、`contradicts`、`verified_by`、证据对象、候选生命周期、思想演化。

因此系统擅长 **管理学习材料**，还不擅长 **保存数学世界**。

---

## 未来模型设计

基本单位改为 **Mathematical Entity**（投影，不是文件）：

Definition · Object · Statement · Theorem · Lemma · Conjecture · Question · Proof · Counterexample · Experiment · Evidence · Artifact · FormalProof

权威仍是仓库 Markdown / YAML / Lean。Entity 由 Adapter + `packages/domain-math` **运行时投影**。

分层：

```text
Canonical Source (Frozen K/P/A/M + Lean + Dossier + Lab Candidate)
        ↓ 只读投影
Mathematical Entity / Relation / Evidence / Event / Space
        ↓ 只读视图
/universe  ·  未来 Research Intelligence
        ↓ 若要进入 canonical
Human Review → Domain Operation → Validator
```

---

## 哪些可以 projection，哪些才可能 future canonical

| 概念 | v0.1 | 将来 canonical？ |
| --- | --- | --- |
| Knowledge → Definition | 投影 | 否。K 仍是 KM 对象。不得把 reviewed Knowledge 写成 Theorem |
| Problem → Question | 投影 | 否。P 仍是题目。开放问题语义另议 |
| Method → Object（程序对象） | 投影 | 否。不新增 Method YAML 字段 |
| Attempt → Evidence(HumanProof) + Event(ProofAttempt) | 投影 | Attempt Schema 已 Frozen，不改 |
| Lean Verified → FormalProof + Evidence(LeanProof) | 投影 | Lean 仍走现有 sidecar；Verified 仍要证据 |
| Lab conjecture → Candidate(Conjecture) | 投影 | Lab **永不**升为 Source |
| Theorem / Lemma / Proof / Counterexample | 类型占位；**当前仓库几乎投不出 Theorem** | 仅当未来有明确 Frozen 或 Operation 时 |
| `proves` / `contradicts` | 类型存在；现有数据几乎不产生 | 禁止从 Attempt.correct 推断 Theorem |
| ResearchSpace | 由 Knowledge.domain / 研究项目 slug 投影 | 不是文件夹 Schema |
| Candidate Promoted | 状态机停在 Candidate 层 | 写入必须新 Operation；v0.1 **不实现写入** |

---

## 迁移策略

1. **不迁移文件。** 不改 `01_` `02_` `12_` YAML。
2. **不改 Frozen Schema。** 不为 Definition/Theorem 增加 status。
3. **双轨并存：** KM 对象继续服务学习工作台；Universe 是其上的数学投影。
4. **禁止自动识别** 正文里的「定理/引理」为 Entity（会污染）。只有明确源对象才投影。
5. 将来若要 Theorem 正式化：先 Schema 治理 → Operation → Validator。不是先改 UI。

---

## 风险

| 风险 | 对策 |
| --- | --- |
| 把投影当成第二套 Schema | 文档与类型标明 projection；无 YAML writer |
| Knowledge.reviewed → Theorem | 映射到 Definition，永不 Theorem |
| Attempt.correct → Proof completed | 只生成 HumanProof evidence + ProofAttempt 事件 |
| Lab → 正式猜想对象 | `candidate: true` 固定；UI 标明 Candidate |
| AI confidence = 真 | Evidence.confidence 禁止 ai_true；Mock AI 只产 Candidate |
| 图数据库 / 向量库 | 内存 Graph Projection，不写回 |
| 导航爆炸 | 三柱不变；猜想/实验/时间线先 disabled；只开 `/universe` 原型 |
| 为关系改 Frozen 字段 | 只用已有 explicit 字段 + 安全 derived |
