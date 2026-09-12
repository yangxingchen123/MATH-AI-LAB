/** Exploration-layer actor. Distinct from Universe ResearchEvent.actor. */

export const ACTOR_TYPES = ["Human", "AI", "FormalSystem"] as const;

export type ActorType = (typeof ACTOR_TYPES)[number];

export interface ResearchActor {
  type: ActorType;
  id: string;
}

export interface AttributedAction {
  actor: ResearchActor;
  action: string;
  targetId: string;
  timestamp: string;
}

export function createActor(
  input: ResearchActor,
): { ok: true; actor: ResearchActor } | { ok: false; error: string } {
  if (!ACTOR_TYPES.includes(input.type)) {
    return { ok: false, error: "Unknown ResearchActor type." };
  }
  if (!input.id?.trim()) {
    return { ok: false, error: "ResearchActor requires id." };
  }
  return { ok: true, actor: input };
}

export function isHuman(actor: ResearchActor): boolean {
  return actor.type === "Human";
}

export function isAI(actor: ResearchActor): boolean {
  return actor.type === "AI";
}

export function isFormalSystem(actor: ResearchActor): boolean {
  return actor.type === "FormalSystem";
}
