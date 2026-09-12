import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { parse as parseYaml } from "yaml";
import type { LabRecord } from "@math-ai-lab/domain";

const ROOT = "tools/research_lab";

const SLOTS: { dir: string; kind: LabRecord["kind"] }[] = [
  { dir: "problems", kind: "problem" },
  { dir: "conjectures", kind: "conjecture" },
  { dir: "tasks", kind: "task" },
  { dir: "literature", kind: "literature" },
  { dir: "experts", kind: "expert" },
];

function asString(value: unknown): string | undefined {
  return typeof value === "string" && value.trim() ? value.trim() : undefined;
}

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map(asString).filter((item): item is string => Boolean(item));
}

function loadYaml(abs: string): Record<string, unknown> | null {
  try {
    const data = parseYaml(readFileSync(abs, "utf8"));
    return data && typeof data === "object" && !Array.isArray(data)
      ? (data as Record<string, unknown>)
      : null;
  } catch {
    return null;
  }
}

export function listLabRecords(repoRoot: string): LabRecord[] {
  const rows: LabRecord[] = [];
  for (const slot of SLOTS) {
    const dir = join(repoRoot, ROOT, slot.dir);
    if (!existsSync(dir)) continue;
    let entries;
    try {
      entries = readdirSync(dir);
    } catch {
      continue;
    }
    for (const name of entries) {
      if (!name.endsWith(".yaml") && !name.endsWith(".yml")) continue;
      const abs = join(dir, name);
      const data = loadYaml(abs);
      if (!data) continue;
      const id = asString(data.id) || name.replace(/\.ya?ml$/, "");
      rows.push({
        id,
        title: asString(data.title) || id,
        kind: slot.kind,
        sourcePath: `${ROOT}/${slot.dir}/${name}`,
        stage: asString(data.stage),
        novelty: asString(data.novelty_claim) || asString(data.novelty),
        leanDecls: asStringList(data.lean_decls),
        candidate: true,
        notes: asString(data.notes),
      });
    }
  }
  return rows.sort((a, b) => a.id.localeCompare(b.id));
}
