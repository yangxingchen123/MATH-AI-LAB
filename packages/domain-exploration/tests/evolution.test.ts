import { describe, expect, it } from "vitest";
import {
  addTheoryEdge,
  addTheoryNode,
  emptyEvolutionGraph,
  evolutionProvesTheorem,
} from "../src/index.ts";

describe("TheoryEvolutionGraph", () => {
  it("can record isolated modules without claiming a theorem", () => {
    const empty = emptyEvolutionGraph();
    expect(evolutionProvesTheorem(empty)).toBe(false);
    const first = addTheoryNode(empty, { id: "theory:Foo.lean", title: "Foo.lean" });
    expect(first.ok).toBe(true);
    if (!first.ok) return;
    const second = addTheoryNode(first.graph, { id: "theory:Bar.lean", title: "Bar.lean" });
    expect(second.ok).toBe(true);
    if (!second.ok) return;
    expect(second.graph.edges).toEqual([]);
    expect(evolutionProvesTheorem(second.graph)).toBe(false);
    const invented = addTheoryEdge(second.graph, {
      id: "e1",
      type: "unifies",
      source: "theory:Foo.lean",
      target: "theory:Bar.lean",
    });
    expect(invented.ok).toBe(true);
    if (!invented.ok) return;
    expect(evolutionProvesTheorem(invented.graph)).toBe(false);
  });
});
