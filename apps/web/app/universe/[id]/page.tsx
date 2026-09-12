import Link from "next/link";
import { notFound } from "next/navigation";
import { historyOf, parseEntityId, relatedIds } from "@math-ai-lab/domain-math";
import { Breadcrumb } from "../../../components/breadcrumb";
import { universeFromRepository } from "../../../src/lib/universe";
import { getRepository } from "../../../src/lib/repo";

export default async function UniverseEntityPage({
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
  if (!parseEntityId(id)) {
    notFound();
  }
  const snap = universeFromRepository(getRepository());
  const entity = snap.entities.find((row) => row.id === id);
  if (!entity) {
    notFound();
  }
  const relations = snap.relations.filter((row) => row.source === id || row.target === id);
  const evidence = snap.evidence.filter((row) => row.claim === id);
  const events = historyOf(snap.events, id);
  const related = relatedIds({ nodes: snap.entities, edges: snap.relations }, id);
  return (
    <article>
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/universe", label: "宇宙" },
          { label: entity.type },
        ]}
      />
      <h1 className="text-2xl font-semibold">{entity.title}</h1>
      <p className="mt-2 font-mono text-sm text-muted">{entity.id}</p>
      <p className="mt-3 text-sm">
        {entity.type} · {entity.status} · {entity.source.kind}/{entity.source.id}
      </p>
      <p className="mt-3 text-sm">{entity.description}</p>
      {entity.source.href ? (
        <p className="mt-3 text-sm">
          <Link href={entity.source.href} className="text-accent">
            打开源对象
          </Link>
        </p>
      ) : null}

      <section className="mt-8">
        <h2 className="text-lg font-semibold">Relations</h2>
        {relations.length === 0 ? (
          <p className="mt-2 text-sm text-muted">没有数学语义关系。</p>
        ) : (
          <table className="mt-3 w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-line text-left text-muted">
                <th className="py-1 pr-3">type</th>
                <th className="py-1 pr-3">from → to</th>
                <th className="py-1 pr-3">origin</th>
                <th className="py-1">evidence</th>
              </tr>
            </thead>
            <tbody>
              {relations.map((row) => (
                <tr key={row.id} className="border-b border-line">
                  <td className="py-1 pr-3 font-mono">{row.type}</td>
                  <td className="py-1 pr-3 font-mono text-xs">
                    <Link href={`/universe/${encodeURIComponent(row.source)}`} className="text-accent">
                      {row.source}
                    </Link>
                    {" → "}
                    <Link href={`/universe/${encodeURIComponent(row.target)}`} className="text-accent">
                      {row.target}
                    </Link>
                  </td>
                  <td className="py-1 pr-3">{row.origin}</td>
                  <td className="py-1 text-xs">
                    {row.evidence.kind}
                    {row.evidence.note ? ` · ${row.evidence.note}` : ""}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="mt-8">
        <h2 className="text-lg font-semibold">Related</h2>
        {related.length === 0 ? (
          <p className="mt-2 text-sm text-muted">没有相邻实体。</p>
        ) : (
          <ul className="mt-2 space-y-1 text-sm">
            {related.map((relatedId) => (
              <li key={relatedId}>
                <Link href={`/universe/${encodeURIComponent(relatedId)}`} className="font-mono text-accent">
                  {relatedId}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-8">
        <h2 className="text-lg font-semibold">Evidence</h2>
        {evidence.length === 0 ? (
          <p className="mt-2 text-sm text-muted">没有绑定到此实体的证据记录。</p>
        ) : (
          <ul className="mt-2 space-y-1 text-sm">
            {evidence.map((row) => (
              <li key={row.id}>
                {row.evidenceType} · {row.status} · confidence={row.confidence}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-8">
        <h2 className="text-lg font-semibold">History</h2>
        {events.length === 0 ? (
          <p className="mt-2 text-sm text-muted">没有历史事件。</p>
        ) : (
          <ol className="mt-2 space-y-1 text-sm">
            {events.map((event) => (
              <li key={event.id}>
                {event.type} · {event.description}
              </li>
            ))}
          </ol>
        )}
      </section>
    </article>
  );
}
