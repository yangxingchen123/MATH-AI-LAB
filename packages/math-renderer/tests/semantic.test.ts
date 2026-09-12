import { describe, expect, it } from "vitest";
import { enhanceSemanticBlocks, renderDocument } from "../src/index.ts";

describe("semantic and math UX", () => {
  it("enhances only clearly marked blocks", () => {
    const enhanced = enhanceSemanticBlocks("定理. 若凸则…\n\n普通段落。\n");
    expect(enhanced).toContain("math-theorem");
    expect(enhanced).toContain("普通段落");
    expect(enhanceSemanticBlocks("普通段落。\n")).not.toContain("math-block");
  });

  it("adds copy LaTeX on display formulas", () => {
    const doc = renderDocument("$$x+y$$\n");
    expect(doc.html).toContain("math-copy");
    expect(doc.html).toContain("data-tex");
  });

  it("marks reserved IDs as broken when catalog is provided", () => {
    const doc = renderDocument("见 P0000 与 P0002。", {
      knownIds: ["P0002"],
    });
    expect(doc.html).toContain("broken-ref");
    expect(doc.html).toContain("/problems/P0002");
  });
});
