import { describe, expect, it } from "vitest";
import {
  concludeSession,
  createMemory,
  createNotebook,
  createSession,
  notebookIsCanonical,
  recordSessionAction,
  sessionConclusionIsTheorem,
} from "../src/index.ts";

const human = { type: "Human" as const, id: "冲" };

describe("ResearchSession", () => {
  it("records one research activity with attributed actions", () => {
    const made = createSession({
      id: "session:topology-1",
      researcher: human,
      goal: "Investigating generalized topology theorem",
      inputs: ["obs:1", "region:topology-gap"],
    });
    expect(made.ok).toBe(true);
    if (!made.ok) return;
    const acted = recordSessionAction(made.session, {
      actor: human,
      kind: "modified_assumption",
      description: "Human modified regularity hypothesis",
      timestamp: "2026-09-09T16:10+08:00",
    });
    expect(acted.ok).toBe(true);
    if (!acted.ok) return;
    const done = concludeSession(acted.session, "Need a boundedness-type extra axiom.");
    expect(sessionConclusionIsTheorem(done)).toBe(false);
    expect(done.actions).toHaveLength(1);
  });

  it("notebook is exploration history, not canonical mathematics", () => {
    const nb = createNotebook({
      id: "nb:1",
      title: "Topology gap notes",
      observations: ["obs:1"],
      questions: ["q:gap-1"],
    });
    expect(nb.ok).toBe(true);
    if (!nb.ok) return;
    expect(notebookIsCanonical(nb.notebook)).toBe(false);
    const mem = createMemory({
      shortTerm: { sessionId: "session:topology-1", notebookId: "nb:1" },
      longTerm: { verifiedEntityIds: ["formal_proof:lean:ALG-001"] },
      failure: { recordIds: ["fail:compactness-without-hausdorff"] },
    });
    expect(mem.ok).toBe(true);
  });
});
