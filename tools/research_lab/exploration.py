"""Read-only exploration briefing. Does not write Source or Canonical."""

from __future__ import annotations

from pathlib import Path

from .conjecture import load_all_conjectures
from .constants import EXPLORATION_DOCS, EXPLORATION_PKG, FAILURE_JOURNAL_PATH, FRONTIER_PKG, PROBLEMS_DIR
from .failures import as_memory_rows, load_failures
from .frontier_catalog import erdos_health_detail, erdos_vendor_ok, frontier_briefing
from .lab_map import LAB_MAP_PATH, lifecycle_state, pipeline_stage
from .registry import TERMINAL_STAGES, list_problem_paths, load_record

REQUIRED_DOCS: tuple[str, ...] = (
    "README.md",
    "observation-model.md",
    "pattern-model.md",
    "conjecture-evolution.md",
    "experiment-framework.md",
    "failure-memory.md",
    "proof-strategy.md",
    "reasoning-graph.md",
    "research-notebook.md",
    "memory-architecture.md",
    "discovery-pipeline.md",
    "frontier-catalog.md",
)

REJECTED_PREFIX = "REJECTED"


def layer_health() -> dict:
    missing_docs = [name for name in REQUIRED_DOCS if not (EXPLORATION_DOCS / name).is_file()]
    ok = (
        FRONTIER_PKG.is_dir()
        and EXPLORATION_PKG.is_dir()
        and LAB_MAP_PATH.is_file()
        and missing_docs == []
        and erdos_vendor_ok()
    )
    return {
        "ok": ok,
        "frontier_package": FRONTIER_PKG.is_dir(),
        "exploration_package": EXPLORATION_PKG.is_dir(),
        "lab_map": LAB_MAP_PATH.is_file(),
        "erdos_frontier": erdos_vendor_ok(),
        "missing_docs": missing_docs,
        "detail": (
            erdos_health_detail()
            if ok
            else f"missing {missing_docs or 'packages/lab-map/erdos-frontier'}"
        ),
        "writes_source": False,
    }


def _lemma_note() -> dict:
    from .lemmas import lemma_graph, reasoning_graph

    graph = lemma_graph()
    reasoning = reasoning_graph()
    return {
        "nodes": len(graph.get("nodes") or []),
        "acyclic": bool(graph.get("acyclic")),
        "reasoning_nodes": len(reasoning.get("nodes") or []),
        "reasoning_edges": len(reasoning.get("edges") or []),
        "proves_theorem": False,
        "not_a_theorem": True,
    }


def _reasoning_briefing() -> dict:
    from .lemmas import reasoning_graph

    return reasoning_graph()


def _resolve_journal(failure_path: Path | None) -> Path:
    if failure_path is not None:
        return Path(failure_path)
    return FAILURE_JOURNAL_PATH


def _pattern_briefing() -> list[dict]:
    from .patterns import pattern_clusters

    return pattern_clusters()


def _strategy_briefing() -> list[dict]:
    from .strategies import scan_proof_strategies

    return scan_proof_strategies()


def _evolution_briefing() -> dict:
    from .theory_map import theory_modules

    return theory_modules()


def _lab_notebook(*, exploring: list[dict], next_dirs: list[dict], failures: list[dict]) -> dict:
    return {
        "id": "notebook:projected",
        "title": "Lab exploration notebook",
        "observations": ["known:lab-inventory"],
        "questions": [str(item.get("id")) for item in exploring],
        "ideas": [str(item.get("id")) for item in next_dirs],
        "attempts": [],
        "experiments": [],
        "failures": [str(item.get("id")) for item in failures],
        "results": [],
        "canonical": False,
        "not_a_theorem": True,
    }


def _lab_session(*, exploring: list[dict]) -> dict:
    return {
        "id": "session:projected",
        "researcher": "Human",
        "goal": "Read-only lab exploration. Not a new research claim.",
        "inputs": [str(item.get("id")) for item in exploring],
        "outputs": ["overview"],
        "conclusion_is_theorem": False,
        "not_a_theorem": True,
    }


