"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import {
  searchExplorationCatalog,
  type ExplorationCatalogItem,
} from "@math-ai-lab/domain-exploration";

export function ExplorationSearch({ items }: { items: ExplorationCatalogItem[] }) {
  const [query, setQuery] = useState("");
  const hits = useMemo(() => searchExplorationCatalog(items, query), [items, query]);
  return (
    <section className="mt-8">
      <h2 className="text-lg font-semibold">检索过程记录</h2>
      <p className="mt-1 text-sm text-muted">字面匹配，无向量。命中仍是 Candidate，不是定理。</p>
      <form
        className="mt-3 flex flex-wrap gap-2"
        onSubmit={(event) => event.preventDefault()}
      >
        <label className="block min-w-[16rem] flex-1 text-sm">
          <span className="sr-only">检索</span>
          <input
            className="w-full border border-line bg-canvas px-2 py-1"
            placeholder="例如 not_sum_free、reasoning、overview"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
      </form>
      {query.trim() ? (
        <p className="mt-2 text-sm text-muted">
          {hits.length} 条命中 · status=candidate · embeddings=false
        </p>
      ) : (
        <p className="mt-2 text-sm text-muted">输入关键词后即时检索。不写 Canonical。</p>
      )}
      {hits.length > 0 ? (
        <ul className="mt-3 space-y-2 text-sm">
          {hits.slice(0, 20).map((hit) => (
            <li key={hit.id}>
              <Link href={`/explore/${encodeURIComponent(hit.id)}`} className="text-accent">
                {hit.title}
              </Link>
              <span className="ml-2 text-muted">
                {hit.kind} · {hit.status}
              </span>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
