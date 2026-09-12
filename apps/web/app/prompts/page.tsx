import Link from "next/link";
import { Breadcrumb } from "../../components/breadcrumb";
import { EmptyState } from "../../components/empty-state";
import { getRepository } from "../../src/lib/repo";

export default async function PromptsPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q = "" } = await searchParams;
  const all = getRepository().listPrompts();
  const query = q.trim().toLowerCase();
  const items = query
    ? all.filter((item) =>
        `${item.title} ${item.category} ${item.body}`.toLowerCase().includes(query),
      )
    : all;
  const categories = [...new Set(all.map((item) => item.category))];
  return (
    <article>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "提示词" }]} />
      <h1 className="text-2xl font-semibold">提示词</h1>
      <p className="mt-2 text-sm text-muted">
        映射 <code>10_提示词/</code>。只读；可复制，不改文件。
      </p>
      <form action="/prompts" className="mt-4">
        <input
          name="q"
          defaultValue={q}
          placeholder="搜索提示词"
          className="w-full max-w-prose border border-line bg-canvas px-3 py-2"
        />
      </form>
      <p className="mt-3 text-sm text-muted">分类：{categories.join(" · ") || "无"}</p>
      {items.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="没有匹配的提示词" />
        </div>
      ) : (
        <ul className="mt-6 space-y-2 text-sm">
          {items.map((item) => (
            <li key={item.id}>
              <Link href={`/prompts/${encodeURIComponent(item.id)}`} className="text-accent">
                {item.title}
              </Link>
              <span className="ml-2 text-muted">{item.category}</span>
            </li>
          ))}
        </ul>
      )}
    </article>
  );
}