def explore_briefing(*, failure_path: Path | None = None) -> dict:
    conjectures = load_all_conjectures()
    problems = [load_record(path) for path in list_problem_paths(PROBLEMS_DIR)]
    exploring: list[dict] = []
    for item in conjectures:
        status = str(item.get("status") or "")
        exploring.append(
            {
                "id": item.get("id"),
                "title": item.get("statement") or item.get("id"),
                "state": lifecycle_state(status),
                "pipeline": pipeline_stage(status),
                "lab_status": status,
                "not_a_theorem": True,
            }
        )
    for item in problems:
        stage = str(item.get("stage") or "")
        exploring.append(
            {
                "id": item.get("id"),
                "title": item.get("title") or item.get("id"),
                "state": lifecycle_state(stage),
                "pipeline": pipeline_stage(stage),
                "lab_status": stage,
                "not_a_theorem": True,
            }
        )
    belief: list[dict] = []
    for item in conjectures + problems:
        prior = item.get("prior_art") or []
        if not isinstance(prior, list):
            continue
        for row in prior:
            if not isinstance(row, dict):
                continue
            belief.append(
                {
                    "id": item.get("id"),
                    "relation": row.get("relation"),
                    "note": row.get("note"),
                    "confidence": "none",
                }
            )
        decls = item.get("lean_decls") or []
        if decls:
            belief.append(
                {
                    "id": item.get("id"),
                    "relation": "lean_declared",
                    "note": f"{len(decls)} Lean decls listed; Source Exists ≠ Verified",
                    "confidence": "none",
                }
            )
    lab_failures = [
        {
            "id": item.get("id"),
            "reason": item.get("stage") or item.get("status"),
            "lesson": "Rejected or blocked lab record. Not deleted.",
            "source": "lab_record",
            "not_a_theorem": True,
        }
        for item in problems + conjectures
        if str(item.get("stage") or item.get("status") or "").startswith(REJECTED_PREFIX)
        or str(item.get("stage") or item.get("status") or "") in TERMINAL_STAGES
    ]
    journal = load_failures(_resolve_journal(failure_path))
    failures = lab_failures + as_memory_rows(journal)
    next_dirs = [
        {
            "id": item["id"],
            "title": item["title"],
            "detail": (
                f"lifecycle={item['state']}; pipeline={item['pipeline']}; "
                "Human Review required before Canonical Operation"
            ),
        }
        for item in exploring
        if item["state"] != "rejected"
    ]
    lemma_note = _lemma_note()
    reasoning = _reasoning_briefing()
    patterns = _pattern_briefing()
    strategies = _strategy_briefing()
    evolution = _evolution_briefing()
    notebook = _lab_notebook(exploring=exploring, next_dirs=next_dirs, failures=failures)
    session = _lab_session(exploring=exploring)
    frontier = frontier_briefing()
    frontier_open = int((frontier.get("counts") or {}).get("open_questions") or 0)
    next_dirs.append(
        {
            "id": "frontier",
            "title": str((frontier.get("region") or {}).get("title") or "前沿"),
            "detail": (
                f"{frontier_open} open Erdős additive-combinatorics pointers. "
                "Not theorems. Promotion is not automatic."
            ),
        }
    )
    return {
        "layer": "exploration",
        "writes_source": False,
        "wrote_canonical": False,
        "promotion_authorized": False,
        "health": layer_health(),
        "journal_loaded": bool(journal),
        "known": {
            "note": "Canonical mathematics stays in Frozen Source. Lab records are Candidates, never theorems.",
            "lab_problem_count": len(problems),
            "lab_conjecture_count": len(conjectures),
            "lemma_graph": lemma_note,
        },
        "exploring": exploring,
        "belief": belief,
        "failures": failures,
        "next": next_dirs,
        "reasoning": reasoning,
        "patterns": patterns,
        "strategies": strategies,
        "evolution": evolution,
        "notebook": notebook,
        "session": session,
        "frontier": frontier,
        "counts": {
            "known_lab_problems": len(problems),
            "exploring": len(exploring),
            "belief": len(belief),
            "failures": len(failures),
            "journal": len(journal),
            "next": len(next_dirs),
            "reasoning_nodes": len(reasoning.get("nodes") or []),
            "reasoning_edges": len(reasoning.get("edges") or []),
            "patterns": len(patterns),
            "strategies": len(strategies),
            "evolution_nodes": len(evolution.get("nodes") or []),
            "evolution_edges": len(evolution.get("edges") or []),
            "frontier_open": frontier_open,
        },
        "answers": {
            "what_we_know": (
                "Canonical Source plus Lab candidate inventory; this briefing declares no theorems. "
                f"Lemma graph nodes={lemma_note.get('nodes', 0)} acyclic={lemma_note.get('acyclic')}. "
                f"Reasoning graph nodes={len(reasoning.get('nodes') or [])} "
                f"requires-edges={len(reasoning.get('edges') or [])} proves_theorem=false. "
                f"Patterns {len(patterns)}, none are theorems. "
                f"Proof strategies {len(strategies)}, none are stored proofs. "
                f"Theory modules {len(evolution.get('nodes') or [])} with {len(evolution.get('edges') or [])} evolution edges. "
                "Notebook is not Canonical. Session conclusion is not a theorem. "
                f"Frontier open pointers {frontier_open}, none are theorems."
            ),
            "what_we_explore": (
                f"{len(exploring)} lab problems/conjectures in process states; "
                f"{frontier_open} external open Erdős pointers in additive combinatorics."
            ),
            "why_we_believe": f"{len(belief)} prior-art or Lean-decl notes; none are mathematical truth.",
            "what_failed": (
                f"{len(failures)} retained dead-ends (lab rejects {len(lab_failures)}, journal {len(journal)})."
                if failures
                else "No rejected lab records or journal lines in this warehouse."
            ),
            "what_is_next": f"{len(next_dirs)} open candidates. Promotion is not automatic.",
        },
    }


