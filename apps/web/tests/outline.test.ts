import { describe, expect, it } from "vitest";
import { createRepository } from "@math-ai-lab/content";
import { problemOutline, researchOutline } from "../src/lib/outline";

describe("TOC outlines", () => {
  it("includes P0002 parts", () => {
    const repo = createRepository();
    const view = repo.problemView("P0002");
    expect(view).not.toBeNull();
    const headings = problemOutline(view!);
    expect(headings.map((item) => item.text)).toEqual(
      expect.arrayContaining(["题面", "Part (a)", "Part (b)", "Part (c)"]),
    );
    const ids = headings.map((item) => item.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("covers research dossier sections", () => {
    const project = createRepository().getResearch("美赛2026-A");
    expect(project).not.toBeNull();
    const headings = researchOutline(project!);
    expect(headings.some((item) => item.id === "overview")).toBe(true);
    expect(headings.some((item) => item.id === "timeline")).toBe(true);
  });
});
