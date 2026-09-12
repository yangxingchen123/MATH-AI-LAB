# teorth/erdosproblems upstream

Repository:
https://github.com/teorth/erdosproblems

Pinned commit:
5308c57c700559416b9f205df274b136784203e7

Pinned date:
2026-09-07

License:
Apache License 2.0 (see `LICENSE`)

Policy:
This directory is a **full-tree pin** of the upstream git tree at the
commit above (every tracked file; no sparse subset).
Runtime reads **local files only**. There is no GitHub API, no REST
client, no live clone, and no scrape of https://www.erdosproblems.com.
Do not follow `main` automatically.
Do not edit upstream files here except when bumping the pin.
Do not copy problem prose from https://www.erdosproblems.com.
Do not vendor `google-deepmind/formal-conjectures` Lean (Mathlib is unplugged).
Do not merge `requirements.txt` into the warehouse root requirements.
Do not run upstream GitHub Actions or deploy their Pages site.
Do not create `P00xx` / Lab problems / Knowledge from these IDs.

MATH-AI-LAB overlay (not upstream):

- `UPSTREAM.md` — this file
- `NOTICE` — redistribution notice

Upstream files in this pin:

- `.github/ISSUE_TEMPLATE/help-wanted.yml`
- `.github/workflows/deploy-pages.yml`
- `.github/workflows/update-formal-conjectures.yml`
- `.github/workflows/update-readme.yml`
- `.github/workflows/validate.yml`
- `.gitignore`
- `CITATIONS.cff`
- `CONTRIBUTING.md`
- `LICENSE`
- `README.md`
- `data/problems.yaml` — ground truth for this pin (1217 records)
- `data/statistics_history.csv`
- `data/statistics_history_dark.svg`
- `data/statistics_history_light.svg`
- `docs/app.js`
- `docs/filters.js`
- `docs/index.html`
- `docs/styles.css`
- `docs/theme-toggle.js`
- `docs/url-state.js`
- `docs/utils.js`
- `requirements.txt` — unused by MATH-AI-LAB; do not merge
- `schema/problems.schema.json`
- `scripts/derive_status.py`
- `scripts/generate_readme.py`
- `scripts/oeis_cons_compare.py`
- `scripts/plot_statistics_history.py`
- `scripts/update_formalization_status.py`
- `scripts/validate.py`
- `tests/test_oeis_cons_compare.py`

How MATH-AI-LAB uses the pin:

1. Python reads `data/problems.yaml` from this directory.
2. In memory, keep tags containing `additive combinatorics`.
3. Project `status.state` equal to `open` or starting with `open `
   as Frontier `OpenQuestion` pointers (`erdos:<n>`, group 前沿).
4. Project the remaining additive-combinatorics rows as local audit
   pointers (same `erdos:<n>`, group 前沿备查). They are not
   OpenQuestions and not theorems.
5. `packages/domain-frontier/src/erdos-additive.json` is a **derived
   local mirror** of that in-memory projection, for the TypeScript
   package. It is not a network payload. Rebuild after bumping the pin:

```text
python -c "from tools.research_lab.frontier_catalog import dump_erdos_index_json; dump_erdos_index_json()"
```

`proved` / `disproved` / other statuses stay in `data/problems.yaml`
for audit and are **not** projected as theorems.
External `formalized: yes` is not Lean verification in this warehouse.
Upstream scripts and `docs/` are kept so the pin is inspectable; this
warehouse does not execute them as part of `operate` / `gate`.
