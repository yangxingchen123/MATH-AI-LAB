# MATH-AI-LAB Normal Operation Guide

本文件是 **Normal Operation Mode** 的使用规范，不是 Schema、不是 Registry、不是新框架。

基础设施已 **FROZEN**。默认做真实数学任务，不为了“还能优化什么”改系统。

---

## AUTO

用户：

直接求解问题

交付 `02_题目库/` Problem md，或按题目模板填写且 `## 题目` 已有实质内容

行为：

直接回答。先按 `项目规则.md` 第四节 §0 分流种类。习题/定理走：重构 → 受控检索 → 方法押注 → 证明本题 → 分流落盘。建模走选模与 Dossier，不走「证明本题」。详略随难度缩放。不得先搜背景再开方法课；不得把启发式写成定理；不得把每个问题都写成「已完全解决」；K/M 不自动创建。

题库 md：解答全部小问（所有 `parts`）。空模板除外。不共享题设的独立题对话里全做，落盘时一题一 P。

已有 Problem：

canonical Solution
+
reconcile

不要：

自动创建 Attempt。

入口：`persist_canonical_solution_op(...)`（WRITTEN/CORRECTED 才 source finalize；NO_OP 仍 reconcile）。

---

## REVIEW

用户：

提交自己的答案/证明

行为：

创建 User Attempt。

必须区分：

User Attempt

和

AI Solution。

参考答案：

NO Attempt。

用户作答：`record_user_attempt_op(...)`。批改可以给 AI 解答，但那不是 Attempt。

---

## STUDY

用户：

自己做，只需要提示。

行为：

一个 episode = 一个 Attempt。

结束：

freeze Attempt

如果用户要求：

切换 AUTO

完成 Solution。

入口：STUDY episode 用 Attempt；切换 AUTO 后用 `persist_canonical_solution_op`（或 `study_to_auto_op` 链）。不得把提示过程拆成多个 Attempt。

---

## Research

研究型任务：

允许长期 Problem。

自动保存：

Problem progress

但：

不要自动创建 K/M。

知识沉淀与正式讲义只在用户明确授权后进行。

---

## P4 Error Diagnosis

保持：WAITING / EVENT-DRIVEN。

现在不要创建 Error Mode、EM001、Error Registry。

只允许从 Attempt narrative 观察重复错误。同类错误约 3–5 次后再讨论 P4。

---

## Failure Handling

发现问题后不要立即扩展架构。先分类：

- P1：状态漂移
- P3：Problem workflow
- P4：错误模式
- P9：Artifact

只修对应范围。

---

## Infrastructure Freeze

任何修改必须先回答：

1. 真实用户任务是否阻塞？
2. 已有能力是否无法解决？
3. 是否可以最小修改？

任一为 NO，则不要修改。

禁止：P11、新 Schema/Registry/DB、新 Agent Framework、改 Frozen Schema、改 Attempt identity、改 P9 architecture、改 ElegantBook vendor source、RAG / Multi-Agent / Lean / 自动证明系统。

---

## LaTeX 依赖

Problem Artifact：不得包含 `elegantbook.cls`；由 P9 注入 pinned ElegantBook v4.7。

Knowledge Document / 长期讲义：允许暂时 self-contained；不要为了统一而改稳定资产。

---

## Burn-in

用真实数学任务收集运行证据（不是测试数据）：AUTO、REVIEW、STUDY、Problem creation、PDF generation。观察输入、模式、mutation、artifact、reconcile、是否 drift。目标约 10 个真实任务。
