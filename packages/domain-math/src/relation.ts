import type { RelationOrigin } from "@math-ai-lab/domain";

export const MATH_RELATION_TYPES = [
  "depends_on",
  "uses",
  "generalizes",
  "special_case_of",
  "equivalent_to",
  "contradicts",
  "proves",
  "disproves",
  "verified_by",
  "derived_from",
  "motivated_by",
] as const;

export type MathRelationType = (typeof MATH_RELATION_TYPES)[number];

export const RELATION_EVIDENCE_KINDS = [
  "explicit_field",
  "derived_reverse",
  "lean_manifest",
  "attempt_ledger",
  "lab_record",
  "none",
] as const;

export type RelationEvidenceKind = (typeof RELATION_EVIDENCE_KINDS)[number];

export interface RelationEvidence {
  kind: RelationEvidenceKind;
  sourcePath?: string;
  note?: string;
}

export interface MathematicalRelation {
  id: string;
  type: MathRelationType;
  source: string;
  target: string;
  origin: RelationOrigin;
  evidence: RelationEvidence;
}

export function relationId(type: MathRelationType, source: string, target: string): string {
  return `${type}:${source}->${target}`;
}

export function validateRelation(
  rel: MathematicalRelation,
  knownIds?: ReadonlySet<string>,
): { ok: true } | { ok: false; error: string } {
  if (!MATH_RELATION_TYPES.includes(rel.type)) {
    return { ok: false, error: "Unknown relation type." };
  }
  if (!rel.source?.trim() || !rel.target?.trim()) {
    return { ok: false, error: "Relation requires source and target." };
  }
  if (rel.source === rel.target) {
    return { ok: false, error: "Relation source and target must differ." };
  }
  if (!rel.evidence || !RELATION_EVIDENCE_KINDS.includes(rel.evidence.kind)) {
    return { ok: false, error: "Relation requires evidence." };
  }
  if (knownIds && (!knownIds.has(rel.source) || !knownIds.has(rel.target))) {
    return { ok: false, error: "Relation endpoints must be known entities." };
  }
  return { ok: true };
}
