import { Breadcrumb } from "../../../components/breadcrumb";
import { LeanBadge } from "../../../components/lean-badge";
import { MarkdownView } from "../../../components/markdown-view";
import { RelationList } from "../../../components/relation-list";
import { StatusPair } from "../../../components/status-pair";
import { RecordView } from "../../../features/prefs/record-view";
import { rejectBadId, requireObject } from "../../../src/lib/require-content";
import { getRepository } from "../../../src/lib/repo";
import Link from "next/link";

export default async function KnowledgeDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  rejectBadId(id);
  const repo = getRepository();
  const item = requireObject(repo.getKnowledge(id));
  const relations = repo.knowledgeRelations(id);
  const knownIds = [...repo.knownIds()];
  const lean = repo.leanFor(id);
  return (
    <article>
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/knowledge", label: "知识" },
          { label: item.id },
        ]}
      />
      <h1 className="text-2xl font-semibold">
        {item.id} — {item.title}
      </h1>
      <RecordView
        kind="knowledge"
        id={item.id}
        title={item.title}
        href={`/knowledge/${item.id}`}
      />
      <div className="mt-4">
        <StatusPair objectStatus={item.objectStatus} />
      </div>
      {item.domain ? (
        <p className="mt-3 text-sm">
          <span className="text-muted">domain</span> {item.domain}
        </p>
      ) : null}
      {item.aliases && item.aliases.length > 0 ? (
        <p className="mt-2 text-sm">
          <span className="text-muted">aliases</span> {item.aliases.join(" · ")}
        </p>
      ) : null}
      {lean.length > 0 ? (
        <p className="mt-3 text-sm">
          {lean.map((row) => (
            <Link key={row.id} href={`/lean/${row.id}`} className="mr-2">
              {row.id} <LeanBadge status={row.status} />
            </Link>
          ))}
        </p>
      ) : null}
      <section className="mt-6">
        <h2 className="text-lg font-semibold">关系</h2>
        <p className="mt-1 text-sm text-muted">
          prerequisites / related 为 explicit；used by 为 derived。
        </p>
        <RelationList title="Prerequisites" items={relations?.prerequisites ?? []} />
        <RelationList title="Related" items={relations?.related ?? []} />
        <RelationList title="Used by（derived）" items={relations?.usedBy ?? []} />
      </section>
      <div className="mt-8">
        <MarkdownView source={item.body} knownIds={knownIds} />
      </div>
    </article>
  );
}
