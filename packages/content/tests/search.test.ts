import { describe, expect, it } from "vitest";
import { buildSearchIndex, createRepository } from "../src/index.ts";

describe("local search", () => {
  const search = buildSearchIndex(createRepository());

  it("finds golden Chinese and English objects", () => {
    expect(search.search("勒让德")[0]?.id).toBe("K0001");
    expect(search.search("Legendre")[0]?.id).toBe("K0001");
    expect(search.search("P0002")[0]?.type).toBe("problem");
    expect(search.search("Sylvester").length + search.search("AX-XB").length).toBeGreaterThan(
      0,
    );
    expect(search.search("美赛")[0]?.type).toBe("research_project");
  });

  it("excludes templates and reserved IDs", () => {
    expect(search.search("P0000")).toEqual([]);
    expect(search.search("K0000")).toEqual([]);
    expect(search.search("待填写")).toEqual([]);
  });
});
