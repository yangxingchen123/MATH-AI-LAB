# Knowledge Workflow v1.0

Thin orchestration over **Knowledge Validator v1.1** and **Knowledge Indexer v1.0**.

Workflow does not own Schema rules, rendering, or derived relations.

## Daily usage

After creating or editing a Knowledge Markdown file:

```text
python -m tools.knowledge_workflow sync "01_知识库/数学变换/勒让德变换.md"
```

This runs:

1. check-file (full-library context)
2. full Knowledge validation
3. index build (`BUILT` or `UP_TO_DATE`)

## Other commands

```text
python -m tools.knowledge_workflow check "<Knowledge Markdown>"
python -m tools.knowledge_workflow status
python -m tools.knowledge_workflow status --format json
python -m tools.knowledge_workflow sync "<file>" --root C:\MATH-AI-LAB --strict-warnings
```

- `check` is read-only (never builds the index).
- `status` is read-only system health (no target file).

## Not in scope

- No auto-fix
- No ID allocation
- No automatic `draft` → `reviewed`
- No math-content review
- No subprocess wrapping of Validator / Indexer

Underlying CLIs remain available:

```text
python -m tools.knowledge_validator
python -m tools.knowledge_indexer
```
