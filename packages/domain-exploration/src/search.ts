/** Semantic mathematical retrieval interface. No embeddings yet. Hits are candidates, not truth. */

export const SEARCH_HIT_KINDS = ["concept", "proof", "strategy", "failure", "analogy"] as const;

export type SearchHitKind = (typeof SEARCH_HIT_KINDS)[number];

export interface SearchHit {
  id: string;
  kind: SearchHitKind;
  title: string;
  status: "candidate";
}

export interface MathematicalSearchProvider {
  searchConcept(query: string): SearchHit[];
  searchProof(query: string): SearchHit[];
  searchStrategy(query: string): SearchHit[];
  searchFailure(query: string): SearchHit[];
  searchAnalogy(query: string): SearchHit[];
}

export class NullSearchProvider implements MathematicalSearchProvider {
  searchConcept(_query: string): SearchHit[] {
    return [];
  }
  searchProof(_query: string): SearchHit[] {
    return [];
  }
  searchStrategy(_query: string): SearchHit[] {
    return [];
  }
  searchFailure(_query: string): SearchHit[] {
    return [];
  }
  searchAnalogy(_query: string): SearchHit[] {
    return [];
  }
}

export type SearchCatalog = Partial<Record<SearchHitKind, { id: string; title: string }[]>>;

/** Substring match over a provided catalog. No embeddings. Hits stay candidates. */
export class LexicalSearchProvider implements MathematicalSearchProvider {
  constructor(private readonly catalog: SearchCatalog) {}

  private hit(kind: SearchHitKind, query: string): SearchHit[] {
    const needle = query.trim().toLowerCase();
    if (!needle) return [];
    return (this.catalog[kind] ?? [])
      .filter(
        (row) => row.title.toLowerCase().includes(needle) || row.id.toLowerCase().includes(needle),
      )
      .map((row) => ({ id: row.id, kind, title: row.title, status: "candidate" as const }));
  }

  searchConcept(query: string): SearchHit[] {
    return this.hit("concept", query);
  }
  searchProof(query: string): SearchHit[] {
    return this.hit("proof", query);
  }
  searchStrategy(query: string): SearchHit[] {
    return this.hit("strategy", query);
  }
  searchFailure(query: string): SearchHit[] {
    return this.hit("failure", query);
  }
  searchAnalogy(query: string): SearchHit[] {
    return this.hit("analogy", query);
  }
}
