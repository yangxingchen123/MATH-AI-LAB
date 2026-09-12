import { describe, expect, it } from "vitest";
import { createRepository } from "../src/index.ts";

describe("research dossiers", () => {
  const repo = createRepository();

  it("only maps 07_项目 and never invents R ids", () => {
    const rows = repo.listResearch();
    expect(rows.map((row) => row.slug)).toEqual(["美赛2026-A"]);
    expect(rows[0]?.kind).toBe("contest_modeling");
    expect(rows[0]?.id).toBe("美赛2026-A");
    expect(rows[0]?.id.startsWith("R")).toBe(false);
    expect(rows[0]?.sections.some((section) => section.id === "question")).toBe(
      true,
    );
    expect(rows.some((row) => row.slug === "_模板")).toBe(false);
  });

  it("does not treat researching problems as dossiers", () => {
    expect(repo.getResearch("P0002")).toBeNull();
    expect(repo.getProblem("美赛2026-A")).toBeNull();
    expect(repo.getResearch("../美赛2026-A")).toBeNull();
    expect(repo.getResearch("_模板")).toBeNull();
  });
});
