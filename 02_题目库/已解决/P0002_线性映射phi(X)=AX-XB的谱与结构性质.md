---
schema_version: 1
id: P0002
type: problem
title: 线性映射 φ(X)=AX-XB 的谱与结构性质
status: reviewed
created: 2026-08-19
updated: 2026-08-20
knowledge: []
parts:
  - a
  - b
  - c
---

# 线性映射 φ(X)=AX-XB 的谱与结构性质

> Candidate Content Review: COMPLETE（2026-08-20）

## 题目

**原题陈述（保留）：** 设 $A$、$B$ 为 $n$ 阶实矩阵。考虑线性映射

$$\varphi(X)=AX-XB.$$

**(a)** 求证：若 $\lambda_1$ 是 $A$ 的特征值，$\lambda_2$ 是 $B$ 的特征值，则 $\varphi$ 有特征值 $\lambda_1 - \lambda_2$。

**(b)** 若 $A$、$B$ 矩阵均可对角化，求证：$\varphi$ 可以对角化。

**(c)** 若 $A$、$B$ 矩阵没有公共特征值，求证：$\varphi$ 是单射。

---

**Content Review 工作假设（用于 (a)(b)(c) 的统一推理语境）：**

原题未指定 $\varphi$ 的定义域、值域，也未指定谱/特征值所在的标量域。下列为 Content Review 后采用的 **Working assumption**（非对原题来源的外部断言）：

| 项目 | 约定 |
| --- | --- |
| 矩阵尺寸 | $A,B\in M_n(\mathbb{R})\subseteq M_n(\mathbb{C})$；$X\in M_n(\mathbb{C})$ |
| $\varphi$ 的定义域 | $M_n(\mathbb{C})$ |
| $\varphi$ 的值域 | $M_n(\mathbb{C})$ |
| $\varphi$ 的线性性 | $\varphi(\alpha X+\beta Y)=\alpha\varphi(X)+\beta\varphi(Y)$（标准矩阵运算） |
| 谱 / 特征值 | 在 $\mathbb{C}$ 上理解：$\lambda$ 为 $A$ 的特征值 $\Leftrightarrow\exists u\neq 0$ 使 $Au=\lambda u$（$u\in\mathbb{C}^n$） |
| $\varphi$ 的特征值 | $\varphi$ 作为 $M_n(\mathbb{C})$ 上线性算子的特征值 |
| (c) 公共特征值 | $\mathrm{spec}_{\mathbb{C}}(A)\cap\mathrm{spec}_{\mathbb{C}}(B)\neq\varnothing$ 的否定 |

**说明：** 在 $F=\mathbb{R}$ 上，实矩阵未必有实特征值；若仅在 $\mathbb{R}$ 上取特征向量，(a)(b)(c) 的表述与证明步骤不能普遍成立。Content Review 结论：三小问在 **复化语境** 下理解与证明；这不等同于声称「原题一定只在 $\mathbb{C}$ 上表述」，而是明确本仓库后续推理所采用的工作假设。

**矩形情形：** 原题限定 $A,B$ 同为 $n$ 阶方阵，故 **不** 引入 $m\neq n$ 的一般 $M_{m\times n}$ 情形。

## Content Review 摘要

- **审查日期：** 2026-08-20
- **原题来源：** 仓库内无外部教材/试卷引用；以题面文字为 Original statement。
- **结论：** (a)(b)(c) 的数学目标形式 **不变**；通过显式 Working assumption 消除 domain/codomain/谱域歧义。
- **与既有 Attempt 的 target 语义：** 不变（A000001/A000002/A000003 已在复化/复谱语境下推理）。

## 研究记录

### (a) 状态

- **User Evidence：** A000002 `partial` · A000004 `unsolved` / `independent`（冻结，不改 outcome）。
- **AI-generated Solution：** 见下节「(a) AI-generated Solution」；**不**构成 User Attempt。

<!-- MATH-AI-LAB:SOLUTION target=P0002/a BEGIN -->
> AI-generated Solution ≠ User Attempt。本节为 AUTO 模式完整解答（2026-08-20 逻辑修正版）。

**目标：** 若 $\lambda_1\in\mathrm{spec}_{\mathbb{C}}(A)$，$\lambda_2\in\mathrm{spec}_{\mathbb{C}}(B)$，则 $\lambda_1-\lambda_2\in\mathrm{spec}_{\mathbb{C}}(\varphi)$。

即：构造 $X\in M_n(\mathbb{C})$，$X\neq 0$，使 $\varphi(X)=(\lambda_1-\lambda_2)X$。

#### 为什么想到这个构造

希望 $AX-XB=(\lambda_1-\lambda_2)X$。一个**自然的充分条件**（不是等价条件）是同时要求

$$AX=\lambda_1 X,\qquad XB=\lambda_2 X.$$

因为若两式成立，则

$$AX-XB=\lambda_1 X-\lambda_2 X=(\lambda_1-\lambda_2)X.$$

**注意：** $AX-XB=(\lambda_1-\lambda_2)X$ **不能**推出 $AX=\lambda_1 X$ 与 $XB=\lambda_2 X$ 分别成立；我们只是找一个满足该充分条件的 $X$。

