"""Conversation routing and thinking contract. Not Frozen Schema."""

from __future__ import annotations

from pathlib import Path

import yaml

from .constants import PROTOCOL_PATH

KIND_IDS: tuple[str, ...] = (
    "exercise",
    "research",
    "modeling",
    "experiment",
    "literature",
    "review",
    "infra",
)

PROOF_KIND_IDS: frozenset[str] = frozenset({"exercise", "research"})
NON_PROOF_LAYERS: frozenset[str] = frozenset(
    {"heuristic", "numeric", "plot", "literature_title"}
)


def load_protocol(path: Path | None = None) -> dict:
    data = yaml.safe_load((path or PROTOCOL_PATH).read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("protocol must be a mapping")
    return data


def validate_protocol(protocol: dict) -> list[str]:
    errors: list[str] = []
    if not protocol.get("authority"):
        errors.append("missing authority")
    if protocol.get("not_frozen_schema") is not True:
        errors.append("protocol must declare not_frozen_schema")
    if not protocol.get("domain"):
        errors.append("domain required")
    if protocol.get("forbid_unscoped_mathematics") is not True:
        errors.append("forbid_unscoped_mathematics must be true")
    kinds = protocol.get("kinds")
    if not isinstance(kinds, dict):
        errors.append("kinds must be a mapping")
        return errors
    missing = [item for item in KIND_IDS if item not in kinds]
    if missing:
        errors.append(f"missing kinds: {missing}")
    for kind, spec in kinds.items():
        if not isinstance(spec, dict) or not spec.get("pipeline") or not spec.get("drop"):
            errors.append(f"kind {kind} needs pipeline and drop")
    if kinds.get("infra", {}).get("forbid_instance_work") is not True:
        errors.append("infra must forbid instance work")
    if kinds.get("modeling", {}).get("pipeline") != "model_select":
        errors.append("modeling pipeline must be model_select")
    steps = protocol.get("proof_steps")
    if not isinstance(steps, list) or not steps:
        errors.append("proof_steps required")
        return errors
    ids = [item.get("id") for item in steps if isinstance(item, dict)]
    if "reconstruct" not in ids or "retrieve" not in ids:
        errors.append("proof_steps must include reconstruct and retrieve")
    elif ids.index("reconstruct") > ids.index("retrieve"):
        errors.append("reconstruct must precede retrieve")
    roles = protocol.get("roles")
    if not isinstance(roles, dict) or "prover" not in roles or "formalizer" not in roles:
        errors.append("roles must include prover and formalizer")
    else:
        for name in ("prover", "formalizer"):
            banned = roles.get(name, {}).get("must_not") or []
            if "mutate_statement" not in banned:
                errors.append(f"{name} must not mutate_statement")
        pi_banned = roles.get("human_pi", {}).get("must_not") or []
        if "outsource_final_judgment" not in pi_banned:
            errors.append("human_pi must not outsource_final_judgment")
    stop_when = protocol.get("stop_when")
    if not isinstance(stop_when, list) or "unknown" not in stop_when:
        errors.append("stop_when must include unknown")
    if protocol.get("require_obstacle_when_stuck") is not True:
        errors.append("require_obstacle_when_stuck must be true")
    tool_first = protocol.get("tool_first")
    if not isinstance(tool_first, list) or "evaluator" not in tool_first:
        errors.append("tool_first must include evaluator")
    if protocol.get("forbid_expensive_model_when_tool_succeeds") is not True:
        errors.append("forbid_expensive_model_when_tool_succeeds must be true")
    if protocol.get("forbid_retry_unrepairable") is not True:
        errors.append("forbid_retry_unrepairable must be true")
    if "out_of_universe" not in (protocol.get("unrepairable_reasons") or []):
        errors.append("unrepairable_reasons must include out_of_universe")
    strategy_banned = (protocol.get("roles") or {}).get("strategy", {}).get("must_not") or []
    if "treat_fluency_as_correctness" not in strategy_banned:
        errors.append("strategy must not treat_fluency_as_correctness")
    layers = protocol.get("layers")
    if not isinstance(layers, list) or layers != ["canonical", "universe", "frontier", "exploration"]:
        errors.append("layers must be canonical, universe, frontier, exploration")
    if protocol.get("forbid_layer_merge") is not True:
        errors.append("forbid_layer_merge must be true")
    pipeline = protocol.get("discovery_pipeline")
    expected_pipeline = [
        "observation",
        "exploration",
        "candidate",
        "experiment",
        "critique",
        "proof_attempt",
        "verification",
        "promotion",
    ]
    if pipeline != expected_pipeline:
        errors.append("discovery_pipeline must be the eight exploration stages")
    promotion = protocol.get("promotion")
    if not isinstance(promotion, dict):
        errors.append("promotion contract missing")
    else:
        if promotion.get("automatic") is not False:
            errors.append("promotion.automatic must be false")
        if promotion.get("require_human_review") is not True:
            errors.append("promotion.require_human_review must be true")
        if promotion.get("require_evidence_evaluation") is not True:
            errors.append("promotion.require_evidence_evaluation must be true")
        if promotion.get("exploration_cannot_write_canonical") is not True:
            errors.append("promotion.exploration_cannot_write_canonical must be true")
        if promotion.get("pending_blocks_promotion") is not True:
            errors.append("promotion.pending_blocks_promotion must be true")
        if promotion.get("formal_verification") != "optional":
            errors.append("promotion.formal_verification must be optional")
    memory = protocol.get("failure_memory")
    if not isinstance(memory, dict):
        errors.append("failure_memory contract missing")
    else:
        if memory.get("reusable") is not True:
            errors.append("failure_memory.reusable must be true")
        if memory.get("embeddings") is not False:
            errors.append("failure_memory.embeddings must be false")
        if memory.get("lookup") != "lexical":
            errors.append("failure_memory.lookup must be lexical")
    exploration = protocol.get("exploration")
    if not isinstance(exploration, dict):
        errors.append("exploration contract missing")
    else:
        if exploration.get("reasoning_proves_theorem") is not False:
            errors.append("exploration.reasoning_proves_theorem must be false")
        if exploration.get("pattern_is_not_theorem") is not True:
            errors.append("exploration.pattern_is_not_theorem must be true")
        if exploration.get("notebook_is_canonical") is not False:
            errors.append("exploration.notebook_is_canonical must be false")
        if exploration.get("strategy_is_proof") is not False:
            errors.append("exploration.strategy_is_proof must be false")
        if exploration.get("evolution_proves_theorem") is not False:
            errors.append("exploration.evolution_proves_theorem must be false")
        if exploration.get("catalog_search") != "lexical":
            errors.append("exploration.catalog_search must be lexical")
        if exploration.get("embeddings") is not False:
            errors.append("exploration.embeddings must be false")
    frontier = protocol.get("frontier")
    if not isinstance(frontier, dict):
        errors.append("frontier contract missing")
    else:
        if frontier.get("catalog") != "erdosproblems":
            errors.append("frontier.catalog must be erdosproblems")
        if frontier.get("scope") != "additive_combinatorics":
            errors.append("frontier.scope must be additive_combinatorics")
        if frontier.get("vendor") != "vendor/erdosproblems":
            errors.append("frontier.vendor must be vendor/erdosproblems")
        if frontier.get("pin") != "5308c57c700559416b9f205df274b136784203e7":
            errors.append("frontier.pin must match the erdosproblems vendor pin")
        if frontier.get("source") != "vendor/erdosproblems/data/problems.yaml":
            errors.append("frontier.source must be vendor/erdosproblems/data/problems.yaml")
        if frontier.get("full_tree") is not True:
            errors.append("frontier.full_tree must be true")
        if frontier.get("writes_canonical") is not False:
            errors.append("frontier.writes_canonical must be false")
        if frontier.get("not_a_theorem") is not True:
            errors.append("frontier.not_a_theorem must be true")
        if frontier.get("embeddings") is not False:
            errors.append("frontier.embeddings must be false")
        if frontier.get("network") is not False:
            errors.append("frontier.network must be false")
    return errors


def route(kind: str, protocol: dict | None = None) -> dict:
    spec = (protocol or load_protocol()).get("kinds") or {}
    if kind not in spec:
        return {
            "ok": False,
            "task_kind": kind,
            "errors": [f"unknown task_kind: {kind}"],
        }
    data = spec[kind]
    return {
        "ok": True,
        "task_kind": kind,
        "pipeline": data.get("pipeline"),
        "drop": data.get("drop"),
        "forbid_instance_work": bool(data.get("forbid_instance_work")),
        "errors": [],
    }


def evaluate_session(session: dict, protocol: dict | None = None) -> dict:
    contract = protocol or load_protocol()
    errors: list[str] = []
    if not isinstance(session, dict):
        return {"ok": False, "errors": ["session must be a mapping"], "warnings": []}
    kind = session.get("task_kind")
    routed = route(str(kind or ""), contract)
    if not routed["ok"]:
        return {
            "ok": False,
            "errors": routed["errors"],
            "warnings": [],
            "kind": kind,
        }
    if routed["forbid_instance_work"] and (
        session.get("new_problem") or session.get("new_lean_theorem")
    ):
        errors.append("infra_must_not_emit_instance_work")
    pipeline = session.get("pipeline") or routed["pipeline"]
    if kind == "modeling" and pipeline == "proof":
        errors.append("modeling_must_not_use_proof_pipeline")
    if kind in PROOF_KIND_IDS:
        retrieved = bool(session.get("retrieved") or session.get("retrieval_query"))
        working = str(session.get("working_proposition") or "").strip()
        if retrieved and not working:
            errors.append("retrieve_before_reconstruct")
        if not working:
            errors.append("missing_working_proposition")
        bets = session.get("bets") or []
        if not isinstance(bets, list):
            errors.append("bets must be a list")
            bets = []
        if len(bets) > 2:
            errors.append("too_many_bets")
        for index, bet in enumerate(bets):
            if not isinstance(bet, dict) or not str(bet.get("kill_criteria") or "").strip():
                errors.append(f"bet_{index}_missing_kill_criteria")
        layer = session.get("evidence_layer")
        if session.get("claimed_proved") and (
            layer in NON_PROOF_LAYERS or not layer
        ):
            errors.append("non_proof_claimed_as_proved")
        if session.get("claimed_proved") and not session.get("stop_marked"):
            errors.append("claimed_proved_without_stop")
    if session.get("stuck"):
        if not str(session.get("obstacle_type") or "").strip():
            errors.append("stuck_without_obstacle")
        if session.get("claimed_proved"):
            errors.append("claimed_proved_while_stuck")
    if session.get("expensive_model") and session.get("tool_succeeded"):
        errors.append("model_after_tool_success")
    if session.get("create_knowledge") and not session.get("knowledge_authorized"):
        errors.append("knowledge_without_authorization")
    if session.get("create_method") and not session.get("method_authorized"):
        errors.append("method_without_authorization")
    if session.get("write_canonical") or session.get("promote_to_canonical"):
        errors.append("exploration_cannot_write_canonical")
    if session.get("ai_promotion"):
        errors.append("ai_cannot_promote")
    if session.get("novelty_claim") == "first" and not session.get("expert_signoff"):
        errors.append("novelty_first_without_expert")
    if session.get("mode") == "STUDY" and not session.get("study_opt_in"):
        errors.append("study_requires_explicit_opt_in")
    role = session.get("role")
    actions = session.get("actions") or []
    roles = contract.get("roles") or {}
    if role and isinstance(roles, dict) and role in roles:
        banned = set(roles[role].get("must_not") or [])
        for action in actions:
            if action in banned:
                errors.append(f"role_{role}_must_not_{action}")
    return {
        "ok": errors == [],
        "errors": errors,
        "warnings": [],
        "kind": kind,
        "drop": routed["drop"],
        "pipeline": routed["pipeline"],
        "forbid_instance_work": routed["forbid_instance_work"],
    }
