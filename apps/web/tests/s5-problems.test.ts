import { describe, expect, it } from "vitest";
import { createRepository } from "@math-ai-lab/content";
import { knowledgeMappingLabel } from "@math-ai-lab/domain";

describe("S5 problems", () => {
  const repo = createRepository();

  it("uses YAML id for P0001 even when the filename is P001_", () => {
    const problem = repo.getProblem("P0001");
    expect(problem?.id).toBe("P0001");
    expect(problem?.sourcePath).toContain("P001_");
    expect(repo.getProblem("P001")).toBeNull();
  });

  it("keeps P0002 knowledge [] as mapping-complete", () => {
    const problem = repo.getProblem("P0002");
    expect(problem?.knowledge).toEqual([]);
    expect(knowledgeMappingLabel(problem!.knowledgeMapping)).toBe(
      "mapping 已完成，当前没有直接对象",
    );
    expect(problem?.objectStatus).toBe("reviewed");
    expect(problem?.workflowDir).toBe("已解决");
  });

  it("rejects path-like problem ids", () => {
    expect(repo.getProblem("../P0002")).toBeNull();
    expect(repo.problemView("P0002/../P0001")).toBeNull();
  });
});
