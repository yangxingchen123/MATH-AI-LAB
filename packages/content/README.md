# `@math-ai-lab/content`

只读 Content Adapter：扫仓库 → 解析 Front Matter → 投影到 `@math-ai-lab/domain`。

**不是** Schema 权威。Python Validator（`tools/*_validator`）才是。冲突时改本包。

Phase 1 禁止写入 canonical YAML。