def search_failures(query: str, *, failure_path: Path | None = None) -> dict:
    from .failures import lookup_failures

    report = explore_briefing(failure_path=failure_path)
    hits = lookup_failures(report.get("failures") or [], query)
    return {
        "query": query,
        "hits": hits,
        "count": len(hits),
        "status": "candidate",
        "embeddings": False,
        "wrote_canonical": False,
        "not_a_theorem": True,
    }


def briefing_markdown(report: dict | None = None) -> str:
    data = report if report is not None else explore_briefing()
    answers = data.get("answers") or {}
    lines = [
        "# 数学探索（过程层）",
        "",
        "只读。不是 Canonical。Lab 记录仍是 Candidate。禁止自动 Promotion。",
        "",
        "## 五问",
        "",
        f"- 我们知道什么：{answers.get('what_we_know', '')}",
        f"- 正在探索什么：{answers.get('what_we_explore', '')}",
        f"- 为何相信：{answers.get('why_we_believe', '')}",
        f"- 哪些失败了：{answers.get('what_failed', '')}",
        f"- 下一步可能是什么：{answers.get('what_is_next', '')}",
        "",
        "## 正在探索",
        "",
    ]
    exploring = data.get("exploring") or []
    if not exploring:
        lines.append("（无）")
    for item in exploring:
        lines.append(
            f"- `{item.get('id')}` · {item.get('title')} · lifecycle=`{item.get('state')}` · pipeline=`{item.get('pipeline')}` · not a theorem"
        )
    lines.extend(["", "## 失败记忆", ""])
    failures = data.get("failures") or []
    if not failures:
        lines.append("（无保留失败。失败被删除才是问题。）")
    for item in failures:
        lines.append(f"- `{item.get('id')}` · {item.get('reason')} · {item.get('lesson')}")
    lines.extend(["", "## 下一步", ""])
    for item in data.get("next") or []:
        lines.append(f"- `{item.get('id')}` · {item.get('title')} · {item.get('detail')}")
    reasoning = data.get("reasoning") or {}
    lines.extend(["", "## 推理图", ""])
    lines.append(
        f"nodes={len(reasoning.get('nodes') or [])} · requires-edges={len(reasoning.get('edges') or [])} · proves_theorem=false"
    )
    lines.append("只投影 declared `depends_on`。文件顺序不是推理边。")
    for node in reasoning.get("nodes") or []:
        lines.append(f"- `{node.get('id')}` · {node.get('kind')} · {node.get('content')}")
    lines.extend(["", "## 模式", ""])
    pattern_rows = data.get("patterns") or []
    if not pattern_rows:
        lines.append("（无重复结构。单例不记为 Pattern。）")
    for item in pattern_rows:
        lines.append(
            f"- `{item.get('id')}` · {item.get('kind')} · instances={len(item.get('instances') or [])} · {item.get('pattern')}"
        )
    lines.extend(["", "## 证明策略", ""])
    strategy_rows = data.get("strategies") or []
    if not strategy_rows:
        lines.append("（无词法命中。未扫描到的命名策略不编造。）")
    for item in strategy_rows:
        cases = ", ".join(f"`{row}`" for row in (item.get("successfulCases") or []))
        lines.append(
            f"- `{item.get('id')}` · {item.get('strategy')} · cases={cases} · not a proof"
        )
    evolution = data.get("evolution") or {}
    lines.extend(["", "## 理论模块", ""])
    lines.append(
        f"nodes={len(evolution.get('nodes') or [])} · edges={len(evolution.get('edges') or [])} · claims_evolution=false"
    )
    for node in evolution.get("nodes") or []:
        lines.append(f"- `{node.get('id')}` · {node.get('title')}")
    notebook = data.get("notebook") or {}
    session = data.get("session") or {}
    lines.extend(
        [
            "",
            "## 笔记本 / 会话",
            "",
            f"- `{notebook.get('id')}` · canonical={notebook.get('canonical')} · not Canonical",
            f"- `{session.get('id')}` · conclusion_is_theorem={session.get('conclusion_is_theorem')}",
            "",
            "## 前沿",
            "",
        ]
    )
    frontier = data.get("frontier") or {}
    counts = (frontier.get("counts") or {})
    lines.append(
        f"open={counts.get('open_questions', 0)} · additive_records={counts.get('additive_records', 0)} · not_a_theorem=true"
    )
    lines.append(
        "Local vendor pin of teorth/erdosproblems. Runtime reads data/problems.yaml. "
        "No GitHub API. No erdosproblems.com scrape."
    )
    lines.extend(
        [
            "",
            f"探索中 {data.get('counts', {}).get('exploring', 0)} · 信念 {data.get('counts', {}).get('belief', 0)} · 失败 {data.get('counts', {}).get('failures', 0)}",
            "",
            "写入 Canonical：否",
        ]
    )
    return "\n".join(lines) + "\n"


