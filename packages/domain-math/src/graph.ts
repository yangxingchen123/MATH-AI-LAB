import type { MathematicalEntity } from "./entity.ts";
import type { MathematicalRelation } from "./relation.ts";
import type { ResearchEvent } from "./event.ts";

export interface MathGraph {
  nodes: MathematicalEntity[];
  edges: MathematicalRelation[];
}

export function relatedIds(graph: MathGraph, entityId: string): string[] {
  const found = new Set<string>();
  for (const edge of graph.edges) {
    if (edge.source === entityId) found.add(edge.target);
    if (edge.target === entityId) found.add(edge.source);
  }
  return [...found].sort();
}

export function dependencyIds(graph: MathGraph, entityId: string): string[] {
  const walk = new Set<string>();
  const stack = [entityId];
  while (stack.length > 0) {
    const current = stack.pop()!;
    for (const edge of graph.edges) {
      if (edge.source !== current) continue;
      if (edge.type !== "depends_on" && edge.type !== "uses") continue;
      if (walk.has(edge.target)) continue;
      walk.add(edge.target);
      stack.push(edge.target);
    }
  }
  return [...walk].sort();
}

export function historyOf(events: ResearchEvent[], entityId: string): ResearchEvent[] {
  return events
    .filter((event) => event.relatedEntity === entityId)
    .sort((a, b) => (a.timestamp ?? "").localeCompare(b.timestamp ?? "") || a.id.localeCompare(b.id));
}
