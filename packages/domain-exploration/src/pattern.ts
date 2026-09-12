/** Recurring structure. Pattern does not equal theorem. */

export const PATTERN_KINDS = [
  "symmetry",
  "invariant",
  "repeated_relationship",
  "hidden_correspondence",
  "other",
] as const;

export type PatternKind = (typeof PATTERN_KINDS)[number];

export const PATTERN_CONFIDENCE = ["none", "heuristic", "human_claimed"] as const;

export type PatternConfidence = (typeof PATTERN_CONFIDENCE)[number];

export interface MathematicalPattern {
  id: string;
  pattern: string;
  kind: PatternKind;
  instances: string[];
  supportingEvidence: string[];
  confidence: PatternConfidence;
  relatedTheory: string[];
}

export function createPattern(
  input: MathematicalPattern,
): { ok: true; pattern: MathematicalPattern } | { ok: false; error: string } {
  if (!input.id?.trim() || !input.pattern?.trim()) {
    return { ok: false, error: "Pattern requires id and pattern description." };
  }
  if (!PATTERN_KINDS.includes(input.kind)) {
    return { ok: false, error: "Unknown pattern kind." };
  }
  if (!PATTERN_CONFIDENCE.includes(input.confidence)) {
    return { ok: false, error: "Pattern confidence cannot be mathematical truth." };
  }
  return { ok: true, pattern: input };
}

export function patternIsTheorem(_pattern: MathematicalPattern): false {
  return false;
}

/** Recurring groups with at least two instances. Never a theorem. */
export function projectRecurringPatterns(
  groups: Array<{
    id: string;
    pattern: string;
    kind: PatternKind;
    instances: string[];
    supportingEvidence?: string[];
    relatedTheory?: string[];
  }>,
): MathematicalPattern[] {
  const patterns: MathematicalPattern[] = [];
  for (const group of groups) {
    if (group.instances.length < 2) continue;
    const made = createPattern({
      id: group.id,
      pattern: group.pattern,
      kind: group.kind,
      instances: group.instances,
      supportingEvidence: group.supportingEvidence ?? [],
      confidence: "heuristic",
      relatedTheory: group.relatedTheory ?? [],
    });
    if (made.ok) patterns.push(made.pattern);
  }
  return patterns;
}
