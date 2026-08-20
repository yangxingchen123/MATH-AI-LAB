# MATH-AI-LAB Lean / Mathlib 形式化规范

**状态：** Candidate
**上位契约：** [博士级数学研究工作台总架构](2026-08-20-doctoral-research-workbench-design.md)
**对应版本：** v1.6 Lean Formalization

---

## 1. 目标与启用边界

Lean 用于对适合的定义、引理、定理和反例进行机器检查。它是最终工作台的必备能力，但不是每个数学任务的默认步骤。

只有任务适合且用户明确要求时才启用 Lean。Lean 不可用、证明失败或 Mathlib 升级漂移不得阻塞普通数学回答、数值实验或非形式化成果。

---

## 2. 单一 Lake 工程

```text
06_LEAN形式化/
├── lakefile.toml
├── lean-toolchain
├── lake-manifest.json
├── MathAILab/
│   ├── Problems/
│   ├── Knowledge/
│   ├── Methods/
│   └── Research/
└── Tests/
```

- 全项目使用一个受控 Lake 工程，避免每个 Problem 重建环境；
- `lean-toolchain` 和 `lake-manifest.json` 固定 Lean 与 Mathlib；
- 模块按职责和依赖分层，避免循环 import 和巨型通用文件；
- 形式化文件连接已有 P/K/M ID 或项目内 Research ref，不创建重复身份；
- 工具链和缓存属于 Sidecar，不进入 Python Core 环境。

---

## 3. 形式化工作流

```text
Reviewed 自然语言命题
→ 适用性判断
→ 定义、变量、类型和量词对照
→ Lean statement candidate
→ 人工语义审核
→ 证明开发
→ lake build
→ 禁止项扫描
→ 反例/边界对照
→ Reviewed formal artifact
```

自然语言命题与 Lean 命题使用双向对照表：

| 对照项 | 必须说明 |
| --- | --- |
| 对象 | 实数、复数、有限集、拓扑空间等是否一致 |
| 量词 | 全称/存在、变量顺序和依赖关系 |
| 假设 | 显式与由 typeclass 隐含的条件 |
| 定义 | 项目定义与 Mathlib 定义是否等价 |
| 结论 | 等式、不等式、蕴含、唯一性等强度 |
| 边界 | 空集、零、端点、退化情况 |
| 经典性 | 是否依赖选择、公理化经典逻辑或不可判定性 |

`lake build` 只验证给定 formal statement，不替代该对照。

---

## 4. 形式化 Artifact Manifest

每个准备进入 Reviewed 的形式化成果扩展 Provenance Envelope：

```yaml
formal_ref: "project-local ref or existing object link"
natural_language_ref: "reviewed statement path and section"
source_files:
  - ref: "Lean file"
    sha256: "64 lowercase hex characters"
toolchain:
  lean: "exact version"
  mathlib_commit: "exact revision"
  lake_manifest_sha256: "64 lowercase hex characters"
build:
  command: ["lake", "build"]
  status: "SUCCEEDED | FAILED | CANCELLED"
  log_ref: "build log path"
semantic_review_ref: "review record"
assumptions:
  explicit: []
  imported_axioms: []
```

正式成果需要能重现构建，并能回答“证明使用了哪些非计算公理或 typeclass 假设”。

---

## 5. 硬性禁止项

正式通过的目标文件及其项目自有依赖中：

- 不得包含 `sorry`；
- 不得包含 `admit`；
- 不得新增用于绕过证明的虚假 `axiom`；
- 不得用更弱或不等价命题冒充原命题；
- 不得隐藏关键假设于未审查的局部定义；
- 不得只编译单个文件而跳过项目级 `lake build`；
- 不得在未记录升级影响时自动更新 Mathlib。

允许依赖 Mathlib 正常使用的逻辑基础，但语义审查必须披露对研究结论有实质影响的经典性或非构造性假设。

---

## 6. Mathlib 检索与复用

形式化前先检索已有定义和定理，优先复用标准库，避免平行定义。复用记录至少包括：

- 候选定义/定理全名；
- 所在模块；
- 与自然语言概念的对应；
- 所需实例和假设；
- 选择或拒绝该候选的理由。

若确需项目自定义定义，应证明与标准定义的关系，或明确它们并不等价。

---

## 7. CI 与路径过滤

Lean CI 仅在下列路径或工具链配置变化时强制运行：

- `06_LEAN形式化/**`；
- 与 Lean 适配器、manifest validator 或发布连接有关的文件；
- 上位自然语言命题发生可能影响语义的修改。

CI 至少执行：

1. 工具链版本检查；
2. `lake build`；
3. 项目自有正式目标的 `sorry` / `admit` / 新增 `axiom` 扫描；
4. manifest 完整性检查；
5. 语义 review 引用存在性检查。

路径过滤只减少无关构建，不得漏掉可能影响 theorem 的依赖变化。

---

## 8. 升级与漂移

Lean 或 Mathlib 升级作为独立变更处理：

1. 保存旧 toolchain、manifest、构建日志和通过 commit；
2. 在隔离分支更新依赖；
3. 全量构建所有正式 theorem；
4. 区分 API 重命名、证明策略变化和语义变化；
5. 对 statement diff 做人工审查；
6. 全部 Gate 通过后迁移；
7. 失败时继续使用旧锁定版本，不覆盖上次成功环境。

自动修复 tactic 或 import 后仍必须确认 theorem statement 没有被弱化。

---

## 9. 失败语义

- 证明未完成保留为 Candidate，不得标为 Reviewed formal proof；
- 构建失败保存日志和最小失败模块；
- 超时或资源不足标为 `FAILED` / `CANCELLED`，不等于命题为假；
- 发现反例时回到自然语言主张和 assumptions，不用修改 formal statement 掩盖问题；
- 引擎不可用时提供自然语言证明和测试证据，但明确未形式化；
- 已发布 theorem 因升级漂移时标为 toolchain-stale，不改写历史成功 Evidence。

---

## 10. 与 Frozen Core 和知识沉淀的关系

- Lean 文件引用 P/K/M ID，不新增同义 Registry；
- AI 生成 formalization 是 Candidate；
- `lake build` 成功只允许提升形式化 Artifact 的技术状态；
- 关联 Knowledge 的正式创建仍需用户明确说 `开始知识沉淀`；
- Problem 的目录状态、YAML status 和 Lean build status 互不替代；
- Formal artifact 失败不回写或破坏 canonical Solution。

---

## 11. v1.6 Gate

固定 Pilot 至少包含两类命题，例如代数恒等/不等式与分析/离散命题；不能只用两个结构相同的 toy theorem。

强制 Threshold：

- 固定工具链下 `lake build` 通过率 `100%`；
- 正式目标中 `sorry`、`admit` 和绕过证明的新增 `axiom` 数量 `0`；
- 自然语言—形式命题对照覆盖率 `100%`；
- source、toolchain、manifest、build log 和 semantic review provenance 完整率 `100%`；
- 已知故意弱化/遗漏假设 fixture 的检出率 `100%`；
- Lean Sidecar 失败导致普通数学路径失败的次数 `0`；
- 工具链升级失败后旧环境可恢复率 `100%`。

达到 v1.6 只证明 Lean Framework 成立；更多数学领域的覆盖按真实项目逐项提升成熟度。

---

## 12. 参考

- [Lean 项目与 Lake 文档](https://lean-lang.org/documentation/)
- [Mathlib 文档](https://leanprover-community.github.io/mathlib4_docs/)

外部文档提供工具使用方式；项目的语义门禁和成果状态以本文为准。
