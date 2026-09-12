import Link from "next/link";
import { Breadcrumb } from "../../components/breadcrumb";
import { EmptyState } from "../../components/empty-state";
import { universeFromRepository } from "../../src/lib/universe";
import { getRepository } from "../../src/lib/repo";

export default function UniversePage() {
  const snap = universeFromRepository(getRepository());
  return (
    <article>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "宇宙" }]} />
      <h1 className="text-2xl font-semibold">数学宇宙</h1>
      <p className="mt-2 text-sm text-muted">
        只读投影。不是新 Schema，不写仓库。Knowledge 不会变成 Theorem。Lab 仍是 Candidate。
        过程层见{" "}
        <Link href="/explore" className="text-accent">
          探索
        </Link>
        。
      </p>
      <dl className="mt-6 grid grid-cols-2 gap-2 text-sm sm:grid-cols-3">
        <div>
          <dt className="text-muted">Entity</dt>
          <dd className="font-mono">{snap.entities.length}</dd>
        </div>
        <div>
          <dt className="text-muted">Relation</dt>
          <dd className="font-mono">{snap.relations.length}</dd>
        </div>
        <div>
          <dt className="text-muted">Evidence</dt>
          <dd className="font-mono">{snap.evidence.length}</dd>
        </div>
        <div>
          <dt className="text-muted">Candidate</dt>
          <dd className="font-mono">{snap.candidates.length}</dd>
        </div>
        <div>
          <dt className="text-muted">Event</dt>
          <dd className="font-mono">{snap.events.length}</dd>
        </div>
        <div>
          <dt className="text-muted">Space</dt>
          <dd className="font-mono">{snap.spaces.length}</dd>
        </div>
      </dl>

      <section className="mt-8">
        <h2 className="text-lg font-semibold">Research spaces</h2>
        {snap.spaces.length === 0 ? (
          <p className="mt-2 text-sm text-muted">没有可投影的领域。</p>
        ) : (
          <ul className="mt-2 space-y-1 text-sm">
            {snap.spaces.map((space) => (
              <li key={space.id}>
                {space.title}
                <span className="ml-2 text-muted">
                  {space.origin} · {space.entityIds.length}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-8">
        <h2 className="text-lg font-semibold">Entities</h2>
        {snap.entities.length === 0 ? (
          <div className="mt-4">
            <EmptyState title="没有实体" />
          </div>
        ) : (
          <table className="mt-3 w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-line text-left text-muted">
                <th className="py-1 pr-3">type</th>
                <th className="py-1 pr-3">title</th>
                <th className="py-1 pr-3">status</th>
                <th className="py-1">source</th>
              </tr>
            </thead>
            <tbody>
              {snap.entities.map((item) => (
                <tr key={item.id} className="border-b border-line">
                  <td className="py-1 pr-3 font-mono">{item.type}</td>
                  <td className="py-1 pr-3">
                    <Link href={`/universe/${encodeURIComponent(item.id)}`} className="text-accent">
                      {item.title}
                    </Link>
                  </td>
                  <td className="py-1 pr-3">{item.status}</td>
                  <td className="py-1 font-mono text-xs">
                    {item.source.kind}/{item.source.id}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="mt-8">
        <h2 className="text-lg font-semibold">Timeline</h2>
        {snap.events.length === 0 ? (
          <p className="mt-2 text-sm text-muted">没有可投影的事件。</p>
        ) : (
          <ol className="mt-3 space-y-2 text-sm">
            {snap.events.slice(0, 40).map((event) => (
              <li key={event.id}>
                <span className="font-mono">{event.type}</span>
                <span className="ml-2 text-muted">{event.actor}</span>
                <span className="ml-2">{event.description}</span>
              </li>
            ))}
          </ol>
        )}
      </section>
    </article>
  );
}
