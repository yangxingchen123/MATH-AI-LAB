/** Old theory → generalization → new theory. Distinct from reasoning graphs and Universe relations. */

export const EVOLUTION_RELATIONS = ["extends", "simplifies", "unifies", "specializes"] as const;

export type EvolutionRelation = (typeof EVOLUTION_RELATIONS)[number];

export interface TheoryNode {
  id: string;
  title: string;
}

export interface TheoryEdge {
  id: string;
  type: EvolutionRelation;
  source: string;
  target: string;
}

export interface TheoryEvolutionGraph {
  nodes: TheoryNode[];
  edges: TheoryEdge[];
}

export function emptyEvolutionGraph(): TheoryEvolutionGraph {
  return { nodes: [], edges: [] };
}

export function addTheoryNode(
  graph: TheoryEvolutionGraph,
  node: TheoryNode,
): { ok: true; graph: TheoryEvolutionGraph } | { ok: false; error: string } {
  if (!node.id?.trim() || !node.title?.trim()) {
    return { ok: false, error: "Theory node requires id and title." };
  }
  if (graph.nodes.some((row) => row.id === node.id)) {
    return { ok: false, error: "Duplicate theory node id." };
  }
  return { ok: true, graph: { ...graph, nodes: [...graph.nodes, node] } };
}

export function addTheoryEdge(
  graph: TheoryEvolutionGraph,
  edge: TheoryEdge,
): { ok: true; graph: TheoryEvolutionGraph } | { ok: false; error: string } {
  if (!EVOLUTION_RELATIONS.includes(edge.type)) {
    return { ok: false, error: "Unknown evolution relation." };
  }
  const ids = new Set(graph.nodes.map((row) => row.id));
  if (!ids.has(edge.source) || !ids.has(edge.target) || edge.source === edge.target) {
    return { ok: false, error: "Evolution edge requires distinct known theories." };
  }
  return { ok: true, graph: { ...graph, edges: [...graph.edges, edge] } };
}

export function evolutionProvesTheorem(_graph: TheoryEvolutionGraph): false {
  return false;
}
