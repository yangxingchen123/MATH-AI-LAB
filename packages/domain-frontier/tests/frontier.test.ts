import { describe, expect, it } from "vitest";
import {
  FRONTIER_LAYER,
  catalogErdosFrontier,
  createOpenQuestion,
  createResearchDirection,
  createUnknownRegion,
  loadErdosIndex,
  projectErdosFrontier,
  questionIsTheorem,
} from "../src/index.ts";

describe("Frontier Layer", () => {
  it("represents unknown regions without becoming entities or conjectures", () => {
    expect(FRONTIER_LAYER).toBe("frontier");
    const region = createUnknownRegion({
      id: "region:topology-gap",
      title: "Separation axioms beyond T3.5",
      description: "Unknown whether a useful intermediate axiom exists.",
      relatedEntityIds: ["definition:knowledge:K0001"],
      openQuestionIds: ["q:gap-1"],
      directionIds: ["dir:axiom-hunt"],
      status: "open",
    });
    expect(region.ok).toBe(true);
    const missing = createUnknownRegion({
      id: "",
      title: "x",
      description: "y",
      relatedEntityIds: [],
      openQuestionIds: [],
      directionIds: [],
      status: "open",
    });
    expect(missing.ok).toBe(false);
  });

  it("binds directions and open questions to a region", () => {
    const direction = createResearchDirection({
      id: "dir:axiom-hunt",
      title: "Hunt for an intermediate axiom",
      regionId: "region:topology-gap",
      motivation: "Existing theorems fail when regularity is dropped.",
      status: "open",
    });
    expect(direction.ok).toBe(true);
    const question = createOpenQuestion({
      id: "q:gap-1",
      prompt: "Is there a strictly weaker axiom that restores compactness implications?",
      regionId: "region:topology-gap",
      relatedEntityIds: [],
    });
    expect(question.ok).toBe(true);
  });
});

describe("Erdős frontier catalog", () => {
  it("projects open pointers without turning them into theorems", () => {
    const index = loadErdosIndex();
    expect(index.writes_canonical).toBe(false);
    expect(index.network).toBe(false);
    expect(index.not_a_theorem).toBe(true);
    expect(index.source).toBe("vendor/erdosproblems/data/problems.yaml");
    expect(index.counts.vendor_records).toBe(1217);
    expect(index.counts.additive_records).toBe(103);
    expect(index.counts.open_questions).toBe(49);
    expect(index.counts.audit_records).toBe(54);
    const projected = projectErdosFrontier();
    expect(projected.region.status).toBe("open");
    expect(projected.questions).toHaveLength(49);
    expect(projected.questions.every((row) => questionIsTheorem(row) === false)).toBe(true);
    expect(projected.questions.some((row) => row.id === "erdos:3")).toBe(true);
    expect(projected.questions.some((row) => row.id === "erdos:1")).toBe(false);
    const catalog = catalogErdosFrontier();
    expect(catalog.find((row) => row.id === "frontier")?.group).toBe("前沿");
    expect(catalog.find((row) => row.id === "frontier-audit")?.group).toBe("前沿备查");
    expect(catalog.find((row) => row.id === "erdos:3")?.body).toContain("Not a theorem");
    expect(catalog.find((row) => row.id === "erdos:1")?.group).toBe("前沿备查");
    expect(catalog.find((row) => row.id === "erdos:1")?.body).toContain("not_an_open_question");
    expect(catalog.every((row) => !row.body.includes("P00"))).toBe(true);
  });
});
