/**
 * Pre-mathematical signal. Not a Question, Conjecture, or Proof.
 */

export const OBSERVATION_ORIGINS = [
  "numerical_pattern",
  "theory_similarity",
  "assumption_failure",
  "human",
  "lab",
  "other",
] as const;

export type ObservationOrigin = (typeof OBSERVATION_ORIGINS)[number];

export interface MathematicalObservation {
  id: string;
  description: string;
  origin: ObservationOrigin;
  relatedEntities: string[];
  evidence: string[];
  researchContext: string;
  timestamp: string;
}

export function createObservation(
  input: MathematicalObservation,
): { ok: true; observation: MathematicalObservation } | { ok: false; error: string } {
  if (!input.id?.trim() || !input.description?.trim()) {
    return { ok: false, error: "Observation requires id and description." };
  }
  if (!OBSERVATION_ORIGINS.includes(input.origin)) {
    return { ok: false, error: "Unknown observation origin." };
  }
  if (!input.timestamp?.trim()) {
    return { ok: false, error: "Observation requires timestamp." };
  }
  if (input.researchContext == null) {
    return { ok: false, error: "Observation requires researchContext." };
  }
  return { ok: true, observation: input };
}

export function observationKind(_observation: MathematicalObservation): "observation" {
  return "observation";
}
