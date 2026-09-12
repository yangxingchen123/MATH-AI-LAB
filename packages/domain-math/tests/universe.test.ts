import { describe, expect, it } from "vitest";
import type { Knowledge, Method, Problem } from "@math-ai-lab/domain";
import {
  MockAIResearchProvider,
  createMathematicalEntity,
  dependencyIds,
  entityId,
  historyOf,
  isMathematicalTruth,
  projectUniverse,
  promoteToCanonical,
  provesCount,
  relatedIds,
  theoremCount,
  transitionCandidate,
  validateRelation,
} from "../src/index.ts";

function knowledge(id: string, extra?: Partial<Knowledge>): Knowledge {
  return {
    id,
    title: id,
    type: "knowledge",
    objectStatus: "reviewed",
    sourcePath: `01_知识库/${id}.md`,
    body: "",
    unknownFields: [],
    domain: "算术",
    aliases: [],
    prerequisites: [],
    related: [],
    ...extra,
  };
}

function problem(id: string, extra?: Partial<Problem>): Problem {
  return {
    id,
    title: id,
    type: "problem",
    objectStatus: "draft",
    sourcePath: `02_题目库/未解决/${id}.md`,
    workflowDir: "未解决",
    knowledgeMapping: { state: "omitted" },
    body: "",
    unknownFields: [],
    ...extra,
  };
}

function method(id: string, extra?: Partial<Method>): Method {
  return {
    id,
    title: id,
    type: "method",
    objectStatus: "draft",
    sourcePath: `12_方法库/${id}.md`,
    body: "",
    unknownFields: [],
    ...extra,
  };
}

describe("entity projection", () => {
  it("creates a projection entity only with required fields", () => {
    const ok = createMathematicalEntity({
      id: entityId("definition", "knowledge", "K0001"),
      title: "K0001",
      type: "definition",
      description: "projection",
      source: { kind: "knowledge", id: "K0001" },
      status: "projected",
    });
    expect(ok.ok).toBe(true);
    const missing = createMathematicalEntity({
      id: "",
      title: "x",
      type: "definition",
      description: "projection",
      source: { kind: "knowledge", id: "K0001" },
      status: "projected",
    });
    expect(missing.ok).toBe(false);
  });

  it("maps Knowledge to Definition, never Theorem", () => {
    const snap = projectUniverse({
      knowledge: [knowledge("K0001")],
      problems: [],
      methods: [],
    });
    expect(snap.entities).toHaveLength(1);
    expect(snap.entities[0]?.type).toBe("definition");
    expect(snap.entities[0]?.id).toBe(entityId("definition", "knowledge", "K0001"));
    expect(theoremCount(snap)).toBe(0);
  });

  it("maps Problem to Question and Method to Object", () => {
    const snap = projectUniverse({
      knowledge: [],
      problems: [problem("P0001")],
      methods: [method("M0001")],
    });
    expect(snap.entities.map((row) => row.type).sort()).toEqual(["object", "question"]);
  });
});

describe("relations", () => {
  it("emits explicit depends_on and derived reverse", () => {
    const snap = projectUniverse({
      knowledge: [knowledge("K0001"), knowledge("K0002", { prerequisites: ["K0001"] })],
      problems: [],
      methods: [],
    });
    const types = snap.relations.map((row) => row.type).sort();
    expect(types).toContain("depends_on");
    expect(types).toContain("derived_from");
    expect(snap.relations.every((row) => row.evidence.kind !== "none")).toBe(true);
  });

  it("emits uses from Problem.knowledge without inventing tags", () => {
    const snap = projectUniverse({
      knowledge: [knowledge("K0001")],
      problems: [problem("P0001", { knowledge: ["K0001"], knowledgeMapping: { state: "mapped", ids: ["K0001"] } })],
      methods: [method("M0001", { knowledge: ["K0001"] })],
    });
    expect(snap.relations.some((row) => row.type === "uses")).toBe(true);
    const deps = dependencyIds(
      { nodes: snap.entities, edges: snap.relations },
      entityId("question", "problem", "P0001"),
    );
    expect(deps).toContain(entityId("definition", "knowledge", "K0001"));
    expect(relatedIds({ nodes: snap.entities, edges: snap.relations }, entityId("definition", "knowledge", "K0001")).length).toBeGreaterThan(0);
    expect(
      snap.relations.every((row) => validateRelation(row, new Set(snap.entities.map((item) => item.id))).ok),
    ).toBe(true);
  });

  it("rejects relations without endpoints or evidence", () => {
    const empty = validateRelation({
      id: "x",
      type: "proves",
      source: "",
      target: "b",
      origin: "derived",
      evidence: { kind: "explicit_field" },
    });
    expect(empty.ok).toBe(false);
    const noEvidence = validateRelation({
      id: "x",
      type: "proves",
      source: "a",
      target: "b",
      origin: "derived",
      evidence: undefined as never,
    });
    expect(noEvidence.ok).toBe(false);
  });
});

