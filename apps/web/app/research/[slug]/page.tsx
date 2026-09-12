import { isUnsafeId } from "@math-ai-lab/domain";
import { Breadcrumb } from "../../../components/breadcrumb";
import { MarkdownView } from "../../../components/markdown-view";
import { RecordView } from "../../../features/prefs/record-view";
import { DocumentOutline } from "../../../features/shell/document-outline";
import { requireObject } from "../../../src/lib/require-content";
import { researchOutline } from "../../../src/lib/outline";
import { getRepository } from "../../../src/lib/repo";

export default async function ResearchDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const decoded = decodeURIComponent(slug);
  if (isUnsafeId(decoded) || decoded === "_模板") {
    requireObject(null);
  }
  const repo = getRepository();
  const item = requireObject(repo.getResearch(decoded));
  const knownIds = [...repo.knownIds()];
  const timeline = repo.researchTimeline(decoded);
  const evidence = repo.researchEvidence(decoded);
  const lean = repo.leanFor(decoded);
  return (
    <article>
      <DocumentOutline headings={researchOutline(item)} />
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/research", label: "研究" },
          { label: item.slug },
        ]}
      />
      <h1 className="text-2xl font-semibold">{item.title}</h1>
      <RecordView
        kind="research"
        id={item.slug}
        title={item.title}
        href={`/research/${encodeURIComponent(item.slug)}`}
      />
      <p className="mt-2 text-sm text-muted">
        {item.slug} · {item.kind} · 不是 Problem
      </p>
      {item.sections.map((section) => (
        <section key={section.id} id={section.id} className="mt-8">
          <h2 className="text-lg font-semibold">{section.title}</h2>
          <div className="mt-3">
            <MarkdownView source={section.body} syncToc={false} knownIds={knownIds} />
          </div>
        </section>
      ))}
      <section id="timeline" className="mt-10">
        <h2 className="text-lg font-semibold">时间线</h2>
        <p className="mt-1 text-sm text-muted">
          文件日期是 derived，不是 Schema 里的精确记录。
        </p>
        <ol className="mt-3 space-y-2 text-sm">
          {timeline.map((event) => (
            <li key={event.id}>
              <span className="text-muted">{event.at ?? "日期不可靠"}</span>
              <span className="mx-2">{event.label}</span>
              <span className="text-xs text-muted">{event.origin}</span>
            </li>
          ))}
        </ol>
      </section>
      <section id="evidence" className="mt-10">
        <h2 className="text-lg font-semibold">证据</h2>
        <p className="mt-1 text-sm text-muted">
          Research Lab Candidate 不会因为出现在这里而变成正式 Source。
        </p>
        <ul className="mt-3 space-y-2 text-sm">
          {evidence.map((row) => (
            <li key={`${row.kind}-${row.sourcePath}`}>
              <span className="font-mono text-xs">{row.kind}</span>
              <span className="ml-2">{row.label}</span>
              {row.sourcePath ? (
                <span className="ml-2 text-muted">{row.sourcePath}</span>
              ) : null}
            </li>
          ))}
        </ul>
        {lean.length > 0 ? (
          <p className="mt-3 text-sm">相关 Lean 记录 {lean.length} 条，见 Lean 页。</p>
        ) : null}
      </section>
    </article>
  );
}
