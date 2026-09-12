import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { basename, dirname, join } from "node:path";
import type { ReferenceKind, ReferenceRecord } from "@math-ai-lab/domain";
import { toPosix } from "./scan.ts";

const ROOT = "03_参考资料";
const SKIP_DIRS = new Set(["_模板", "derived"]);

function kindFromPath(sourcePath: string): ReferenceKind {
  if (sourcePath.includes("/教材/")) return "book";
  if (sourcePath.includes("/论文/")) return "paper";
  if (sourcePath.includes("/竞赛/")) return "contest";
  if (sourcePath.includes("/讲义/")) return "note";
  if (sourcePath.includes("/网站/") || sourcePath.includes("/websites/")) {
    return "website";
  }
  if (sourcePath.includes("/数据/") || sourcePath.includes("/datasets/")) {
    return "dataset";
  }
  return "note";
}

function parseIdentity(text: string): Record<string, string> {
  const fields: Record<string, string> = {};
  for (const line of text.split(/\r?\n/)) {
    const match = line.match(/^-\s*([a-zA-Z_]+):\s*(.*)$/);
    if (!match) continue;
    fields[match[1]] = match[2].trim();
  }
  const heading = text.match(/^#\s+(.+)$/m);
  if (heading?.[1] && !fields.title) {
    fields.title = heading[1].trim();
  }
  return fields;
}

function present(value: string | undefined): string | undefined {
  if (!value) return undefined;
  if (value === "UNKNOWN" || value === "LOCAL") return undefined;
  return value;
}

function authorsOf(raw: string | undefined): string[] | undefined {
  if (!raw) return undefined;
  const items = raw
    .split(/[,;，]/)
    .map((item) => item.trim())
    .filter(Boolean);
  return items.length ? items : undefined;
}

function walkIdentity(absDir: string, out: string[]): void {
  let entries;
  try {
    entries = readdirSync(absDir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    if (SKIP_DIRS.has(entry.name) || entry.name.startsWith(".")) {
      continue;
    }
    const full = join(absDir, entry.name);
    if (entry.isDirectory()) {
      walkIdentity(full, out);
    } else if (entry.isFile() && entry.name === "identity.md") {
      out.push(full);
    }
  }
}

export function listReferences(repoRoot: string): ReferenceRecord[] {
  const base = join(repoRoot, ROOT);
  if (!existsSync(base)) {
    return [];
  }
  const files: string[] = [];
  walkIdentity(base, files);
  const rows: ReferenceRecord[] = [];
  for (const abs of files) {
    const sourcePath = toPosix(repoRoot, abs);
    const fields = parseIdentity(readFileSync(abs, "utf8"));
    const dir = dirname(abs);
    const slug = fields.slug || basename(dir);
    const pdfCandidate = join(dir, "source.pdf");
    const pdfPath = existsSync(pdfCandidate)
      ? toPosix(repoRoot, pdfCandidate)
      : undefined;
    const notes = fields.notes || undefined;
    const relatedResearch: string[] = [];
    if (notes?.includes("07_项目/")) {
      const hit = notes.match(/07_项目\/([^\s。]+)/);
      if (hit?.[1]) {
        relatedResearch.push(hit[1]);
      }
    }
    rows.push({
      id: slug,
      title: fields.title || slug,
      kind: kindFromPath(sourcePath),
      sourcePath,
      authors: authorsOf(present(fields.authors)),
      year: present(fields.year),
      venue: present(fields.venue),
      domain: present(fields.domain),
      doi: present(fields.doi),
      arxiv: present(fields.arxiv),
      url: present(fields.url),
      bibtex: present(fields.bibtex),
      pdfPath,
      relatedKnowledge: [],
      relatedResearch,
      notes,
    });
  }
  return rows.sort((a, b) => a.id.localeCompare(b.id, "zh"));
}

export function getReference(
  repoRoot: string,
  id: string,
): ReferenceRecord | null {
  if (!id || id.includes("..") || id.includes("/") || id.includes("\\")) {
    return null;
  }
  return listReferences(repoRoot).find((row) => row.id === id) ?? null;
}

export function referenceHasFile(absOrRel: string): boolean {
  try {
    return existsSync(absOrRel) && statSync(absOrRel).isFile();
  } catch {
    return false;
  }
}
