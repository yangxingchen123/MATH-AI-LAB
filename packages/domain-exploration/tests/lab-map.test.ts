import { describe, expect, it } from "vitest";
import labMap from "../src/lab-map.json" with { type: "json" };
import {
  CONJECTURE_STATES,
  PIPELINE_STAGES,
  lifecycleFromLabStage,
  pipelineFromLabStage,
  pipelineStageFromLab,
} from "../src/index.ts";

describe("shared lab map", () => {
  it("covers lifecycle and pipeline without mapping any lab stage to promotion", () => {
    expect(labMap.never_maps_to_promotion).toBe(true);
    const lifecycleValues = Object.values(labMap.lifecycle);
    const pipelineValues = Object.values(labMap.pipeline);
    expect(lifecycleValues.every((state) => CONJECTURE_STATES.includes(state as (typeof CONJECTURE_STATES)[number]))).toBe(
      true,
    );
    expect(pipelineValues.every((stage) => PIPELINE_STAGES.includes(stage as (typeof PIPELINE_STAGES)[number]))).toBe(
      true,
    );
    expect(pipelineValues.includes("promotion")).toBe(false);
    expect(lifecycleFromLabStage("FALSIFICATION")).toBe("challenged");
    expect(pipelineStageFromLab("FALSIFICATION")).toBe("experiment");
    expect(pipelineStageFromLab("PAPER_READY")).toBe("verification");
    const pipe = pipelineFromLabStage("pipe:lab:PROB-SF-001", "FALSIFICATION", "candidate:lab:PROB-SF-001");
    expect(pipe.stage).toBe("experiment");
    expect(pipe.humanReview).toBe(false);
    expect(pipe.formalVerification).toBe("pending");
  });
});
