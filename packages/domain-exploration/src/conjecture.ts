import type { Candidate } from "@math-ai-lab/domain-math";
import { isAI, isHuman, type ResearchActor } from "./actor.ts";
import labMap from "./lab-map.json" with { type: "json" };

/**
 * Process model over a Universe Candidate.
 * Never: AI generated → Theorem.
 */

export const CONJECTURE_STATES = [
  "idea",
  "generated",
  "exploring",
  "tested",
  "supported",
  "challenged",
  "modified",
  "resolved",
  "rejected",
] as const;

export type ConjectureState = (typeof CONJECTURE_STATES)[number];

export interface LifecycleEvent {
  from: ConjectureState;
  to: ConjectureState;
  event: string;
  actor: ResearchActor;
  evidence: string;
  timestamp: string;
}

export interface ConjectureLifecycle {
  id: string;
  candidateId: string;
  state: ConjectureState;
  history: LifecycleEvent[];
}

const TRANSITIONS: Record<ConjectureState, ConjectureState[]> = {
  idea: ["generated", "exploring", "rejected", "modified"],
  generated: ["exploring", "modified", "rejected", "idea"],
  exploring: ["tested", "challenged", "modified", "rejected"],
  tested: ["supported", "challenged", "rejected", "modified", "exploring"],
  supported: ["challenged", "modified", "resolved", "rejected"],
  challenged: ["modified", "rejected", "exploring", "tested"],
  modified: ["exploring", "generated", "rejected", "idea"],
  resolved: [],
  rejected: ["idea", "modified"],
};

export function canTransitionConjecture(from: ConjectureState, to: ConjectureState): boolean {
  return TRANSITIONS[from].includes(to);
}

export function lifecycleFromLabStage(stage: string): ConjectureState {
  const raw = stage.trim();
  const mapped = (labMap.lifecycle as Record<string, ConjectureState>)[raw];
  if (mapped) return mapped;
  if (raw.startsWith("REJECTED")) return "rejected";
  return "exploring";
}

export function labStageFromNotes(notes?: string): string | null {
  if (!notes) return null;
  const match = notes.match(/\blab_stage=([A-Z0-9_]+)/);
  return match?.[1] ?? null;
}

export function fromCandidate(candidate: Candidate): ConjectureLifecycle {
  const labStage = labStageFromNotes(candidate.notes);
  const state: ConjectureState =
    candidate.origin === "ai_mock" && candidate.status === "idea"
      ? "generated"
      : labStage
        ? lifecycleFromLabStage(labStage)
        : candidate.status === "rejected"
          ? "rejected"
          : candidate.status === "supported" || candidate.status === "promoted"
            ? "supported"
            : candidate.status === "exploring"
              ? "exploring"
              : "idea";
  return {
    id: `lifecycle:${candidate.id}`,
    candidateId: candidate.id,
    state,
    history: [],
  };
}

export function conjectureIsTheorem(_lifecycle: ConjectureLifecycle): false {
  return false;
}

export function transitionConjecture(
  lifecycle: ConjectureLifecycle,
  to: ConjectureState,
  ctx: { event: string; actor: ResearchActor; evidence: string; timestamp: string },
): { ok: true; lifecycle: ConjectureLifecycle } | { ok: false; error: string } {
  if (!ctx.event?.trim()) {
    return { ok: false, error: "Conjecture transition requires event." };
  }
  if (!ctx.evidence?.trim()) {
    return { ok: false, error: "Conjecture transition requires evidence." };
  }
  if (!ctx.actor?.type || !ctx.actor.id?.trim()) {
    return { ok: false, error: "Conjecture transition requires actor." };
  }
  if (!canTransitionConjecture(lifecycle.state, to)) {
    return { ok: false, error: `Illegal conjecture transition ${lifecycle.state} → ${to}.` };
  }
  if ((to === "supported" || to === "resolved") && !isHuman(ctx.actor)) {
    return { ok: false, error: "supported/resolved require a Human actor." };
  }
  if (lifecycle.state === "generated" && to === "resolved") {
    return { ok: false, error: "AI generated conjectures cannot resolve into theorems." };
  }
  if (isAI(ctx.actor) && (to === "supported" || to === "resolved")) {
    return { ok: false, error: "AI cannot declare a conjecture supported or resolved." };
  }
  const event: LifecycleEvent = {
    from: lifecycle.state,
    to,
    event: ctx.event,
    actor: ctx.actor,
    evidence: ctx.evidence,
    timestamp: ctx.timestamp,
  };
  return {
    ok: true,
    lifecycle: {
      ...lifecycle,
      state: to,
      history: [...lifecycle.history, event],
    },
  };
}