问题变为：如何构造非零 $X$，使左乘 $A$、右乘 $B$ 在 $X$ 上分别表现为乘 $\lambda_1$、$\lambda_2$？

$\varphi(X)=AX-XB$ 含**左乘 $A$** 与**右乘 $B$**。对秩一矩阵 $X=uv^{\mathsf T}$：

$$A(uv^{\mathsf T})=(Au)v^{\mathsf T},\qquad (uv^{\mathsf T})B=u(v^{\mathsf T}B).$$

左端只动 $u$，右端只动 $v^{\mathsf T}$。取 $Au=\lambda_1 u$（$A$ 的右特征向量），再取 $v^{\mathsf T}B=\lambda_2 v^{\mathsf T}$（$B$ 的左特征结构），则两侧同时标量化，得到 $X=uv^{\mathsf T}$ 的构造来源。

#### $B$ 与 $B^{\mathsf T}$ 的谱（修正表述）

已知 $\lambda_2\in\mathrm{spec}_{\mathbb{C}}(B)$。由于

$$\det(B^{\mathsf T}-\lambda I)=\det(B-\lambda I),$$

$B$ 与 $B^{\mathsf T}$ 有相同特征多项式，从而有相同复特征值，故 $\lambda_2\in\mathrm{spec}_{\mathbb{C}}(B^{\mathsf T})$。

于是存在 $v\in\mathbb{C}^n$，$v\neq 0$，使

$$B^{\mathsf T}v=\lambda_2 v.$$

转置（此处为普通转置 $\mathsf T$，非共轭转置）得

$$v^{\mathsf T}B=\lambda_2 v^{\mathsf T}.$$

**注意：** 这不是「$Bv_0=\lambda_2 v_0$ 与 $B^{\mathsf T}v=\lambda_2 v$ 为同一向量的等价改写」；而是从 $\lambda_2\in\mathrm{spec}(B)$ 推出 $\lambda_2\in\mathrm{spec}(B^{\mathsf T})$，再取 $B^{\mathsf T}$ 的（右）特征向量 $v$，得到左特征行向量关系 $v^{\mathsf T}B=\lambda_2 v^{\mathsf T}$。

#### 严格证明

取 $u\in\mathbb{C}^n$，$u\neq 0$，使 $Au=\lambda_1 u$。

因 $\lambda_2\in\mathrm{spec}_{\mathbb{C}}(B^{\mathsf T})$，取 $v\in\mathbb{C}^n$，$v\neq 0$，使 $B^{\mathsf T}v=\lambda_2 v$，即 $v^{\mathsf T}B=\lambda_2 v^{\mathsf T}$。

令 $X=uv^{\mathsf T}$。因 $u\neq 0$ 且 $v\neq 0$，故 $X\neq 0$。

$$\begin{aligned}
\varphi(X)&=AX-XB=Auv^{\mathsf T}-uv^{\mathsf T}B \\
&=(Au)v^{\mathsf T}-u(v^{\mathsf T}B) \\
&=\lambda_1 uv^{\mathsf T}-\lambda_2 uv^{\mathsf T} \\
&=(\lambda_1-\lambda_2)uv^{\mathsf T}=(\lambda_1-\lambda_2)X.
\end{aligned}$$

故 $X\neq 0$ 且 $\varphi(X)=(\lambda_1-\lambda_2)X$，即 $\lambda_1-\lambda_2\in\mathrm{spec}_{\mathbb{C}}(\varphi)$。$\square$

#### 条件检查

1. $A,B\in M_n(\mathbb{R})\subseteq M_n(\mathbb{C})$，工作空间为 $M_n(\mathbb{C})$；$u,v\in\mathbb{C}^n$ 可为复向量；$X=uv^{\mathsf T}\in M_n(\mathbb{C})$。
2. $A,B,X$ 均为 $n\times n$，左乘、右乘维度匹配。
3. 本问只需构造**一个**非零特征向量，**不要**求 $A,B$ 可对角化。
4. $B^{\mathsf T}$ 与 $B$ 谱相同由 $\det(B^{\mathsf T}-\lambda I)=\det(B-\lambda I)$ 保证。

#### 与 M0002 的关系

P0002(a) 是 M0002「左右特征结构 + 秩一对象构造」的一次具体应用：$L=A$，$R=B$；$u$ 来自 $A$ 的右特征结构；$v$ 来自 $B^{\mathsf T}$ 的右特征向量以得到 $v^{\mathsf T}B=\lambda_2 v^{\mathsf T}$；$X=uv^{\mathsf T}$；$\varphi(X)=(\lambda_1-\lambda_2)X$。M0002 步骤 5「若只需单个特征值存在性」即本题情形；(b) 才需步骤 4 的完整张成性验证。
<!-- MATH-AI-LAB:SOLUTION target=P0002/a END -->

### (b) 状态

assisted 尝试（A000001）完成 $X_{ij}=u_i v_j^T$ 构造与对角化证明；`correct`。

### (c) 状态

