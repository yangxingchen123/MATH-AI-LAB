/** A failure is a reusable mathematical object. Prevents repeated dead ends. */

export interface FailureRecord {
  id: string;
  failedAttempt: string;
  reason: string;
  assumptionFailure?: string;
  methodFailure?: string;
  lesson: string;
  relatedFutureResearch: string[];
}

export interface FailureMemorySystem {
  records: FailureRecord[];
}

export function emptyFailureMemory(): FailureMemorySystem {
  return { records: [] };
}

export function rememberFailure(
  memory: FailureMemorySystem,
  record: FailureRecord,
): { ok: true; memory: FailureMemorySystem } | { ok: false; error: string } {
  if (!record.id?.trim() || !record.failedAttempt?.trim() || !record.reason?.trim() || !record.lesson?.trim()) {
    return { ok: false, error: "FailureRecord requires id, failedAttempt, reason, and lesson." };
  }
  if (memory.records.some((row) => row.id === record.id)) {
    return { ok: false, error: "FailureRecord id already exists." };
  }
  return { ok: true, memory: { records: [...memory.records, record] } };
}

export function lookupFailures(
  memory: FailureMemorySystem,
  query: { reason?: string; methodFailure?: string; assumptionFailure?: string },
): FailureRecord[] {
  const reason = query.reason?.trim().toLowerCase();
  const method = query.methodFailure?.trim().toLowerCase();
  const assumption = query.assumptionFailure?.trim().toLowerCase();
  return memory.records.filter((row) => {
    if (reason && !row.reason.toLowerCase().includes(reason)) return false;
    if (method && !(row.methodFailure ?? "").toLowerCase().includes(method)) return false;
    if (assumption && !(row.assumptionFailure ?? "").toLowerCase().includes(assumption)) return false;
    return Boolean(reason || method || assumption);
  });
}
