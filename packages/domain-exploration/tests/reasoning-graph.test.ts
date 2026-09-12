import { describe, expect, it } from "vitest";
import {
  addReasoningEdge,
  addReasoningNode,
  emptyReasoningGraph,
  projectLemmaReasoning,
  reasoningProvesTheorem,
} from "../src/index.ts";

describe("MathematicalReasoningGraph", () => {
  it("represents premise → transformation → conclusion without proving a theorem", () => {
    let graph = emptyReasoningGraph();
    const p = addReasoningNode(graph, { id: "n1", kind: "premise", content: "X is compact" });
    expect(p.ok).toBe(true);
    if (!p.ok) return;
    const t = addReasoningNode(p.graph, { id: "n2", kind: "transformation", content: "cover refinement" });
    expect(t.ok).toBe(true);
    if (!t.ok) return;
    const c = addReasoningNode(t.graph, { id: "n3", kind: "conclusion", content: "X is sequentially compact" });
    expect(c.ok).toBe(true);
    if (!c.ok) return;
    graph = c.graph;
    const req = addReasoningEdge(graph, { id: "e1", type: "requires", source: "n2", target: "n1" });
    expect(req.ok).toBe(true);
    if (!req.ok) return;
    const tr = addReasoningEdge(req.graph, { id: "e2", type: "transforms", source: "n1", target: "n3" });
    expect(tr.ok).toBe(true);
    if (!tr.ok) return;
    expect(reasoningProvesTheorem(tr.graph)).toBe(false);
  });

  it("rejects unknown endpoints and unknown edge types", () => {
    const graph = emptyReasoningGraph();
    const dangling = addReasoningEdge(graph, {
      id: "e",
      type: "contradicts",
      source: "a",
      target: "b",
    });
    expect(dangling.ok).toBe(false);
    const node = addReasoningNode(graph, { id: "a", kind: "premise", content: "A" });
    expect(node.ok).toBe(true);
    if (!node.ok) return;
    const self = addReasoningEdge(node.graph, { id: "e", type: "strengthens", source: "a", target: "a" });
    expect(self.ok).toBe(false);
  });

  it("projects lemma depends_on as requires and never proves a theorem", () => {
    const graph = projectLemmaReasoning([
      { id: "B", content: "odds are sum-free", dependsOn: [] },
      { id: "A", content: "length bound", dependsOn: ["B", "missing"] },
    ]);
    expect(graph.nodes.map((row) => row.kind)).toEqual(["premise", "conclusion"]);
    expect(graph.edges).toEqual([
      { id: "requires:A:B", type: "requires", source: "A", target: "B" },
    ]);
    expect(reasoningProvesTheorem(graph)).toBe(false);
  });
});
