/**
 * Four-layer stack. Do not merge.
 *
 * Canonical  — Frozen Source (K/P/A/M, Lean, Dossier). Existing mathematics.
 * Universe   — packages/domain-math. Mathematical entities / relations / evidence.
 * Frontier   — packages/domain-frontier. Unknown regions / directions.
 * Exploration — this package. Research processes. Not a document store.
 */

export const CANONICAL_LAYER = "canonical" as const;
export const UNIVERSE_LAYER = "universe" as const;
export const FRONTIER_LAYER = "frontier" as const;
export const EXPLORATION_LAYER = "exploration" as const;

export const MATHEMATICAL_LAYERS = [
  CANONICAL_LAYER,
  UNIVERSE_LAYER,
  FRONTIER_LAYER,
  EXPLORATION_LAYER,
] as const;

export type MathematicalLayer = (typeof MATHEMATICAL_LAYERS)[number];
