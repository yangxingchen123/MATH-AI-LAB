import { describe, expect, it } from "vitest";
import type { Knowledge, Problem } from "@math-ai-lab/domain";
import { projectUniverse } from "@math-ai-lab/domain-math";
import {
  catalogExploration,
  lookupExploration,
  projectExploration,
  reasoningProvesTheorem,
  searchExplorationCatalog,
  notebookIsCanonical,
  sessionConclusionIsTheorem,
  evolutionProvesTheorem,
} from "../src/index.ts";

function knowledge(id: string): Knowledge {
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
  };
}

function problem(id: string): Problem {
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
  };
}

describe("exploration catalog", () => {
  it("looks up read-only items and rejects path traversal", () => {
    const snap = projectUniverse({
      knowledge: [knowledge("K0001")],
      problems: [problem("P0001")],
      methods: [],
      lean: [
        {
          id: "DISC-003",
          title: "odds are sum-free",
          sourceExists: true,
          status: "source_exists",
          leanFile: "06_LEAN形式化/MathAILab/Research/SumFree.lean",
        },
      ],
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
    });
    const projected = projectExploration(snap);
    expect(projected.state.reasoning[0]?.nodes).toHaveLength(1);
    expect(projected.state.reasoning[0]?.nodes[0]?.kind).toBe("premise");
    expect(reasoningProvesTheorem(projected.state.reasoning[0]!)).toBe(false);
    const catalog = catalogExploration(projected);
    expect(lookupExploration(catalog, "overview")?.group).toBe("总览");
    expect(lookupExploration(catalog, "reasoning")?.detail).toContain("proves_theorem=false");
    expect(lookupExploration(catalog, "reasoning:formal_proof:lean:DISC-003")?.title).toBe("odds are sum-free");
    expect(projected.briefing.patterns.every((row) => row.detail.includes("theorem=false"))).toBe(true);
    expect(lookupExploration(catalog, "notebook:projected")?.group).toBe("笔记本");
    expect(notebookIsCanonical(projected.state.notebooks[0]!)).toBe(false);
    expect(sessionConclusionIsTheorem(projected.state.sessions[0]!)).toBe(false);
    expect(projected.state.evolution[0]?.edges).toEqual([]);
    expect(evolutionProvesTheorem(projected.state.evolution[0]!)).toBe(false);
    expect(lookupExploration(catalog, "evolution")?.detail).toContain("proves_theorem=false");
    const hits = searchExplorationCatalog(catalog, "odds are sum-free");
    expect(hits.length).toBeGreaterThan(0);
    expect(hits.every((row) => row.status === "candidate")).toBe(true);
    expect(searchExplorationCatalog(catalog, "")).toEqual([]);
    expect(lookupExploration(catalog, "../元数据规范.md")).toBeNull();
    expect(lookupExploration(catalog, "reasoning/../../../secret")).toBeNull();
  });
});
