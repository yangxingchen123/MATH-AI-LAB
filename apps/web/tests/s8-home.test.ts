import { describe, expect, it } from "vitest";
import { createRepository } from "@math-ai-lab/content";

describe("home counts", () => {
  it("uses real repository sizes", () => {
    const repo = createRepository();
    expect(repo.listKnowledge().length).toBe(2);
    expect(repo.listProblems().length).toBe(2);
    expect(repo.listMethods().length).toBe(2);
    expect(repo.listResearch().length).toBe(1);
  });
});
