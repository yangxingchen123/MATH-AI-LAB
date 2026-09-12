import { describe, expect, it } from "vitest";
import { MATH_ENTITY_TYPES, type Candidate } from "@math-ai-lab/domain-math";
import {
  MATHEMATICAL_LAYERS,
  NullSearchProvider,
  NullSimilarityEngine,
  advancePipeline,
  createPipeline,
  executeCanonicalWrite,
  markEvidenceEvaluation,
  markFormalVerification,
  markHumanReview,
  recordAssessment,
  requestPromotion,
} from "../src/index.ts";
import type { CriticAgent, ExplorerAgent, ResearchActor } from "../src/index.ts";

const human = { type: "Human" as const, id: "冲" };
const ai = { type: "AI" as const, id: "mock" };
const stamp = "2026-09-09T16:00+08:00";

function step(event: string, actor: ResearchActor = human) {
  return { event, actor, evidence: "notebook note", timestamp: stamp };
}

describe("Promotion safety", () => {
  it("keeps the four layers distinct and never adds exploration types to Universe", () => {
    expect(MATHEMATICAL_LAYERS).toEqual(["canonical", "universe", "frontier", "exploration"]);
    expect(MATH_ENTITY_TYPES.includes("observation" as never)).toBe(false);
    expect(MATH_ENTITY_TYPES.includes("pattern" as never)).toBe(false);
  });

  it("blocks pipeline jumps and AI promotion", () => {
    const made = createPipeline({ id: "pipe:1", observationId: "obs:1" });
    expect(made.ok).toBe(true);
    if (!made.ok) return;
    const skip = advancePipeline(made.pipeline, "promotion", step("skip"));
    expect(skip.ok).toBe(false);
    let pipe = made.pipeline;
    for (const to of ["exploration", "candidate", "experiment", "critique", "proof_attempt"] as const) {
      const next = advancePipeline(pipe, to, step(`to ${to}`));
      expect(next.ok).toBe(true);
      if (!next.ok) return;
      pipe = next.pipeline;
    }
    const noReview = advancePipeline(pipe, "promotion", step("promote"));
    expect(noReview.ok).toBe(false);
    pipe = markHumanReview(pipe, human);
    pipe = markEvidenceEvaluation(pipe, human);
    const pending = advancePipeline(pipe, "promotion", step("promote"));
    expect(pending.ok).toBe(false);
    pipe = markFormalVerification(pipe, "skipped", human);
    const aiPromote = advancePipeline(pipe, "promotion", step("promote", ai));
    expect(aiPromote.ok).toBe(false);
    const ok = advancePipeline(pipe, "promotion", step("human promote"));
    expect(ok.ok).toBe(true);
    if (!ok.ok) return;
    expect(ok.pipeline.stage).toBe("promotion");
  });

  it("authorizes Canonical Operation handoff without writing Canonical", () => {
    const blocked = requestPromotion({
      candidateId: "candidate:lab:C001",
      actor: ai,
      humanReview: true,
      evidenceEvaluation: true,
      formalVerification: "skipped",
    });
    expect(blocked.authorized).toBe(false);
    expect(blocked.wroteCanonical).toBe(false);
    const missingEvidence = requestPromotion({
      candidateId: "candidate:lab:C001",
      actor: human,
      humanReview: true,
      evidenceEvaluation: false,
      formalVerification: "skipped",
    });
    expect(missingEvidence.authorized).toBe(false);
    const pending = requestPromotion({
      candidateId: "candidate:lab:C001",
      actor: human,
      humanReview: true,
      evidenceEvaluation: true,
      formalVerification: "pending",
    });
    expect(pending.authorized).toBe(false);
    const ready = requestPromotion({
      candidateId: "candidate:lab:C001",
      actor: human,
      humanReview: true,
      evidenceEvaluation: true,
      formalVerification: "skipped",
    });
    expect(ready.authorized).toBe(true);
    expect(ready.wroteCanonical).toBe(false);
    expect(ready.next).toBe("canonical_operation_not_executed");
    const candidate: Candidate = {
      id: "candidate:lab:C001",
      title: "lab",
      proposedType: "conjecture",
      status: "supported",
      origin: "lab",
    };
    const write = executeCanonicalWrite(candidate);
    expect(write.ok).toBe(false);
    expect(write.wroteCanonical).toBe(false);
  });

  it("keeps assessment human-controlled and agent/search output as Candidate", () => {
    const aiAssess = recordAssessment({
      id: "assess:1",
      targetId: "candidate:lab:C001",
      novelty: "high",
      difficulty: "unknown",
      evidence: [],
      connections: [],
      formalStatus: "none",
      assessor: ai,
    });
    expect(aiAssess.ok).toBe(false);
    const humanAssess = recordAssessment({
      id: "assess:1",
      targetId: "candidate:lab:C001",
      novelty: "local observation",
      difficulty: "undergraduate",
      evidence: ["evidence:run:1"],
      connections: ["definition:knowledge:K0001"],
      formalStatus: "none",
      assessor: human,
    });
    expect(humanAssess.ok).toBe(true);
    const explorer: ExplorerAgent = {
      explore: (observationId) => ({
        id: `candidate:ai_mock:explore:${observationId}`,
        title: "explored",
        proposedType: "conjecture",
        status: "idea",
        origin: "ai_mock",
      }),
    };
    const critic: CriticAgent = {
      critique: (targetId) => ({
        id: `candidate:ai_mock:critique:${targetId}`,
        title: "critique",
        proposedType: "conjecture",
        status: "idea",
        origin: "ai_mock",
      }),
    };
    expect(explorer.explore("obs:1").status).toBe("idea");
    expect(critic.critique("c1").origin).toBe("ai_mock");
    expect(new NullSimilarityEngine().findAnalogies("e1")).toEqual([]);
    expect(new NullSearchProvider().searchFailure("compactness")).toEqual([]);
  });
});
