/**
 * Reasoning graph: premise → transformation → intermediate → conclusion.
 * Distinct from Universe MathGraph (entity knowledge graph).
 */

export const REASONING_NODE_KINDS = ["premise", "transformation", "intermediate", "conclusion"] as const;

export type ReasoningNodeKind = (typeof REASONING_NODE_KINDS)[number];

export const REASONING_EDGE_TYPES = [
  "requires",
  "transforms",
  "strengthens",
  "weakens",
  "contradicts",
  "generalizes",
] as const;

export type ReasoningEdgeType = (typeof REASONING_EDGE_TYPES)[number];

export interface ReasoningNode {
  id: string;
  kind: ReasoningNodeKind;
  content: string;
}

export interface ReasoningEdge {
  id: string;
  type: ReasoningEdgeType;
  source: string;
  target: string;
}

export interface MathematicalReasoningGraph {
  nodes: ReasoningNode[];
  edges: ReasoningEdge[];
}

export function emptyReasoningGraph(): MathematicalReasoningGraph {
  return { nodes: [], edges: [] };
}

export function addReasoningNode(
  graph: MathematicalReasoningGraph,
  node: ReasoningNode,
): { ok: true; graph: MathematicalReasoningGraph } | { ok: false; error: string } {
  if (!node.id?.trim() || !node.content?.trim()) {
    return { ok: false, error: "Reasoning node requires id and content." };
  }
  if (!REASONING_NODE_KINDS.includes(node.kind)) {
    return { ok: false, error: "Unknown reasoning node kind." };
  }
  if (graph.nodes.some((row) => row.id === node.id)) {
    return { ok: false, error: "Duplicate reasoning node id." };
  }
  return { ok: true, graph: { ...graph, nodes: [...graph.nodes, node] } };
}

export function addReasoningEdge(
  graph: MathematicalReasoningGraph,
  edge: ReasoningEdge,
): { ok: true; graph: MathematicalReasoningGraph } | { ok: false; error: string } {
  if (!REASONING_EDGE_TYPES.includes(edge.type)) {
    return { ok: false, error: "Unknown reasoning edge type." };
  }
  if (edge.source === edge.target) {
    return { ok: false, error: "Reasoning edge endpoints must differ." };
  }
  const ids = new Set(graph.nodes.map((row) => row.id));
  if (!ids.has(edge.source) || !ids.has(edge.target)) {
    return { ok: false, error: "Reasoning edge endpoints must be known nodes." };
  }
  return { ok: true, graph: { ...graph, edges: [...graph.edges, edge] } };
}

export function reasoningProvesTheorem(_graph: MathematicalReasoningGraph): false {
  return false;
}

export interface LemmaDecl {
  id: string;
  content: string;
  dependsOn?: string[];
}

/**
 * Project declared lemma dependencies into a reasoning graph.
 * File-order adjacency is not a reasoning edge.
 * The graph never proves a theorem.
 */
export function projectLemmaReasoning(lemmas: LemmaDecl[]): MathematicalReasoningGraph {
  const ids = new Set(lemmas.map((row) => row.id).filter((id) => id.trim()));
  const depended = new Set<string>();
  for (const lemma of lemmas) {
    for (const dep of lemma.dependsOn ?? []) {
      if (ids.has(dep)) depended.add(dep);
    }
  }
  let graph = emptyReasoningGraph();
  for (const lemma of lemmas) {
    if (!lemma.id.trim()) continue;
    const deps = (lemma.dependsOn ?? []).filter((dep) => ids.has(dep) && dep !== lemma.id);
    const kind: ReasoningNodeKind =
      deps.length === 0 ? "premise" : depended.has(lemma.id) ? "intermediate" : "conclusion";
    const added = addReasoningNode(graph, {
      id: lemma.id,
      kind,
      content: lemma.content.trim() || lemma.id,
    });
    if (added.ok) graph = added.graph;
  }
  for (const lemma of lemmas) {
    for (const dep of lemma.dependsOn ?? []) {
      if (!ids.has(dep) || dep === lemma.id) continue;
      const added = addReasoningEdge(graph, {
        id: `requires:${lemma.id}:${dep}`,
        type: "requires",
        source: lemma.id,
        target: dep,
      });
      if (added.ok) graph = added.graph;
    }
  }
  return graph;
}
