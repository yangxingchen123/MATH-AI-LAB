import { isUnsafeId } from "@math-ai-lab/domain";
import { Breadcrumb } from "../../../components/breadcrumb";
import { LeanBadge } from "../../../components/lean-badge";
import { requireObject } from "../../../src/lib/require-content";
import { getRepository } from "../../../src/lib/repo";

export default async function LeanDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const decoded = decodeURIComponent(id);
  if (isUnsafeId(decoded)) {
    requireObject(null);
  }
  const item = requireObject(getRepository().getLean(decoded));
  return (
    <article className="mx-auto max-w-prose">
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/lean", label: "Lean" },
          { label: item.id },
        ]}
      />
      <h1 className="text-2xl font-semibold">{item.id}</h1>
      <p className="mt-3">{item.title}</p>
      <div className="mt-4">
        <LeanBadge status={item.status} />
      </div>
      <dl className="mt-6 space-y-2 text-sm">
        {item.leanDecl ? (
          <div>
            <dt className="text-muted">定理名</dt>
            <dd className="font-mono">{item.leanDecl}</dd>
          </div>
        ) : null}
        {item.leanFile ? (
          <div>
            <dt className="text-muted">源文件</dt>
            <dd className="font-mono">{item.leanFile}</dd>
          </div>
        ) : null}
        {item.evidencePath ? (
          <div>
            <dt className="text-muted">验证证据</dt>
            <dd className="font-mono">{item.evidencePath}</dd>
          </div>
        ) : (
          <div>
            <dt className="text-muted">验证证据</dt>
            <dd>无 SUCCEEDED / FAILED manifest。不能显示为已验证。</dd>
          </div>
        )}
        {item.logSummary ? (
          <div>
            <dt className="text-muted">摘要</dt>
            <dd>{item.logSummary}</dd>
          </div>
        ) : null}
      </dl>
    </article>
  );
}
