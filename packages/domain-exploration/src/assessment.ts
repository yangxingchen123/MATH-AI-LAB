import { isHuman, type ResearchActor } from "./actor.ts";

/** Human-controlled research evaluation. Not automatic judgment. */

export const FORMAL_STATUSES = ["none", "attempted", "verified"] as const;

export type FormalStatus = (typeof FORMAL_STATUSES)[number];

export interface ResearchAssessment {
  id: string;
  targetId: string;
  novelty: string;
  difficulty: string;
  evidence: string[];
  connections: string[];
  formalStatus: FormalStatus;
  assessor: ResearchActor;
}

export function recordAssessment(
  input: ResearchAssessment,
): { ok: true; assessment: ResearchAssessment } | { ok: false; error: string } {
  if (!input.id?.trim() || !input.targetId?.trim()) {
    return { ok: false, error: "ResearchAssessment requires id and targetId." };
  }
  if (!FORMAL_STATUSES.includes(input.formalStatus)) {
    return { ok: false, error: "Unknown formalStatus." };
  }
  if (!isHuman(input.assessor)) {
    return { ok: false, error: "ResearchAssessment must be recorded by a Human." };
  }
  return { ok: true, assessment: input };
}
