import type { ContentRepository } from "./repository.ts";

export type SearchType =
  | "knowledge"
  | "problem"
  | "method"
  | "research_project"
  | "reference"
  | "output"
  | "memory"
  | "prompt"
  | "lean"
  | "lab";

export interface SearchHit {
  type: SearchType;
  id: string;
  title: string;
  href: string;
  snippet: string;
  sourcePath: string;
  score: number;
}

export interface SearchFilters {
  type?: SearchType;
  status?: string;
  domain?: string;
}

export interface SearchProvider {
  search(query: string, filters?: SearchFilters): SearchHit[];
}

interface SearchRecord {
  type: SearchHit["type"];
  id: string;
  title: string;
  href: string;
  sourcePath: string;
  haystack: string;
  aliases?: string;
  status?: string;
  domain?: string;
}

export class LocalSearchProvider implements SearchProvider {
  constructor(private readonly records: SearchRecord[]) {}

  search(query: string, filters: SearchFilters = {}): SearchHit[] {
    const q = query.trim();
    if (!q) {
      return [];
    }
    const lower = q.toLowerCase();
    const hits: SearchHit[] = [];
    for (const record of this.records) {
      if (filters.type && record.type !== filters.type) continue;
      if (filters.status && record.status !== filters.status) continue;
      if (filters.domain && record.domain !== filters.domain) continue;
      const score = scoreRecord(record, q, lower);
      if (score <= 0) continue;
      const hay = record.haystack.toLowerCase();
      const index = hay.indexOf(lower);
      hits.push({
        type: record.type,
        id: record.id,
        title: record.title,
        href: record.href,
        sourcePath: record.sourcePath,
        score,
        snippet: snippet(record.haystack, index >= 0 ? index : 0, lower.length),
      });
    }
    return hits.sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
  }
}

const TYPE_BONUS: Record<SearchType, number> = {
  knowledge: 80,
  problem: 80,
  method: 70,
  research_project: 60,
  lean: 30,
  reference: 25,
  prompt: 20,
  lab: 15,
  memory: 10,
  output: 0,
};

function scoreRecord(record: SearchRecord, raw: string, lower: string): number {
  const bonus = TYPE_BONUS[record.type] ?? 0;
  if (record.id.toLowerCase() === lower) {
    return 1000 + bonus;
  }
  if (record.id.toLowerCase().startsWith(lower)) {
    return 700 + bonus;
  }
  const title = record.title.toLowerCase();
  const aliases = (record.aliases ?? "").toLowerCase();
  if (title === lower || aliases === lower) {
    return 500 + bonus;
  }
  if (title.includes(lower) || aliases.includes(lower)) {
    return 220 + bonus;
  }
  const hay = record.haystack.toLowerCase();
  const index = hay.indexOf(lower);
  if (index < 0) {
    return 0;
  }
  return Math.max(10, 40 - Math.floor(index / 80)) + Math.floor(bonus / 4);
}

export function buildSearchIndex(repo: ContentRepository): LocalSearchProvider {
  const records: SearchRecord[] = [];
  for (const item of repo.listKnowledge()) {
    records.push({
      type: "knowledge",
      id: item.id,
      title: item.title,
      href: `/knowledge/${item.id}`,
      sourcePath: item.sourcePath,
      status: item.objectStatus,
      domain: item.domain,
      aliases: (item.aliases ?? []).join(" "),
      haystack: `${item.id} ${item.title} ${(item.aliases ?? []).join(" ")} ${item.domain ?? ""} ${item.body}`,
    });
  }
  for (const item of repo.listProblems()) {
    records.push({
      type: "problem",
      id: item.id,
      title: item.title,
      href: `/problems/${item.id}`,
      sourcePath: item.sourcePath,
      status: item.objectStatus,
      haystack: `${item.id} ${item.title} ${item.workflowDir ?? ""} ${item.body}`,
    });
  }
  for (const item of repo.listMethods()) {
    records.push({
      type: "method",
      id: item.id,
      title: item.title,
      href: `/methods/${item.id}`,
      sourcePath: item.sourcePath,
      status: item.objectStatus,
      haystack: `${item.id} ${item.title} ${item.body}`,
    });
  }
  for (const item of repo.listResearch()) {
    records.push({
      type: "research_project",
      id: item.slug,
      title: item.title,
      href: `/research/${encodeURIComponent(item.slug)}`,
      sourcePath: item.sourcePath,
      haystack: `${item.slug} ${item.title} ${item.kind} ${item.sections.map((section) => section.body).join("\n")}`,
    });
  }
  for (const item of repo.listReferences()) {
    records.push({
      type: "reference",
      id: item.id,
      title: item.title,
      href: `/references/${encodeURIComponent(item.id)}`,
      sourcePath: item.sourcePath,
      domain: item.domain,
      haystack: `${item.id} ${item.title} ${item.kind} ${item.notes ?? ""}`,
    });
  }
  for (const item of repo.listOutputs()) {
    records.push({
      type: "output",
      id: item.id,
      title: item.title,
      href: item.href,
      sourcePath: item.sourcePath,
      haystack: `${item.title} ${item.sourcePath}`,
    });
  }
  for (const item of repo.listMemory()) {
    records.push({
      type: "memory",
      id: item.id,
      title: item.title,
      href: `/memory/${encodeURIComponent(item.id)}`,
      sourcePath: item.sourcePath,
      haystack: `${item.title} ${item.body}`,
    });
  }
  for (const item of repo.listPrompts()) {
    records.push({
      type: "prompt",
      id: item.id,
      title: item.title,
      href: `/prompts/${encodeURIComponent(item.id)}`,
      sourcePath: item.sourcePath,
      haystack: `${item.title} ${item.category} ${item.body}`,
    });
  }
  for (const item of repo.listLean()) {
    records.push({
      type: "lean",
      id: item.id,
      title: item.title,
      href: `/lean/${encodeURIComponent(item.id)}`,
      sourcePath: item.leanFile ?? item.evidencePath ?? "",
      haystack: `${item.id} ${item.title} ${item.leanDecl ?? ""}`,
    });
  }
  for (const item of repo.listLab()) {
    records.push({
      type: "lab",
      id: item.id,
      title: item.title,
      href: `/lab#${encodeURIComponent(item.id)}`,
      sourcePath: item.sourcePath,
      haystack: `${item.id} ${item.title} ${item.notes ?? ""}`,
    });
  }
  return new LocalSearchProvider(records);
}

let cached:
  | {
      key: string;
      provider: LocalSearchProvider;
    }
  | null = null;

export function getSearchProvider(repo: ContentRepository): LocalSearchProvider {
  const key = [
    repo.repoRoot,
    repo.listKnowledge().length,
    repo.listProblems().length,
    repo.listMethods().length,
    repo.listResearch().length,
    repo.listReferences().length,
    repo.listPrompts().length,
    repo.listLean().length,
    repo.skips().length,
  ].join(":");
  if (cached && cached.key === key) {
    return cached.provider;
  }
  const provider = buildSearchIndex(repo);
  cached = { key, provider };
  return provider;
}

function snippet(text: string, index: number, length: number): string {
  const start = Math.max(0, index - 24);
  const end = Math.min(text.length, index + length + 48);
  const slice = text.slice(start, end).replace(/\s+/g, " ").trim();
  return `${start > 0 ? "…" : ""}${slice}${end < text.length ? "…" : ""}`;
}
