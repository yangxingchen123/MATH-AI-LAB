/** Projection-only mathematical entity. Not Frozen Schema. */

export const MATH_ENTITY_TYPES = [
  "definition",
  "object",
  "statement",
  "theorem",
  "lemma",
  "conjecture",
  "question",
  "proof",
  "counterexample",
  "experiment",
  "evidence",
  "artifact",
  "formal_proof",
] as const;

export type MathEntityType = (typeof MATH_ENTITY_TYPES)[number];

export const MATH_ENTITY_STATUSES = [
  "projected",
  "candidate",
  "supported_by_evidence",
  "formal_verified",
] as const;

export type MathEntityStatus = (typeof MATH_ENTITY_STATUSES)[number];

export const MATH_SOURCE_KINDS = [
  "knowledge",
  "problem",
  "method",
  "attempt",
  "lean",
  "lab",
  "research",
  "output",
  "ai_mock",
] as const;

export type MathSourceKind = (typeof MATH_SOURCE_KINDS)[number];

export interface MathEntitySource {
  kind: MathSourceKind;
  id: string;
  href?: string;
  sourcePath?: string;
}

export interface MathematicalEntity {
  id: string;
  title: string;
  type: MathEntityType;
  description: string;
  source: MathEntitySource;
  status: MathEntityStatus;
  created?: string;
  updated?: string;
}

export function entityId(type: MathEntityType, sourceKind: MathSourceKind, sourceId: string): string {
  return `${type}:${sourceKind}:${sourceId}`;
}

export function createMathematicalEntity(
  input: MathematicalEntity,
): { ok: true; entity: MathematicalEntity } | { ok: false; error: string } {
  if (!MATH_ENTITY_TYPES.includes(input.type)) {
    return { ok: false, error: "Unknown entity type." };
  }
  if (!MATH_ENTITY_STATUSES.includes(input.status)) {
    return { ok: false, error: "Unknown entity status." };
  }
  if (!input.id?.trim() || !input.title?.trim() || !input.description?.trim()) {
    return { ok: false, error: "Entity requires id, title, and description." };
  }
  if (!input.source || !MATH_SOURCE_KINDS.includes(input.source.kind) || !input.source.id.trim()) {
    return { ok: false, error: "Entity requires a source kind and source id." };
  }
  return { ok: true, entity: input };
}

export function parseEntityId(
  raw: string,
): { type: MathEntityType; sourceKind: MathSourceKind; sourceId: string } | null {
  const parts = raw.split(":");
  if (parts.length < 3) return null;
  const type = parts[0] as MathEntityType;
  const sourceKind = parts[1] as MathSourceKind;
  const sourceId = parts.slice(2).join(":");
  if (!MATH_ENTITY_TYPES.includes(type)) return null;
  if (!MATH_SOURCE_KINDS.includes(sourceKind)) return null;
  if (!sourceId) return null;
  return { type, sourceKind, sourceId };
}
