import { describe, expect, it } from "vitest";
import type { Knowledge, Problem } from "@math-ai-lab/domain";
import { projectUniverse, theoremCount } from "@math-ai-lab/domain-math";
import {
  LexicalSearchProvider,
  LexicalSimilarityEngine,
  executeCanonicalWrite,
  notebookIsCanonical,
  projectExploration,
  sessionConclusionIsTheorem,
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

describe("projectExploration", () => {
  it("answers the five exploration questions without writing canonical or inventing theorems", () => {
    const snap = projectUniverse({
      knowledge: [knowledge("K0001")],
      problems: [problem("P0001")],
      methods: [],
      attempts: [{ id: "A000001", problem: "P0001", outcome: "incorrect", assistance: "independent" }],
      lab: [
        {
          id: "C001",
          title: "lab conjecture",
          kind: "conjecture",
          sourcePath: "tools/research_lab/conjectures/C001.yaml",
          leanDecls: [],
          candidate: true,
          stage: "FALSIFICATION",
        },
      ],
      research: [
        {
          type: "research_project",
          id: "gap",
          slug: "gap",
          title: "Open gap",
          kind: "research",
          sourcePath: "07_项目/gap/research_dossier.md",
          sections: [],
        },
      ],
    });
    const { state, briefing } = projectExploration(snap);
    expect(briefing.layer).toBe("exploration");
    expect(briefing.writesCanonical).toBe(false);
    expect(briefing.theoremCount).toBe(0);
    expect(theoremCount(snap)).toBe(0);
    expect(state.conjectures).toHaveLength(1);
    expect(state.conjectures[0]?.state).toBe("challenged");
    expect(state.pipelines).toHaveLength(1);
    expect(state.pipelines[0]?.stage).toBe("experiment");
    expect(state.pipelines[0]?.formalVerification).toBe("pending");
    expect(briefing.exploring[0]?.pipeline).toBe("experiment");
    expect(briefing.exploring.length).toBeGreaterThan(0);
    expect(briefing.known.length).toBeGreaterThan(0);
    expect(briefing.belief.some((row) => row.detail.includes("HumanProof"))).toBe(true);
    expect(briefing.failures.length).toBeGreaterThan(0);
    expect(briefing.next.some((row) => row.id.includes("gap"))).toBe(true);
    expect(briefing.answers.what_we_explore).toContain("candidate");
    expect(state.failures.length).toBeGreaterThan(0);
    expect(state.memory?.failure.recordIds.length).toBeGreaterThan(0);
    expect(state.reasoning[0]?.nodes ?? []).toEqual([]);
    expect(state.notebooks[0]?.id).toBe("notebook:projected");
    expect(notebookIsCanonical(state.notebooks[0]!)).toBe(false);
    expect(sessionConclusionIsTheorem(state.sessions[0]!)).toBe(false);
    expect(state.evolution).toEqual([]);
    expect(executeCanonicalWrite(snap.candidates[0]!).ok).toBe(false);
  });
});

describe("lexical interfaces", () => {
  it("returns candidates from title overlap and never theorems", () => {
    const engine = new LexicalSimilarityEngine([
      { id: "a", title: "sum-free odds construction" },
      { id: "b", title: "sum-free upper half" },
      { id: "c", title: "compactness without Hausdorff" },
    ]);
    const hits = engine.findAnalogies("a");
    expect(hits.length).toBeGreaterThan(0);
    expect(hits.every((row) => row.status === "idea" && row.origin === "ai_mock")).toBe(true);
    const search = new LexicalSearchProvider({
      failure: [{ id: "fail:1", title: "compactness without Hausdorff" }],
    });
    expect(search.searchFailure("compactness")[0]?.status).toBe("candidate");
    expect(search.searchProof("compactness")).toEqual([]);
  });
});