assisted 尝试（A000003）完成单射性证明；`correct`。证明使用题面现规定的 $\mathbb{C}$ 谱语境。

## 整题归档状态

- Content Review：**COMPLETE**
- 三 part Attempt 覆盖：a — A000002 partial · A000004 unsolved；b correct；c correct
- (a) 已有 AI-generated Solution（见上）；**User Attempt 仍缺** independent correct
- **尚未** 满足整题归档条件；未获人工「审核通过，请归档」授权

## 解答

<!-- MATH-AI-LAB:SOLUTION target=P0002/c BEGIN -->
> AI-generated Solution ≠ User Attempt。本节为 AUTO 模式完整解答。

**目标：** 若 $A,B$ 没有公共复特征值，则 $\varphi(X)=AX-XB$ 单射。

#### 为什么想到这个方法

由 (a)(b) 的谱差结构：$\varphi$ 的特征值形如 $\lambda-\mu$。于是
$$
0\in\mathrm{spec}(\varphi)\iff \exists\,\lambda\in\mathrm{spec}(A),\,\mu\in\mathrm{spec}(B)\text{ 使 }\lambda=\mu.
$$
故无公共特征值应推出 $0\notin\mathrm{spec}(\varphi)$，从而在有限维空间上 $\ker\varphi=\{0\}$。

#### 严格证明

在 $\mathbb{C}$ 上理解谱。设存在 $X\neq 0$ 使 $AX-XB=0$，即 $AX=XB$。

取 $B$ 的左特征向量 $w\neq 0$：$wB=\mu w$（$\mu\in\mathrm{spec}(B)$）。左乘 $AX=XB$ 得
$$
(wA)X = w(XB) = \mu (wX),
$$
即行向量 $wX$ 满足 $wXA$ 意义下的左特征关系，故 $\mu\in\mathrm{spec}(A)$。

于是 $\mu\in\mathrm{spec}(A)\cap\mathrm{spec}(B)$，与假设矛盾。

**关于 $wX\neq 0$：** 若对 $B$ 的一切左特征向量 $w$ 都有 $wX=0$，则在 $\mathbb{C}$ 上可推出 $X=0$，矛盾。故存在 $w$ 使 $wX\neq 0$，上述步骤合法。

因此 $\ker\varphi=\{0\}$，$\varphi$ 单射。$\square$

#### 条件检查

1. 公共特征值指 $\mathrm{spec}_{\mathbb{C}}(A)\cap\mathrm{spec}_{\mathbb{C}}(B)=\varnothing$。
2. 有限维下单射等价于核为零。
3. 与 (a) 的谱差结构一致：公共特征值存在时可用 $X=uv^{\mathsf T}$ 给出非平凡核元。
<!-- MATH-AI-LAB:SOLUTION target=P0002/c END -->

<!-- MATH-AI-LAB:SOLUTION target=P0002/b BEGIN -->
> AI-generated Solution ≠ User Attempt。本节为 AUTO 模式完整解答。

**目标：** 若 $A,B$ 均可对角化，则 $\varphi(X)=AX-XB$ 可对角化。

#### 为什么想到这个构造

(a) 已给出秩一构造 $X=uv^{\mathsf T}$ 使 $\varphi(X)=(\lambda-\mu)X$。若 $A,B$ 均可对角化，可取完整特征基，把同一构造推广为 $n^2$ 个特征向量，从而对角化 $\varphi$。

#### 严格证明

因 $A$ 可对角化，取特征基 $u_1,\ldots,u_n$，满足 $Au_i=\lambda_i u_i$。

因 $B$ 可对角化，$B^{\mathsf T}$ 亦可对角化；取特征基 $v_1,\ldots,v_n$，满足 $B^{\mathsf T}v_j=\mu_j v_j$，即 $v_j^{\mathsf T}B=\mu_j v_j^{\mathsf T}$。

令 $X_{ij}=u_i v_j^{\mathsf T}$。则
$$
\varphi(X_{ij})=A u_i v_j^{\mathsf T}-u_i v_j^{\mathsf T}B=\lambda_i u_i v_j^{\mathsf T}-\mu_j u_i v_j^{\mathsf T}=(\lambda_i-\mu_j)X_{ij}.
$$
故每个 $X_{ij}$ 都是 $\varphi$ 的特征向量。

$\{X_{ij}\}$ 共有 $n^2$ 个。设 $U=(u_1,\ldots,u_n)$、$V=(v_1,\ldots,v_n)$ 可逆，则 $X_{ij}=U E_{ij} V^{\mathsf T}$。$\{E_{ij}\}$ 是 $M_n$ 的标准基，且映射 $X\mapsto UXV^{\mathsf T}$ 可逆，故 $\{X_{ij}\}$ 也是 $M_n$ 的基。

因此 $\varphi$ 有由特征向量组成的基，故可对角化。$\square$

#### 条件检查

1. 工作空间为 $M_n(\mathbb{C})$（与题面 Working assumption 一致）。
2. 仅用 $A,B$ 可对角化；不要求谱互不相交。
3. 本问是完整对角化，不是单一特征值存在性。
<!-- MATH-AI-LAB:SOLUTION target=P0002/b END -->
