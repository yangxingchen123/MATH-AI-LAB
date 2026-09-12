import Link from "next/link";
import { getSearchProvider, type SearchType } from "@math-ai-lab/content";
import { Breadcrumb } from "../../components/breadcrumb";
import { getRepository } from "../../src/lib/repo";

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; type?: string; status?: string; domain?: string }>;
}) {
  const { q = "", type, status, domain } = await searchParams;
  const hits = getSearchProvider(getRepository()).search(q, {
    type: type as SearchType | undefined,
    status: status || undefined,
    domain: domain || undefined,
  });
  return (
    <div>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "搜索" }]} />
      <h1 className="text-2xl font-semibold">搜索</h1>
      <form action="/search" className="mt-4 grid gap-2 sm:grid-cols-4">
        <input
          name="q"
          defaultValue={q}
          placeholder="知识、题目、方法、研究"
          className="border border-line bg-canvas px-3 py-2 sm:col-span-2"
        />
        <select name="type" defaultValue={type ?? ""} className="border border-line bg-canvas px-2 py-2">
          <option value="">全部类型</option>
          <option value="knowledge">知识</option>
          <option value="problem">题目</option>
          <option value="method">方法</option>
          <option value="research_project">研究</option>
          <option value="reference">参考</option>
          <option value="prompt">提示词</option>
          <option value="lean">Lean</option>
        </select>
        <select name="status" defaultValue={status ?? ""} className="border border-line bg-canvas px-2 py-2">
          <option value="">全部 status</option>
          <option value="draft">draft</option>
          <option value="reviewed">reviewed</option>
          <option value="archived">archived</option>
        </select>
        <button type="submit" className="border border-line px-3 py-2 sm:col-span-4 sm:w-fit">
          搜索
        </button>
      </form>
      <ul className="mt-6 space-y-3">
        {hits.map((hit) => (
          <li key={`${hit.type}-${hit.id}`} className="border-b border-line pb-3">
            <p className="text-xs text-muted">
              {hit.type} · {hit.sourcePath}
            </p>
            <Link href={hit.href} className="text-accent">
              {hit.id} {hit.title}
            </Link>
            <p className="text-sm text-muted">{hit.snippet}</p>
          </li>
        ))}
      </ul>
      {q && hits.length === 0 ? (
        <p className="mt-6 text-muted">没有匹配。</p>
      ) : null}
      {domain ? <p className="mt-3 text-xs text-muted">domain={domain}</p> : null}
    </div>
  );
}