def exploration_index(*, failure_path: Path | None = None) -> list[dict]:
    report = explore_briefing(failure_path=failure_path)
    rows: list[dict] = [
        {
            "id": "overview",
            "title": "探索总览",
            "group": "总览",
            "body": briefing_markdown(report),
        }
    ]
    for item in report.get("exploring") or []:
        rows.append(
            {
                "id": str(item.get("id")),
                "title": str(item.get("title") or item.get("id")),
                "group": f"正在探索 · {item.get('state')}",
                "body": (
                    f"# {item.get('title')}\n\n"
                    f"- id: `{item.get('id')}`\n"
                    f"- lifecycle: `{item.get('state')}`\n"
                    f"- pipeline: `{item.get('pipeline')}`\n"
                    f"- lab_status: `{item.get('lab_status')}`\n"
                    f"- not_a_theorem: true\n\n"
                    "Candidate only. Human Review required before Canonical Operation.\n"
                ),
            }
        )
    for item in report.get("failures") or []:
        rows.append(
            {
                "id": str(item.get("id")),
                "title": str(item.get("reason") or item.get("id")),
                "group": "失败记忆",
                "body": (
                    f"# {item.get('reason')}\n\n"
                    f"- id: `{item.get('id')}`\n"
                    f"- lesson: {item.get('lesson')}\n\n"
                    "Failure is retained. Not deleted. Not a theorem.\n"
                ),
            }
        )
    for item in report.get("next") or []:
        rows.append(
            {
                "id": f"next:{item.get('id')}",
                "title": str(item.get("title") or item.get("id")),
                "group": "下一步",
                "body": f"# {item.get('title')}\n\n{item.get('detail')}\n\nPromotion is not automatic.\n",
            }
        )
    reasoning = report.get("reasoning") or {}
    rows.append(
        {
            "id": "reasoning",
            "title": "推理图（引理依赖）",
            "group": "推理图",
            "body": (
                "# 推理图（引理依赖）\n\n"
                "只投影 declared `depends_on`。文件顺序不是推理边。图的存在不等于定理已证。\n\n"
                f"proves_theorem: false\n"
                f"nodes: {len(reasoning.get('nodes') or [])}\n"
                f"requires-edges: {len(reasoning.get('edges') or [])}\n\n"
                + "".join(
                    f"- `{node.get('id')}` · {node.get('kind')} · {node.get('content')}\n"
                    for node in reasoning.get("nodes") or []
                )
                + "\nNot Canonical.\n"
            ),
        }
    )
    for node in reasoning.get("nodes") or []:
        requires = [
            str(edge.get("target"))
            for edge in reasoning.get("edges") or []
            if edge.get("source") == node.get("id") and edge.get("type") == "requires"
        ]
        rows.append(
            {
                "id": f"reasoning:{node.get('id')}",
                "title": str(node.get("content") or node.get("id")),
                "group": "推理图",
                "body": (
                    f"# {node.get('content')}\n\n"
                    f"- id: `{node.get('id')}`\n"
                    f"- kind: `{node.get('kind')}`\n"
                    f"- requires: {', '.join(f'`{item}`' for item in requires) or '（无）'}\n"
                    "- reasoningProvesTheorem: false\n\n"
                    "Candidate / process record only. Not Canonical.\n"
                ),
            }
        )
    for item in report.get("patterns") or []:
        rows.append(
            {
                "id": str(item.get("id")),
                "title": str(item.get("pattern") or item.get("id")),
                "group": "模式",
                "body": (
                    f"# {item.get('pattern')}\n\n"
                    f"- id: `{item.get('id')}`\n"
                    f"- kind: `{item.get('kind')}`\n"
                    f"- confidence: `{item.get('confidence')}`\n"
                    f"- instances: {', '.join(f'`{row}`' for row in (item.get('instances') or []))}\n"
                    "- Pattern ≠ theorem.\n\n"
                    "Candidate / process record only. Not Canonical.\n"
                ),
            }
        )
    notebook = report.get("notebook") or {}
    if notebook.get("id"):
        rows.append(
            {
                "id": str(notebook.get("id")),
                "title": str(notebook.get("title") or notebook.get("id")),
                "group": "笔记本",
                "body": (
                    f"# {notebook.get('title')}\n\n"
                    f"- id: `{notebook.get('id')}`\n"
                    f"- canonical: {notebook.get('canonical')}\n"
                    f"- questions: {len(notebook.get('questions') or [])}\n"
                    f"- failures: {len(notebook.get('failures') or [])}\n"
                    "- Notebook is exploration history. Not Canonical.\n"
                ),
            }
        )
    session = report.get("session") or {}
    if session.get("id"):
        rows.append(
            {
                "id": str(session.get("id")),
                "title": str(session.get("goal") or session.get("id")),
                "group": "会话",
                "body": (
                    f"# {session.get('goal')}\n\n"
                    f"- id: `{session.get('id')}`\n"
                    f"- conclusion_is_theorem: {session.get('conclusion_is_theorem')}\n"
                    f"- inputs: {len(session.get('inputs') or [])}\n"
                    "- Session conclusion is not a theorem.\n"
                ),
            }
        )
    for item in report.get("strategies") or []:
        cases = ", ".join(f"`{row}`" for row in (item.get("successfulCases") or []))
        rows.append(
            {
                "id": str(item.get("id")),
                "title": str(item.get("strategy") or item.get("id")),
                "group": "证明策略",
                "body": (
                    f"# {item.get('strategy')}\n\n"
                    f"- id: `{item.get('id')}`\n"
                    f"- strategyIsProof: false\n"
                    f"- successfulCases: {cases or '（无）'}\n"
                    + "".join(f"- condition: {line}\n" for line in (item.get("applicableConditions") or []))
                    + "".join(f"- limitation: {line}\n" for line in (item.get("limitations") or []))
                    + "\nLexical scan ≠ stored proof. Not Canonical.\n"
                ),
            }
        )
    evolution = report.get("evolution") or {}
    if evolution:
        node_lines = "".join(
            f"- `{node.get('id')}` · {node.get('title')}\n" for node in (evolution.get("nodes") or [])
        )
        rows.append(
            {
                "id": "evolution",
                "title": "理论模块（无演化边）",
                "group": "理论演化",
                "body": (
                    "# 理论模块（无演化边）\n\n"
                    "One node per Lean module. No extends/simplifies/unifies/specializes is claimed.\n\n"
                    "proves_theorem: false\n"
                    f"edges: {len(evolution.get('edges') or [])}\n"
                    f"claims_evolution: {evolution.get('claims_evolution')}\n\n"
                    f"{node_lines}\n"
                    "Not Canonical.\n"
                ),
            }
        )
    from .frontier_catalog import frontier_catalog_rows

    rows.extend(frontier_catalog_rows())
    return rows


