import Link from "next/link";
import { notFound } from "next/navigation";
import { Breadcrumb } from "../../../components/breadcrumb";
import { explorationItem } from "../../../src/lib/exploration";

export default async function ExploreItemPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: raw } = await params;
  let id = raw;
  try {
    id = decodeURIComponent(raw);
  } catch {
    notFound();
  }
  const item = explorationItem(id);
  if (!item) {
    notFound();
  }
  return (
    <article>
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/explore", label: "探索" },
          { label: item.group },
        ]}
      />
      <h1 className="text-2xl font-semibold">{item.title}</h1>
      <p className="mt-2 font-mono text-sm text-muted">{item.id}</p>
      <p className="mt-2 text-sm text-muted">
        {item.group}
        {item.state ? ` · lifecycle=${item.state}` : ""}
        {item.pipeline ? ` · pipeline=${item.pipeline}` : ""}
      </p>
      <p className="mt-3 text-sm">{item.detail}</p>
      <pre className="mt-6 overflow-x-auto whitespace-pre-wrap border border-line bg-[var(--sidebar)] p-3 text-sm">
        {item.body}
      </pre>
      <p className="mt-6 text-sm text-muted">只读过程记录。不是 Canonical，不能写成 Theorem。</p>
      <p className="mt-3 text-sm">
        <Link href="/explore" className="text-accent">
          返回探索总览
        </Link>
      </p>
    </article>
  );
}
