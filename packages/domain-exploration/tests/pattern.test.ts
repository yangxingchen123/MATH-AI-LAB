import { describe, expect, it } from "vitest";
import { createPattern, patternIsTheorem, projectRecurringPatterns } from "../src/index.ts";

describe("MathematicalPattern", () => {
  it("records recurring structure without becoming a theorem", () => {
    const made = createPattern({
      id: "pat:symmetry-1",
      pattern: "Pairing n and n+1 avoids 2-term sums inside the set",
      kind: "symmetry",
      instances: ["obs:1", "obs:2"],
      supportingEvidence: ["evidence:run:1"],
      confidence: "heuristic",
      relatedTheory: ["definition:knowledge:K0001"],
    });
    expect(made.ok).toBe(true);
    if (made.ok) {
      expect(patternIsTheorem(made.pattern)).toBe(false);
    }
  });

  it("rejects confidence that would look like mathematical truth", () => {
    const bad = createPattern({
      id: "pat:x",
      pattern: "hidden correspondence",
      kind: "hidden_correspondence",
      instances: [],
      supportingEvidence: [],
      confidence: "machine_checked" as never,
      relatedTheory: [],
    });
    expect(bad.ok).toBe(false);
  });

  it("projects only recurring groups and never a theorem", () => {
    const rows = projectRecurringPatterns([
      {
        id: "pattern:family:ALG",
        pattern: "algebra cluster",
        kind: "repeated_relationship",
        instances: ["formal_proof:lean:ALG-001"],
      },
      {
        id: "pattern:family:ANL",
        pattern: "analysis cluster",
        kind: "repeated_relationship",
        instances: ["formal_proof:lean:ANL-001", "formal_proof:lean:ANL-004"],
      },
    ]);
    expect(rows).toHaveLength(1);
    expect(rows[0]?.id).toBe("pattern:family:ANL");
    expect(rows[0]?.confidence).toBe("heuristic");
    expect(patternIsTheorem(rows[0]!)).toBe(false);
  });
});
