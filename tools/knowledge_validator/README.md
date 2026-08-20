# Knowledge Validator v1.1

Read-only Metadata validator for **Frozen Knowledge Schema v1**.

## Usage

From project root (or with `PYTHONPATH` pointing at the project root):

```text
python -m tools.knowledge_validator check
python -m tools.knowledge_validator check-file "01_知识库/优化理论/凸函数.md"
python -m tools.knowledge_validator check --format json
python -m tools.knowledge_validator check --root C:\MATH-AI-LAB
```

## Notes

- Does **not** modify Markdown / YAML.
- Does **not** auto-fix or allocate IDs.
- Does **not** generate indexes or reverse links.
- Exit `0` = no ERROR; `1` = has ERROR (or WARNING if `--strict-warnings`).
- Template `01_知识库/知识库模板.md` is excluded by path (not by `K0000`).
