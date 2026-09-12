import Link from "next/link";
import { isUnsafeId } from "@math-ai-lab/domain";
import { Breadcrumb } from "../../../components/breadcrumb";
import { requireObject } from "../../../src/lib/require-content";
import { getRepository } from "../../../src/lib/repo";

export default async function ReferenceDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const decoded = decodeURIComponent(id);
  if (isUnsafeId(decoded)) {
    requireObject(null);
  }
  const item = requireObject(getRepository().getReference(decoded));
  return (
    <article className="mx-auto max-w-prose">
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/references", label: "参考" },
          { label: item.id },
        ]}
      />
      <h1 className="text-2xl font-semibold">{item.title}</h1>
      <dl className="mt-4 space-y-1 text-sm">
        <div>
          <dt className="inline text-muted">类型</dt> <dd className="inline">{item.kind}</dd>
        </div>
        {item.authors?.length ? (
          <div>
            <dt className="inline text-muted">作者</dt>{" "}
            <dd className="inline">{item.authors.join(", ")}</dd>
          </div>
        ) : null}
        {item.year ? (
          <div>
            <dt className="inline text-muted">年份</dt> <dd className="inline">{item.year}</dd>
          </div>
        ) : null}
        {item.venue ? (
          <div>
            <dt className="inline text-muted">来源</dt> <dd className="inline">{item.venue}</dd>
          </div>
        ) : null}
        {item.domain ? (
          <div>
            <dt className="inline text-muted">领域</dt> <dd className="inline">{item.domain}</dd>
          </div>
        ) : null}
        {item.doi ? (
          <div>
            <dt className="inline text-muted">DOI</dt> <dd className="inline">{item.doi}</dd>
          </div>
        ) : null}
        {item.arxiv ? (
          <div>
            <dt className="inline text-muted">arXiv</dt> <dd className="inline">{item.arxiv}</dd>
          </div>
        ) : null}
        {item.bibtex ? (
          <div>
            <dt className="inline text-muted">BibTeX</dt> <dd className="inline">{item.bibtex}</dd>
          </div>
        ) : null}
        <div>
          <dt className="inline text-muted">路径</dt>{" "}
          <dd className="inline font-mono">{item.sourcePath}</dd>
        </div>
      </dl>
      {item.pdfPath ? (
        <p className="mt-4">
          <a
            href={`/api/artifact?path=${encodeURIComponent(item.pdfPath)}`}
            className="text-accent"
            target="_blank"
            rel="noreferrer"
          >
            打开 PDF
          </a>
        </p>
      ) : null}
      {item.relatedResearch.length > 0 ? (
        <p className="mt-4 text-sm">
          相关研究{" "}
          {item.relatedResearch.map((slug) => (
            <Link key={slug} href={`/research/${encodeURIComponent(slug)}`} className="text-accent">
              {slug}
            </Link>
          ))}
        </p>
      ) : null}
      {item.notes ? <p className="mt-6 text-sm text-muted">{item.notes}</p> : null}
    </article>
  );
}
