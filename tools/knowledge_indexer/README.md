# Knowledge Indexer v1.0

Deterministic derived index from **validated** Knowledge Metadata (Frozen Knowledge Schema v1).

## Pipeline

```text
Knowledge Markdown
  → Knowledge Validator v1.1
  → Validation PASS
  → Knowledge Indexer v1.0
  → 01_知识库/_索引/
```

## Commands

```text
python -m tools.knowledge_indexer build
python -m tools.knowledge_indexer check
python -m tools.knowledge_indexer check --format json
python -m tools.knowledge_indexer build --root C:\MATH-AI-LAB
python -m tools.knowledge_indexer build --strict-warnings
```

## Output

`01_知识库/_索引/` is **GENERATED / DERIVED**:

- `README.md`
- `按领域.md`
- `关系索引.md`
- `knowledge_index.json`

Do not hand-edit. Safe to delete and rebuild. Knowledge YAML remains the source of truth.

## Notes

- Indexer never modifies Knowledge Markdown / YAML.
- Does not allocate IDs, auto-fix, or write `required_by` / symmetric `related` back to sources.
- `build` is UP_TO_DATE when outputs already match.
- `check` never writes files.
