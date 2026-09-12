import { describe, expect, it } from "vitest";
import { explorationFromRepository, explorationItem } from "../src/lib/exploration";
import { reasoningProvesTheorem, searchExplorationCatalog } from "@math-ai-lab/domain-exploration";

describe("exploration projection safety", () => {
  it("answers process questions without inventing theorems or writing canonical", () => {
    const { briefing, state, catalog } = explorationFromRepository();
    expect(briefing.layer).toBe("exploration");
    expect(briefing.writesCanonical).toBe(false);
    expect(briefing.theoremCount).toBe(0);
    expect(briefing.exploring.every((row) => row.detail.includes("not a theorem"))).toBe(true);
    expect(briefing.answers.what_is_next.toLowerCase()).toContain("promotion");
    expect(state.conjectures.every((row) => row.state !== "resolved")).toBe(true);
    expect(state.reasoning[0]).toBeDefined();
    expect(reasoningProvesTheorem(state.reasoning[0]!)).toBe(false);
    expect(catalog.some((row) => row.id === "reasoning")).toBe(true);
    expect(catalog.some((row) => row.id === "notebook:projected")).toBe(true);
    expect(explorationItem("notebook:projected")?.group).toBe("笔记本");
    expect(briefing.patterns.every((row) => row.detail.includes("theorem=false"))).toBe(true);
    expect(explorationItem("overview")?.group).toBe("总览");
    expect(explorationItem("frontier")?.group).toBe("前沿");
    expect(explorationItem("erdos:3")?.body).toContain("Not a theorem");
    expect(explorationItem("erdos:1")?.group).toBe("前沿备查");
    expect(explorationItem("frontier-audit")?.group).toBe("前沿备查");
    expect(explorationItem("../元数据规范.md")).toBeNull();
    expect(searchExplorationCatalog(catalog, "overview").some((hit) => hit.id === "overview")).toBe(true);
    expect(searchExplorationCatalog(catalog, "overview").every((hit) => hit.status === "candidate")).toBe(true);
  });
});
