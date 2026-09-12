"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { listRecentSearches, recordSearch } from "../prefs/local-prefs";

interface SearchHit {
  type: string;
  id: string;
  title: string;
  href: string;
  snippet: string;
  sourcePath: string;
}

const COMMANDS = [
  { id: "home", label: "打开工作台", href: "/" },
  { id: "knowledge", label: "打开知识", href: "/knowledge" },
  { id: "problems", label: "打开题目", href: "/problems" },
  { id: "methods", label: "打开方法", href: "/methods" },
  { id: "research", label: "打开研究", href: "/research" },
  { id: "inbox", label: "打开收件箱", href: "/inbox" },
  { id: "diagnostics", label: "打开诊断", href: "/advanced/diagnostics" },
  { id: "create-problem", label: "创建题目", href: "/problems/new" },
  { id: "create-knowledge", label: "创建知识", href: "/knowledge/new" },
  { id: "create-method", label: "创建方法", href: "/methods/new" },
  { id: "theme", label: "切换主题", href: "__theme__" },
  { id: "references", label: "打开参考", href: "/references" },
  { id: "outputs", label: "打开成果", href: "/outputs" },
  { id: "memory", label: "打开记忆", href: "/memory" },
  { id: "prompts", label: "打开提示词", href: "/prompts" },
  { id: "lean", label: "打开 Lean", href: "/lean" },
  { id: "lab", label: "打开 Lab", href: "/lab" },
  { id: "universe", label: "打开宇宙", href: "/universe" },
  { id: "repository", label: "打开仓库", href: "/repository" },
  { id: "settings", label: "打开设置", href: "/settings" },
];

export function CommandPalette() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<SearchHit[]>([]);
  const [active, setActive] = useState(0);
  const [recents, setRecents] = useState<string[]>([]);

  const rows = useMemo(() => {
    if (query.trim()) {
      return hits.map((hit) => ({
        id: `${hit.type}-${hit.id}`,
        label: `${hit.id} ${hit.title}`,
        detail: hit.snippet,
        href: hit.href,
      }));
    }
    const recentRows = recents.map((item) => ({
      id: `recent-${item}`,
      label: item,
      detail: "最近搜索",
      href: `/search?q=${encodeURIComponent(item)}`,
    }));
    return [
      ...recentRows,
      ...COMMANDS.map((command) => ({
        id: command.id,
        label: command.label,
        detail: "",
        href: command.href,
      })),
    ];
  }, [hits, query, recents]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((value) => !value);
      }
      if (event.key === "Escape") {
        setOpen(false);
      }
    };
    const onClick = (event: Event) => {
      const target = event.target as HTMLElement | null;
      if (target?.closest("[data-search-trigger]")) {
        setOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("click", onClick);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("click", onClick);
    };
  }, []);

  useEffect(() => {
    if (!open) return;
    setRecents(listRecentSearches());
    setActive(0);
    const q = query.trim();
    if (!q) {
      setHits([]);
      return;
    }
    const controller = new AbortController();
    fetch(`/api/search?q=${encodeURIComponent(q)}`, { signal: controller.signal })
      .then((response) => response.json())
      .then((data: { hits?: SearchHit[] }) => setHits(data.hits ?? []))
      .catch(() => undefined);
    return () => controller.abort();
  }, [open, query]);

  const go = (href: string, maybeQuery?: string) => {
    if (href === "__theme__") {
      window.dispatchEvent(new Event("math-ai-lab-toggle-theme"));
      setOpen(false);
      return;
    }
    if (maybeQuery) {
      recordSearch(maybeQuery);
    }
    setOpen(false);
    setQuery("");
    router.push(href);
  };

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50">
      <button
        type="button"
        className="absolute inset-0 bg-black/40"
        aria-label="关闭搜索"
        onClick={() => setOpen(false)}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label="搜索"
        className="relative mx-auto mt-[12vh] w-[min(40rem,calc(100%-2rem))] border border-line bg-[var(--panel)] p-3 shadow-lg"
      >
        <input
          autoFocus
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setActive(0);
          }}
          onKeyDown={(event) => {
            if (event.key === "ArrowDown") {
              event.preventDefault();
              setActive((value) => Math.min(rows.length - 1, value + 1));
            }
            if (event.key === "ArrowUp") {
              event.preventDefault();
              setActive((value) => Math.max(0, value - 1));
            }
            if (event.key === "Enter") {
              event.preventDefault();
              const row = rows[active];
              if (row) {
                go(row.href, query.trim() || undefined);
              }
            }
          }}
          placeholder="搜索知识、题目、方法、研究"
          className="w-full border border-line bg-canvas px-3 py-2 text-ink"
          aria-autocomplete="list"
          aria-controls="search-results"
        />
        <ul id="search-results" role="listbox" className="mt-3 max-h-[50vh] overflow-y-auto text-sm">
          {rows.map((row, index) => (
            <li key={row.id} role="option" aria-selected={index === active}>
              <button
                type="button"
                className={`block w-full px-2 py-2 text-left ${
                  index === active ? "bg-[var(--sidebar)]" : "hover:bg-[var(--sidebar)]"
                }`}
                onMouseEnter={() => setActive(index)}
                onClick={() => go(row.href, query.trim() || undefined)}
              >
                <span className="font-medium">{row.label}</span>
                {row.detail ? (
                  <span className="mt-1 block text-muted">{row.detail}</span>
                ) : null}
              </button>
            </li>
          ))}
        </ul>
        {query.trim() && hits.length === 0 ? (
          <p className="px-2 py-3 text-sm text-muted">没有匹配。检索失败合法。</p>
        ) : null}
      </div>
    </div>
  );
}
