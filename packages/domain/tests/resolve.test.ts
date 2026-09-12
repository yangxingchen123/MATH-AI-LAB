import { describe, expect, it } from "vitest";
import { resolveContentRef } from "../src/index.ts";

describe("resolveContentRef", () => {
  it("resolves well-formed Frozen IDs", () => {
    expect(resolveContentRef("K0001")).toMatchObject({
      status: "ok",
      href: "/knowledge/K0001",
    });
    expect(resolveContentRef("P0002").href).toBe("/problems/P0002");
    expect(resolveContentRef("M0001").href).toBe("/methods/M0001");
  });

  it("marks reserved and missing IDs as broken when a catalog is given", () => {
    const catalog = new Set(["K0001", "P0002"]);
    expect(resolveContentRef("K0000", catalog).status).toBe("broken");
    expect(resolveContentRef("P0001", catalog)).toMatchObject({
      status: "broken",
      reason: "missing",
    });
    expect(resolveContentRef("not-an-id", catalog).status).toBe("ignore");
  });

  it("does not treat research slugs as Frozen IDs", () => {
    expect(resolveContentRef("美赛2026-A").status).toBe("ignore");
  });
});
