import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { renderDocument, renderFormula } from "../src/index.ts";

const fixtureDir = join(dirname(fileURLToPath(import.meta.url)), "fixtures");

function fixture(name: string): string {
  return readFileSync(join(fixtureDir, name), "utf8");
}

describe("formula isolation", () => {
  it("renders \\alpha_i without splitting the subscript", () => {
    const result = renderFormula("\\alpha_i", false);
    expect(result.ok).toBe(true);
    expect(result.html).toContain("katex");
    expect(result.tex).toBe("\\alpha_i");
  });

  it("keeps illegal \\alphai as an error and does not rewrite it", () => {
    const result = renderFormula("\\alphai", false);
    expect(result.ok).toBe(false);
    expect(result.tex).toBe("\\alphai");
    expect(result.html).toContain("Formula rendering error");
    expect(result.html).toContain("\\alphai");
  });
});

describe("document fixtures", () => {
  it("renders mixed Chinese and math", () => {
    const doc = renderDocument(fixture("zh-math.md"));
    expect(doc.html).toContain("勒让德");
    expect(doc.html).toContain("katex");
    expect(doc.formulas.every((row) => row.ok)).toBe(true);
  });

  it("renders inline and display formulas", () => {
    const doc = renderDocument(fixture("inline-display.md"));
    expect(doc.html).toContain("math-inline");
    expect(doc.html).toContain("math-display");
    expect(doc.formulas).toHaveLength(2);
  });

  it("renders a long display formula inside an overflow box", () => {
    const doc = renderDocument(fixture("long-formula.md"));
    expect(doc.html).toContain("math-display");
    expect(doc.html).not.toMatch(/<body[^>]*overflow/);
  });

  it("renders matrix, cases, and aligned", () => {
    const doc = renderDocument(fixture("structures.md"));
    expect(doc.formulas.every((row) => row.ok)).toBe(true);
    expect(doc.html).toContain("katex");
  });

  it("isolates an illegal command from the rest of the page", () => {
    const doc = renderDocument(fixture("illegal.md"));
    expect(doc.html).toContain("这段文字必须保留");
    expect(doc.html).toContain("Formula rendering error");
    expect(doc.formulas.some((row) => !row.ok && row.tex === "\\alphai")).toBe(
      true,
    );
    expect(doc.formulas.some((row) => row.ok)).toBe(true);
  });

  it("reports an unclosed math environment without dropping later text", () => {
    const doc = renderDocument(fixture("unclosed.md"));
    expect(doc.html).toContain("结尾仍在");
    expect(doc.formulas.some((row) => row.error === "Unclosed math delimiter")).toBe(
      true,
    );
  });

  it("renders a table that contains formulas", () => {
    const doc = renderDocument(fixture("table-math.md"));
    expect(doc.html).toContain("<table>");
    expect(doc.html).toContain("katex");
  });

  it("adds heading anchors and autolinks Frozen IDs", () => {
    const doc = renderDocument("# 标题\n\n见 P0002 与 K0001。\n");
    expect(doc.headings[0]?.id).toBe("标题");
    expect(doc.html).toContain('id="标题"');
    expect(doc.html).toContain("/problems/P0002");
    expect(doc.html).toContain("/knowledge/K0001");
  });

  it("does not treat dollar signs inside code as math", () => {
    const doc = renderDocument("use `$x$` in code\n");
    expect(doc.formulas).toHaveLength(0);
    expect(doc.html).toContain("<code>");
  });
});
