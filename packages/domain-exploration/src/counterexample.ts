/** A counterexample is how mathematics progresses. Not a canonical theorem. */

export interface CounterexampleRecord {
  id: string;
  claim: string;
  counterexample: string;
  construction: string;
  whyFailure: string;
  lesson: string;
  futureDirection: string;
}

export function createCounterexample(
  input: CounterexampleRecord,
): { ok: true; record: CounterexampleRecord } | { ok: false; error: string } {
  if (
    !input.id?.trim() ||
    !input.claim?.trim() ||
    !input.counterexample?.trim() ||
    !input.construction?.trim() ||
    !input.whyFailure?.trim() ||
    !input.lesson?.trim()
  ) {
    return { ok: false, error: "CounterexampleRecord requires claim, construction, whyFailure, and lesson." };
  }
  return { ok: true, record: input };
}
