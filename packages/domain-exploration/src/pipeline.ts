import { isAI, isFormalSystem, isHuman, type ResearchActor } from "./actor.ts";
import labMap from "./lab-map.json" with { type: "json" };

/**
 * Observation → Exploration → Candidate → Experiment → Critique
 * → Proof Attempt → Verification → Promotion
 */

export const PIPELINE_STAGES = [
  "observation",
  "exploration",
  "candidate",
  "experiment",
  "critique",
  "proof_attempt",
  "verification",
  "promotion",
] as const;

export type PipelineStage = (typeof PIPELINE_STAGES)[number];

export type FormalVerificationStatus = "done" | "skipped" | "pending";

export interface PipelineStep {
  from: PipelineStage;
  to: PipelineStage;
  event: string;
  actor: ResearchActor;
  evidence: string;
  timestamp: string;
}

export interface DiscoveryPipeline {
  id: string;
  stage: PipelineStage;
  observationId?: string;
  candidateId?: string;
  humanReview: boolean;
  evidenceEvaluation: boolean;
  formalVerification: FormalVerificationStatus;
  history: PipelineStep[];
}

const FORWARD: Record<PipelineStage, PipelineStage[]> = {
  observation: ["exploration"],
  exploration: ["candidate"],
  candidate: ["experiment"],
  experiment: ["critique", "exploration"],
  critique: ["proof_attempt", "experiment", "exploration"],
  proof_attempt: ["verification", "promotion", "critique"],
  verification: ["promotion", "proof_attempt"],
  promotion: [],
};

export function pipelineStageFromLab(stage: string): PipelineStage {
  const raw = stage.trim();
  const mapped = (labMap.pipeline as Record<string, PipelineStage>)[raw];
  if (mapped && mapped !== "promotion") return mapped;
  return "exploration";
}

export function pipelineFromLabStage(
  id: string,
  labStage: string,
  candidateId?: string,
): DiscoveryPipeline {
  const formalVerification: FormalVerificationStatus =
    labStage === "PROVED_FORMAL" || labStage === "EXTERNAL_REVIEWED"
      ? "done"
      : labStage === "PAPER_READY"
        ? "skipped"
        : "pending";
  return {
    id,
    stage: pipelineStageFromLab(labStage),
    candidateId,
    humanReview: false,
    evidenceEvaluation: false,
    formalVerification,
    history: [],
  };
}

export function createPipeline(
  input: { id: string; observationId?: string },
): { ok: true; pipeline: DiscoveryPipeline } | { ok: false; error: string } {
  if (!input.id?.trim()) {
    return { ok: false, error: "DiscoveryPipeline requires id." };
  }
  return {
    ok: true,
    pipeline: {
      id: input.id,
      stage: "observation",
      observationId: input.observationId,
      humanReview: false,
      evidenceEvaluation: false,
      formalVerification: "pending",
      history: [],
    },
  };
}

export function markHumanReview(pipeline: DiscoveryPipeline, actor: ResearchActor): DiscoveryPipeline {
  if (!isHuman(actor)) return pipeline;
  return { ...pipeline, humanReview: true };
}

export function markEvidenceEvaluation(pipeline: DiscoveryPipeline, actor: ResearchActor): DiscoveryPipeline {
  if (!isHuman(actor)) return pipeline;
  return { ...pipeline, evidenceEvaluation: true };
}

export function markFormalVerification(
  pipeline: DiscoveryPipeline,
  status: Exclude<FormalVerificationStatus, "pending">,
  actor: ResearchActor,
): DiscoveryPipeline {
  if (status === "skipped" && !isHuman(actor)) return pipeline;
  if (status === "done" && isAI(actor)) return pipeline;
  if (status === "done" && !(isHuman(actor) || isFormalSystem(actor))) return pipeline;
  return { ...pipeline, formalVerification: status };
}

export function advancePipeline(
  pipeline: DiscoveryPipeline,
  to: PipelineStage,
  ctx: { event: string; actor: ResearchActor; evidence: string; timestamp: string },
): { ok: true; pipeline: DiscoveryPipeline } | { ok: false; error: string } {
  if (!ctx.event?.trim() || !ctx.evidence?.trim() || !ctx.actor?.type) {
    return { ok: false, error: "Pipeline advance requires event, actor, and evidence." };
  }
  if (!FORWARD[pipeline.stage].includes(to)) {
    return { ok: false, error: `Illegal pipeline move ${pipeline.stage} → ${to}.` };
  }
  if (to === "promotion") {
    if (!pipeline.humanReview || !pipeline.evidenceEvaluation) {
      return { ok: false, error: "Promotion requires human review and evidence evaluation." };
    }
    if (pipeline.formalVerification === "pending") {
      return { ok: false, error: "Formal verification is pending; skip explicitly or finish it." };
    }
    if (isAI(ctx.actor)) {
      return { ok: false, error: "AI cannot move a pipeline into promotion." };
    }
  }
  return {
    ok: true,
    pipeline: {
      ...pipeline,
      stage: to,
      history: [
        ...pipeline.history,
        {
          from: pipeline.stage,
          to,
          event: ctx.event,
          actor: ctx.actor,
          evidence: ctx.evidence,
          timestamp: ctx.timestamp,
        },
      ],
    },
  };
}
