import { Breadcrumb } from "../../../components/breadcrumb";
import { RecordView } from "../../../features/prefs/record-view";
import { rejectBadId, requireObject } from "../../../src/lib/require-content";
import { MarkdownView } from "../../../components/markdown-view";
import { StatusPair } from "../../../components/status-pair";
import { getRepository } from "../../../src/lib/repo";

export default async function MethodDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  rejectBadId(id);
  const item = requireObject(getRepository().getMethod(id));
  return (
    <article>
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/methods", label: "方法" },
          { label: item.id },
        ]}
      />
      <h1 className="text-2xl font-semibold">
        {item.id} — {item.title}
      </h1>
      <RecordView
        kind="method"
        id={item.id}
        title={item.title}
        href={`/methods/${item.id}`}
      />
      <div className="mt-4">
        <StatusPair objectStatus={item.objectStatus} />
      </div>
      {item.knowledge && item.knowledge.length > 0 ? (
        <p className="mt-3 text-sm">
          <span className="text-muted">knowledge</span> {item.knowledge.join(", ")}
        </p>
      ) : null}
      <div className="mt-8">
        <MarkdownView source={item.body} />
      </div>
    </article>
  );
}
