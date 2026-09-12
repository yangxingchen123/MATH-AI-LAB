# ADR 003 — Web Adapter is read-only

`packages/content` 只投影。页面不得 `fs.readFile`。React 不得解析 Front Matter。写入必须走已有 Python Layer 2 操作，且需要用户授权。
