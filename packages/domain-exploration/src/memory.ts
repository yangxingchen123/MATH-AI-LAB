/**
 * Three memories future AI requires:
 * short-term — current ResearchSession
 * long-term — verified mathematics (IDs into Universe/Canonical, never copied bodies)
 * failure — rejected approaches
 */

export interface MathematicalMemory {
  shortTerm: { sessionId: string; notebookId?: string };
  longTerm: { verifiedEntityIds: string[] };
  failure: { recordIds: string[] };
}

export function createMemory(
  input: MathematicalMemory,
): { ok: true; memory: MathematicalMemory } | { ok: false; error: string } {
  if (!input.shortTerm?.sessionId?.trim()) {
    return { ok: false, error: "Short-term memory requires a session id." };
  }
  return { ok: true, memory: input };
}
