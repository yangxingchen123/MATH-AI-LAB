# 设计系统

关键词：clean / academic / dense but readable / research workspace。  
反面：Hero、大渐变、玻璃拟态、卡片墙、为动效浪费空间。

参考气质：Fumadocs 的阅读密度、GitHub 的信息层级、Linear 的克制、VS Code 的工作区。对象模型跟它们都不同。

---

## 1. 版式

| 令牌 | 值 |
| --- | --- |
| 正文宽 | 约 68–80ch（公式可超出并横向滚） |
| 侧栏 | ~232px |
| TOC | ~220px |
| 字号 | 正文 14–16px；标题阶梯小，不用大于 24px 的装饰大字 |
| 色 | 一种 accent；其余中性 |
| 动效 | 无装饰动画；主题切换瞬时 |

状态 **不能只靠颜色**：`reviewed` / `已解决` / `Verified` 必须带文字（可加小点）。

Light / Dark / System。KaTeX 两套背景都要能读；代码块跟主题走。

---

## 2. 基础组件（Phase 1 够用再做）

Button、IconButton、Input、Select、Dialog、Drawer、Tooltip、Tabs、Badge、Table、Tree、Breadcrumb、CommandPalette、Sidebar、TOC、EmptyState、ErrorState、LoadingState。

业务：`StatusPair`（YAML × 目录两行）、`ProblemRow`、`KnowledgeRow`、`PartBlock`、`ArtifactLink`。

数学：`Math`、`MathErrorBoundary`、`Proof`（可折叠）、`Callout`。  
Definition / Theorem / Lemma 只在正文出现对应结构时渲染，**不为填空造节**。

---

## 3. 数学阅读（最高优先级）

- 行内 `$...$`、块 `$$...$$`、`\[ \]`、`\( \)`
- AMS：aligned / cases / matrix / pmatrix / bmatrix
- 非法公式（`\alphai` 等）：块内「公式无法渲染」+ 查看源码；**整页不崩**
- 开发环境 console warning
- 编号公式：仅当源文已有编号
- 复制：块公式可「复制 LaTeX」
- 移动端：`.katex-display` overflow-x auto，body 不横滑

Adapter 抽公式时不得拆坏 `\alpha_i`。与黄金 fixture 对测。

---

## 4. Markdown

支持：标题锚点、复制标题链接、GFM 表、引用、围栏代码（复制）、脚注、图片 lazy、内部 `P0002` / `K0001` 链接、callout。  
YAML front matter **永不进正文**。  
Mermaid：仅当某页已有 mermaid 围栏再做，不预做引擎。

Proof 长于阈值可默认 Collapse。

---

## 5. 无障碍与性能

语义标签、可见 focus、对比度、键盘可达侧栏/命令盘/TOC。禁止纯 div 菜单。

一页不加载全库。目录按路由取数。搜索索引构建与页面分离。RSC 默认；命令盘 / 主题 / 公式交互才 client。

---

## 6. 错误

统一 Error UI：MD 解析失败、元数据非法、文件缺失、断链、PDF 无、索引无、公式失败。空白页算验收失败。
