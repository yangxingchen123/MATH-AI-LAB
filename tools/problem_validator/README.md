# Problem Validator v1

Problem Validator v1 is the **formal mechanical validator** for **Frozen Problem Schema v1** (frozen 2026-08-19).

It is **not** a rename of Problem Candidate Gate v0.1. Candidate Gate remains a pre-freeze migration oracle only.

## Principles

- Read-only (no `--fix`, no ID allocation, no status mutation, no Knowledge creation)
- Dependency-aware: `check` automatically runs Knowledge Validator v1.1 first via Python API
- Strict data directory: every `02_题目库/**/*.md` except `题目模板.md` is governed Problem data
- YAML `id` is identity source of truth; **filename does not define Problem identity**
- Does not validate mathematical body content
- Ignores Candidate-only markers such as `Candidate Content Review: PENDING`

## CLI

```text
python -m tools.problem_validator check
python -m tools.problem_validator check-file <PATH>
```

Options: `--root`, `--format text|json`, `--summary`, `--verbose`, `--strict-warnings`

Exit codes: `0` = no ERROR; `1` = ERROR (or WARNING with `--strict-warnings`)

## Public Python API

```python
from tools.problem_validator import validate_project, focus_view, ValidationResult, ProblemDocument

result = validate_project(root=project_root)
# Or inject Knowledge result to avoid duplicate Knowledge validation:
from tools.knowledge_validator import validate_project as validate_knowledge
kv = validate_knowledge(root=project_root)
result = validate_project(root=project_root, knowledge_result=kv)
view = focus_view(result, path_to_problem_file)
```

## Rule families

| Family | Purpose |
| --- | --- |
| P-DISC | Discovery / check-file scope |
| P-PARSE | Front Matter / YAML parsing |
| P-BASE | Core Frozen fields |
| P-STATE | `status` enum |
| P-DATE | `created` / `updated` |
| P-ID | P ID uniqueness |
| P-KNOW | `knowledge` list + Knowledge dependency |
| P-PART | optional `parts` |
| P-FIELD | unknown field WARNING |

See `constants.py` (`RULES`) for stable rule IDs.

## New Problem authoring

1. Copy from `02_题目库/题目模板.md` as a **draft** scaffold (not a Schema source).
2. Replace sentinel `P0000` with a real `Pdddd`.
3. Save under `02_题目库/` (the template file itself is excluded from Problem objects).
4. Run:

```text
python -m tools.problem_validator check-file "<PATH>"
```

Full library (includes Knowledge dependency):

```text
python -m tools.problem_validator check
```

## Knowledge dependency

If Knowledge Validator reports ERROR, Problem Validator emits `P-KNOW-E010` and skips unreliable P→K target existence checks to avoid cascade false positives.
