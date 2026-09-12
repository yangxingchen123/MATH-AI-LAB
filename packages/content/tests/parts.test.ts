import { describe, expect, it } from "vitest";
import { createRepository } from "../src/index.ts";

describe("problem parts", () => {
  const repo = createRepository();

  it("keeps P0001 as a single body", () => {
    const view = repo.problemView("P0001");
    expect(view?.parts).toEqual([]);
    expect(view?.shared.includes("勒让德")).toBe(true);
  });

  it("splits P0002 into a, b, c without inventing empty blocks", () => {
    const view = repo.problemView("P0002");
    expect(view?.parts.map((part) => part.id)).toEqual(["a", "b", "c"]);
    expect(view?.parts[0]?.statement).toContain("特征值");
    expect(view?.parts[0]?.solution).toContain("秩一");
    expect(view?.parts[1]?.solution).toContain("可对角化");
    expect(view?.parts[2]?.solution).toContain("单射");
    expect(view?.shared).toContain("Working assumption");
  });

  it("reads real Attempt ledger only", () => {
    expect(repo.listAttempts("P0001")).toEqual([]);
    const attempts = repo.listAttempts("P0002");
    expect(attempts.map((row) => row.id)).toContain("A000001");
    expect(attempts.every((row) => row.problem === "P0002")).toBe(true);
    expect(repo.listAttempts("../P0002")).toEqual([]);
  });
});