describe("evidence and attempts", () => {
  it("records HumanProof from attempts but never proves a theorem", () => {
    const snap = projectUniverse({
      knowledge: [],
      problems: [problem("P0001")],
      methods: [],
      attempts: [
        {
          id: "A000001",
          problem: "P0001",
          outcome: "correct",
          assistance: "independent",
          attemptedAt: "2026-09-09T12:00+08:00",
        },
      ],
    });
    expect(snap.evidence).toHaveLength(1);
    expect(snap.evidence[0]?.evidenceType).toBe("HumanProof");
    expect(snap.evidence[0]?.confidence).toBe("human_claimed");
    expect(isMathematicalTruth(snap.evidence[0]!.confidence)).toBe(false);
    expect(provesCount(snap)).toBe(0);
    expect(theoremCount(snap)).toBe(0);
    expect(snap.events.some((row) => row.type === "ProofAttempt")).toBe(true);
    expect(snap.events.some((row) => row.type === "ProofCompleted")).toBe(false);
  });

  it("marks Lean Verified as machine_checked FormalProof", () => {
    const lean = {
      id: "ALG-001",
      title: "add_comm",
      sourceExists: true,
      status: "verified" as const,
      evidencePath: "06_LEAN形式化/manifests/ALG-001.yaml",
    };
    const snap = projectUniverse({
      knowledge: [],
      problems: [problem("P0001")],
      methods: [],
      lean: [lean],
      leanBindings: [{ sourceId: "P0001", sourceKind: "problem", lean }],
    });
    const fp = snap.entities.find((row) => row.type === "formal_proof");
    expect(fp?.status).toBe("formal_verified");
    expect(snap.evidence.some((row) => row.confidence === "machine_checked")).toBe(true);
    expect(snap.relations.some((row) => row.type === "verified_by")).toBe(true);
  });

  it("does not treat source_exists Lean as Verified", () => {
    const snap = projectUniverse({
      knowledge: [],
      problems: [],
      methods: [],
      lean: [{ id: "X", title: "x", sourceExists: true, status: "source_exists" }],
    });
    expect(snap.entities[0]?.status).not.toBe("formal_verified");
    expect(snap.evidence[0]?.confidence).toBe("none");
  });
});

describe("candidate lifecycle", () => {
  it("projects Lab as Candidate and never auto-promotes", () => {
    const snap = projectUniverse({
      knowledge: [],
      problems: [],
      methods: [],
      lab: [
        {
          id: "C001",
          title: "fake conjecture",
          kind: "conjecture",
          sourcePath: "tools/research_lab/conjectures/C001.yaml",
          leanDecls: [],
          candidate: true,
        },
      ],
    });
    expect(snap.candidates).toHaveLength(1);
    expect(snap.candidates[0]?.status).toBe("exploring");
    expect(snap.entities[0]?.status).toBe("candidate");
    expect(promoteToCanonical(snap.candidates[0]!).ok).toBe(false);
    const blocked = transitionCandidate(snap.candidates[0]!, "promoted", { humanReview: false });
    expect(blocked.ok).toBe(false);
    const skip = transitionCandidate(snap.candidates[0]!, "promoted", { humanReview: true });
    expect(skip.ok).toBe(false);
    const noReview = transitionCandidate(snap.candidates[0]!, "supported", { humanReview: false });
    expect(noReview.ok).toBe(false);
    const exploreToSupported = transitionCandidate(snap.candidates[0]!, "supported", { humanReview: true });
    expect(exploreToSupported.ok).toBe(true);
    if (exploreToSupported.ok) {
      const promoted = transitionCandidate(exploreToSupported.candidate, "promoted", { humanReview: true });
      expect(promoted.ok).toBe(true);
      if (promoted.ok) {
        expect(promoted.candidate.status).toBe("promoted");
        expect(promoteToCanonical(promoted.candidate).ok).toBe(false);
      }
    }
  });
});

describe("graph, timeline, spaces, AI mock", () => {
  it("builds domain spaces and history without writing", () => {
    const snap = projectUniverse({
      knowledge: [knowledge("K0001")],
      problems: [problem("P0001")],
      methods: [],
      attempts: [{ id: "A000001", problem: "P0001", outcome: "unassessed", assistance: "independent" }],
      research: [
        {
          type: "research_project",
          id: "美赛2026-A",
          slug: "美赛2026-A",
          title: "美赛2026-A",
          kind: "contest_modeling",
          sourcePath: "07_项目/美赛2026-A/research_dossier.md",
          sections: [],
        },
      ],
    });
    expect(snap.spaces.some((row) => row.origin === "knowledge_domain")).toBe(true);
    expect(snap.spaces.some((row) => row.origin === "research_project")).toBe(true);
    const qid = entityId("question", "problem", "P0001");
    expect(historyOf(snap.events, qid).some((row) => row.type === "ProofAttempt")).toBe(true);
  });

  it("mock AI only returns idea candidates", () => {
    const ai = new MockAIResearchProvider();
    const out = ai.suggest("sum-free");
    expect(out.candidates[0]?.origin).toBe("ai_mock");
    expect(out.candidates[0]?.status).toBe("idea");
    expect(out.warning.toLowerCase()).toContain("never");
    expect(promoteToCanonical(out.candidates[0]!).ok).toBe(false);
  });
});
