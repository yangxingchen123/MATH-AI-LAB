# Knowledge 自动索引

> 本目录由 Knowledge Indexer v1.0 自动生成。禁止手工维护。所有事实以 Knowledge Markdown YAML Metadata 为准；本目录可以删除并重新构建。

## 1. 总体统计

- Knowledge objects: 2
- Domains (非空): 1
- Without domain: 0
- Prerequisite edges: 1
- Related declared edges: 0
- Related effective edges (undirected pairs): 0
- Source metadata SHA-256: `62673af695b573488ec73577d7b2643c3b23a398af67edcaa4f67a41f7cb826d`

## 2. Knowledge 总表

| ID | 标题 | Status | Domain | Prerequisites | Required By | Related |
| --- | --- | --- | --- | --- | --- | --- |
| K0001 | [勒让德变换](../数学变换/勒让德变换.md) | reviewed | 凸分析 | K0002 | [] | [] |
| K0002 | [凸函数](../优化理论/凸函数.md) | reviewed | 凸分析 | [] | K0001 | [] |

## 3. Status 统计

- draft: 0
- reviewed: 2
- archived: 0

## 4. Domain 统计

- 凸分析: 2

## 5. 关系统计

- prerequisite_edges: 1
- related_declared_edges: 0
- related_effective_edges (无向 pair): 0

## 6. 使用说明

- 本目录为 **DERIVED / GENERATED DATA**，可随时删除并用 Indexer 重建。
- Knowledge YAML Metadata 是权威事实源；索引不得反向写回 Knowledge。
- `required_by` / `related_effective` 仅为派生视图。
- 请勿在 `_索引/` 中放置手工文件。
- 重建：`python -m tools.knowledge_indexer build`
- 检查是否过期：`python -m tools.knowledge_indexer check`
