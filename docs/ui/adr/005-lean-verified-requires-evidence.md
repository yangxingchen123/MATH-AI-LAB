# ADR 005 — Lean Verified requires evidence

`.lean` 存在只能显示「源文件存在」。`Verified` 必须来自已有 lake / manifest / CI 证据（当前为 `manifests/*.yaml` 的 `build.status: SUCCEEDED`）。Web UI 不是 verifier。