def list_index(*, failure_path: Path | None = None) -> list[dict]:
    return [
        {"id": row.get("id"), "group": row.get("group"), "title": row.get("title")}
        for row in exploration_index(failure_path=failure_path)
    ]


def _hit_kind(group: str) -> str:
    if "失败" in group:
        return "failure"
    if "推理" in group:
        return "proof"
    if "策略" in group:
        return "strategy"
    if "模式" in group or "演化" in group:
        return "analogy"
    return "concept"


def search_explore(query: str, *, failure_path: Path | None = None) -> dict:
    needle = query.strip().lower()
    hits: list[dict] = []
    if needle:
        for row in exploration_index(failure_path=failure_path):
            ident = str(row.get("id") or "")
            if not is_safe_exploration_id(ident):
                continue
            hay = "\n".join(
                [
                    ident,
                    str(row.get("title") or ""),
                    str(row.get("group") or ""),
                    str(row.get("body") or ""),
                ]
            ).lower()
            if needle not in hay:
                continue
            hits.append(
                {
                    "id": ident,
                    "kind": _hit_kind(str(row.get("group") or "")),
                    "title": str(row.get("title") or ident),
                    "group": str(row.get("group") or ""),
                    "status": "candidate",
                }
            )
    return {
        "query": query,
        "hits": hits,
        "count": len(hits),
        "status": "candidate",
        "embeddings": False,
        "wrote_canonical": False,
        "not_a_theorem": True,
    }


def is_safe_exploration_id(object_id: str) -> bool:
    if not object_id or len(object_id) > 240:
        return False
    normalized = object_id.replace("\\", "/")
    if ".." in normalized or "/" in normalized or "\0" in object_id:
        return False
    return True


def lookup_index(object_id: str, *, failure_path: Path | None = None) -> dict | None:
    if not is_safe_exploration_id(object_id):
        return None
    for row in exploration_index(failure_path=failure_path):
        if str(row.get("id")) == object_id:
            return row
    return None
