import type { KnowledgeMapping } from "./types.ts";

/**
 * UI copy for Problem.knowledge. Frozen semantics:
 * reviewed + [] = mapping finished, no suitable Knowledge — not "unknown".
 */
export function knowledgeMappingOf(
  knowledge: string[] | undefined,
): KnowledgeMapping {
  if (knowledge === undefined) {
    return { state: "omitted" };
  }
  if (knowledge.length === 0) {
    return { state: "complete_empty" };
  }
  return { state: "mapped", ids: knowledge };
}

export function knowledgeMappingLabel(mapping: KnowledgeMapping): string {
  if (mapping.state === "omitted") {
    return "knowledge 未写（draft 可省略）";
  }
  if (mapping.state === "complete_empty") {
    return "mapping 已完成，当前没有直接对象";
  }
  return mapping.ids.join(", ");
}
