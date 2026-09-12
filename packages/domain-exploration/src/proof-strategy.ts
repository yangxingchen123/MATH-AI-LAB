/** Proof search strategy. Not a stored proof. */

export const NAMED_PROOF_STRATEGIES = [
  "induction",
  "contradiction",
  "compactness",
  "category_argument",
  "algebraic_construction",
] as const;

export type NamedProofStrategy = (typeof NAMED_PROOF_STRATEGIES)[number];

export interface ProofStrategy {
  id: string;
  strategy: string;
  applicableConditions: string[];
  successfulCases: string[];
  failedCases: string[];
  limitations: string[];
}

export function createProofStrategy(
  input: ProofStrategy,
): { ok: true; strategy: ProofStrategy } | { ok: false; error: string } {
  if (!input.id?.trim() || !input.strategy?.trim()) {
    return { ok: false, error: "ProofStrategy requires id and strategy." };
  }
  return { ok: true, strategy: input };
}

export function strategyIsProof(_strategy: ProofStrategy): false {
  return false;
}

const INDUCTION_RE = /\binduction\b/;
const ODDS_RE = /\bodds\b/;

/** Lexical scan of public theorem bodies. Not a stored proof. */
export function scanNamedProofStrategies(
  theorems: Array<{ id: string; body: string }>,
): ProofStrategy[] {
  const induction: string[] = [];
  const construction: string[] = [];
  for (const theorem of theorems) {
    if (!theorem.id?.trim() || !theorem.body) continue;
    if (INDUCTION_RE.test(theorem.body)) induction.push(theorem.id);
    if (ODDS_RE.test(theorem.body)) construction.push(theorem.id);
  }
  const rows: ProofStrategy[] = [];
  if (induction.length) {
    rows.push({
      id: "strategy:induction",
      strategy: "induction",
      applicableConditions: [
        "Applies when a Nat/List statement is proved by recursion on the same inductive type.",
      ],
      successfulCases: induction,
      failedCases: [],
      limitations: ["Lexical scan of `induction` in the public theorem body. Not a stored proof."],
    });
  }
  if (construction.length) {
    rows.push({
      id: "strategy:algebraic_construction",
      strategy: "algebraic_construction",
      applicableConditions: [
        "Applies when a named construction (here `odds`) is used inside the theorem body.",
      ],
      successfulCases: construction,
      failedCases: [],
      limitations: ["Mentions of `odds` are not a uniqueness proof. Not Canonical."],
    });
  }
  return rows;
}
