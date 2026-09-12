import type { Candidate } from "@math-ai-lab/domain-math";

/** Abstraction only. Do not implement AI. Output is Candidate only. */

export interface TitledItem {
  id: string;
  title: string;
}

export interface MathematicalSimilarityEngine {
  findAnalogies(entityId: string): Candidate[];
  findGeneralizations(entityId: string): Candidate[];
  findRelatedStructures(entityId: string): Candidate[];
  findPotentialConnections(entityId: string): Candidate[];
}

export class NullSimilarityEngine implements MathematicalSimilarityEngine {
  findAnalogies(_entityId: string): Candidate[] {
    return [];
  }
  findGeneralizations(_entityId: string): Candidate[] {
    return [];
  }
  findRelatedStructures(_entityId: string): Candidate[] {
    return [];
  }
  findPotentialConnections(_entityId: string): Candidate[] {
    return [];
  }
}

function tokens(text: string): Set<string> {
  return new Set(
    text
      .toLowerCase()
      .split(/[^\p{L}\p{N}]+/u)
      .filter((part) => part.length >= 2),
  );
}

function overlap(left: Set<string>, right: Set<string>): number {
  let score = 0;
  for (const token of left) {
    if (right.has(token)) score += 1;
  }
  return score;
}

function asCandidate(item: TitledItem, note: string): Candidate {
  return {
    id: `candidate:ai_mock:lexical:${item.id}`,
    title: item.title,
    proposedType: "conjecture",
    status: "idea",
    origin: "ai_mock",
    notes: note,
  };
}

/** Title-token overlap. Not embeddings, not mathematical analogy. */
export class LexicalSimilarityEngine implements MathematicalSimilarityEngine {
  constructor(private readonly items: TitledItem[]) {}

  private related(entityId: string, note: string): Candidate[] {
    const seed = this.items.find((row) => row.id === entityId);
    if (!seed) return [];
    const seedTokens = tokens(seed.title);
    return this.items
      .filter((row) => row.id !== entityId)
      .map((row) => ({ row, score: overlap(seedTokens, tokens(row.title)) }))
      .filter((item) => item.score > 0)
      .sort((a, b) => b.score - a.score || a.row.id.localeCompare(b.row.id))
      .map((item) => asCandidate(item.row, `${note}; overlap=${item.score}`));
  }

  findAnalogies(entityId: string): Candidate[] {
    return this.related(entityId, "Lexical analogy candidate only.");
  }
  findGeneralizations(entityId: string): Candidate[] {
    return this.related(entityId, "Lexical generalization candidate only.");
  }
  findRelatedStructures(entityId: string): Candidate[] {
    return this.related(entityId, "Lexical related-structure candidate only.");
  }
  findPotentialConnections(entityId: string): Candidate[] {
    return this.related(entityId, "Lexical connection candidate only.");
  }
}
