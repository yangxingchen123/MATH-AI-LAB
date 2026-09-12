import { describe, expect, it } from "vitest";
import {
  createProofStrategy,
  scanNamedProofStrategies,
  strategyIsProof,
} from "../src/index.ts";

describe("ProofStrategy", () => {
  it("scans named tactics lexically and never stores a proof", () => {
    const rows = scanNamedProofStrategies([
      { id: "ALG-004", body: "theorem add_comm := by\n  induction m with\n  | zero => rfl" },
      { id: "DISC-003", body: "theorem odds_sum_free (n : Nat) : isSumFree (odds n) := by\n  intro" },
      { id: "DISC-005", body: "theorem one_two_three_not_sum_free := by\n  intro h" },
    ]);
    expect(rows.map((row) => row.strategy)).toEqual(["induction", "algebraic_construction"]);
    expect(rows[0]?.successfulCases).toEqual(["ALG-004"]);
    expect(rows[1]?.successfulCases).toEqual(["DISC-003"]);
    expect(rows.every((row) => strategyIsProof(row) === false)).toBe(true);
    expect(rows.some((row) => row.strategy === "compactness")).toBe(false);
    const made = createProofStrategy({
      id: "strategy:compactness",
      strategy: "compactness",
      applicableConditions: ["Hausdorff"],
      successfulCases: [],
      failedCases: [],
      limitations: ["Not scanned from this warehouse."],
    });
    expect(made.ok).toBe(true);
    if (!made.ok) return;
    expect(strategyIsProof(made.strategy)).toBe(false);
  });
});
