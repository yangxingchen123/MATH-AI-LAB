export const CANDIDATE_STATUSES = [
  "idea",
  "exploring",
  "supported",
  "rejected",
  "promoted",
] as const;

export type CandidateStatus = (typeof CANDIDATE_STATUSES)[number];

export interface Candidate {
  id: string;
  title: string;
  proposedType: string;
  status: CandidateStatus;
  origin: "lab" | "inbox" | "ai_mock" | "human";
  sourcePath?: string;
  notes?: string;
}

const TRANSITIONS: Record<CandidateStatus, CandidateStatus[]> = {
  idea: ["exploring", "rejected"],
  exploring: ["supported", "rejected", "idea"],
  supported: ["promoted", "rejected", "exploring"],
  rejected: ["idea"],
  promoted: [],
};

export function canTransition(from: CandidateStatus, to: CandidateStatus): boolean {
  return TRANSITIONS[from].includes(to);
}

export function transitionCandidate(
  candidate: Candidate,
  to: CandidateStatus,
  ctx: { humanReview: boolean },
): { ok: true; candidate: Candidate } | { ok: false; error: string } {
  if (!ctx.humanReview) {
    return { ok: false, error: "Candidate transition requires human review." };
  }
  if (!canTransition(candidate.status, to)) {
    return { ok: false, error: `Illegal candidate transition ${candidate.status} → ${to}.` };
  }
  return { ok: true, candidate: { ...candidate, status: to } };
}

export function promoteToCanonical(_candidate: Candidate): { ok: false; error: string } {
  return {
    ok: false,
    error: "v0.1 forbids promoting a Candidate to canonical. Use a future Domain Operation after review.",
  };
}
