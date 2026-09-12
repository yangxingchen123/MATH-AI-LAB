import type { Candidate } from "@math-ai-lab/domain-math";
import { promoteToCanonical } from "@math-ai-lab/domain-math";
import { isHuman, type ResearchActor } from "./actor.ts";

/**
 * No automatic promotion.
 * Candidate → Human Review → Evidence Evaluation → Formal Verification (optional)
 * → Canonical Operation (not executed here).
 */

export interface PromotionRequest {
  candidateId: string;
  actor: ResearchActor;
  humanReview: boolean;
  evidenceEvaluation: boolean;
  formalVerification: "done" | "skipped" | "pending";
}

export interface PromotionDecision {
  authorized: boolean;
  wroteCanonical: false;
  next: "blocked" | "canonical_operation_not_executed";
  error?: string;
}

export function requestPromotion(req: PromotionRequest): PromotionDecision {
  if (!isHuman(req.actor)) {
    return {
      authorized: false,
      wroteCanonical: false,
      next: "blocked",
      error: "Promotion handoff requires a Human actor.",
    };
  }
  if (!req.humanReview) {
    return {
      authorized: false,
      wroteCanonical: false,
      next: "blocked",
      error: "Promotion requires human review.",
    };
  }
  if (!req.evidenceEvaluation) {
    return {
      authorized: false,
      wroteCanonical: false,
      next: "blocked",
      error: "Promotion requires evidence evaluation.",
    };
  }
  if (req.formalVerification === "pending") {
    return {
      authorized: false,
      wroteCanonical: false,
      next: "blocked",
      error: "Formal verification is pending; skip explicitly or finish it.",
    };
  }
  return {
    authorized: true,
    wroteCanonical: false,
    next: "canonical_operation_not_executed",
  };
}

export function executeCanonicalWrite(candidate: Candidate): {
  ok: false;
  error: string;
  wroteCanonical: false;
} {
  const inner = promoteToCanonical(candidate);
  return {
    ok: false,
    error: `Exploration Layer cannot write Canonical. ${inner.error}`,
    wroteCanonical: false,
  };
}
