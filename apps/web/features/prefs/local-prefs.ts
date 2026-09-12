export type PrefKind = "knowledge" | "problem" | "method" | "research";

export interface PrefItem {
  kind: PrefKind;
  id: string;
  title: string;
  href: string;
  at: number;
}

const RECENT_KEY = "math-ai-lab-recent";
const PINS_KEY = "math-ai-lab-pins";
const SEARCH_KEY = "math-ai-lab-recent-searches";
const LIMIT = 12;

function readList(key: string): PrefItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as PrefItem[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeList(key: string, items: PrefItem[]): void {
  window.localStorage.setItem(key, JSON.stringify(items.slice(0, LIMIT)));
}

export function listRecent(): PrefItem[] {
  return readList(RECENT_KEY);
}

export function listPins(): PrefItem[] {
  return readList(PINS_KEY);
}

export function recordView(item: Omit<PrefItem, "at">): void {
  const next = [
    { ...item, at: Date.now() },
    ...listRecent().filter((row) => !(row.kind === item.kind && row.id === item.id)),
  ];
  writeList(RECENT_KEY, next);
}

export function clearRecent(): void {
  window.localStorage.removeItem(RECENT_KEY);
}

export function isPinned(kind: PrefKind, id: string): boolean {
  return listPins().some((row) => row.kind === kind && row.id === id);
}

export function togglePin(item: Omit<PrefItem, "at">): boolean {
  const current = listPins();
  const exists = current.some((row) => row.kind === item.kind && row.id === item.id);
  const next = exists
    ? current.filter((row) => !(row.kind === item.kind && row.id === item.id))
    : [{ ...item, at: Date.now() }, ...current];
  writeList(PINS_KEY, next);
  return !exists;
}

export function clearPins(): void {
  window.localStorage.removeItem(PINS_KEY);
}

export function listRecentSearches(): string[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(SEARCH_KEY);
    const parsed = raw ? (JSON.parse(raw) as string[]) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function recordSearch(query: string): void {
  const q = query.trim();
  if (!q) return;
  const next = [q, ...listRecentSearches().filter((item) => item !== q)].slice(0, 8);
  window.localStorage.setItem(SEARCH_KEY, JSON.stringify(next));
}

export function clearRecentSearches(): void {
  window.localStorage.removeItem(SEARCH_KEY);
}
