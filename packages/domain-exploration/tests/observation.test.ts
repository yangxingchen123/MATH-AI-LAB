import { describe, expect, it } from "vitest";
import { MATH_ENTITY_TYPES } from "@math-ai-lab/domain-math";
import {
  EXPLORATION_LAYER,
  MATHEMATICAL_LAYERS,
  createObservation,
  observationKind,
} from "../src/index.ts";

describe("MathematicalObservation", () => {
  it("records a pre-mathematical signal", () => {
    const made = createObservation({
      id: "obs:1",
      description: "Unexpected numerical pattern in sum-free densities",
      origin: "numerical_pattern",
      relatedEntities: ["question:problem:P0001"],
      evidence: ["evidence:run:1"],
      researchContext: "region:sum-free",
      timestamp: "2026-09-09T16:00+08:00",
    });
    expect(made.ok).toBe(true);
    if (made.ok) {
      expect(observationKind(made.observation)).toBe("observation");
    }
  });

  it("is not a Universe entity type and is not a conjecture", () => {
    expect(MATH_ENTITY_TYPES.includes("observation" as never)).toBe(false);
    expect(MATHEMATICAL_LAYERS).toContain(EXPLORATION_LAYER);
    const missing = createObservation({
      id: "",
      description: "x",
      origin: "human",
      relatedEntities: [],
      evidence: [],
      researchContext: "",
      timestamp: "t",
    });
    expect(missing.ok).toBe(false);
  });
});
