# ADR 007 — Web write uses domain operations

Web 写入必须经过具名 Domain Operation → Python authority → Validator。不得让 Next.js 或 React 直接改 canonical Markdown。
