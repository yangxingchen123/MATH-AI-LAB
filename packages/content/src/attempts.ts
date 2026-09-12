import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { parseDocument } from "yaml";
import { isUnsafeId } from "@math-ai-lab/domain";

export interface AttemptRecord {
  id: string;
  problem: string;
  part?: string;
  outcome: string;
  assistance: string;
  attemptedAt?: string;
  narrative?: string;
}

export function readAttemptLedger(
  repoRoot: string,
  problemId: string,
): AttemptRecord[] {
  if (isUnsafeId(problemId)) {
    return [];
  }
  const path = join(repoRoot, "11_学习证据", "尝试记录", `${problemId}.md`);
  if (!existsSync(path)) {
    return [];
  }
  const text = readFileSync(path, "utf8");
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) {
    return [];
  }
  const doc = parseDocument(match[1]);
  const data = doc.toJSON() as { attempts?: unknown } | null;
  if (!data || !Array.isArray(data.attempts)) {
    return [];
  }
  const narratives = parseAttemptNarratives(text);
  const rows: AttemptRecord[] = [];
  for (const raw of data.attempts) {
    if (!raw || typeof raw !== "object") continue;
    const row = raw as Record<string, unknown>;
    if (row.type !== "attempt") continue;
    if (typeof row.id !== "string" || typeof row.problem !== "string") continue;
    if (typeof row.outcome !== "string" || typeof row.assistance !== "string") {
      continue;
    }
    rows.push({
      id: row.id,
      problem: row.problem,
      part: typeof row.part === "string" ? row.part : undefined,
      outcome: row.outcome,
      assistance: row.assistance,
      attemptedAt:
        typeof row.attempted_at === "string" ? row.attempted_at : undefined,
      narrative: narratives.get(row.id),
    });
  }
  return rows;
}

function parseAttemptNarratives(text: string): Map<string, string> {
  const map = new Map<string, string>();
  const matches = [...text.matchAll(/^## (A\d{6})\s*$/gm)];
  for (let i = 0; i < matches.length; i += 1) {
    const id = matches[i][1];
    const start = matches[i].index ?? 0;
    const from = text.indexOf("\n", start) + 1;
    const end = matches[i + 1]?.index ?? text.length;
    const body = text.slice(from, end).trim();
    if (body) map.set(id, body);
  }
  return map;
}
