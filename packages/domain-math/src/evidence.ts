export const EVIDENCE_TYPES = [
  "HumanProof",
  "LeanProof",
  "Computation",
  "Experiment",
  "Literature",
  "Counterexample",
  "ExpertReview",
] as const;

export type EvidenceType = (typeof EVIDENCE_TYPES)[number];

export const EVIDENCE_STATUSES = [
  "unverified",
  "supporting",
  "contradicting",
  "rejected",
  "candidate",
] as const;

export type EvidenceStatus = (typeof EVIDENCE_STATUSES)[number];

export const EVIDENCE_CONFIDENCE = ["none", "heuristic", "human_claimed", "machine_checked"] as const;

export type EvidenceConfidence = (typeof EVIDENCE_CONFIDENCE)[number];

export interface EvidenceRecord {
  id: string;
  claim: string;
  evidenceType: EvidenceType;
  source: string;
  status: EvidenceStatus;
  confidence: EvidenceConfidence;
}

export function isMathematicalTruth(confidence: EvidenceConfidence): boolean {
  return confidence === "machine_checked";
}
