import { isUnsafeId } from "@math-ai-lab/domain";
import { Breadcrumb } from "../../../components/breadcrumb";
import { MarkdownView } from "../../../components/markdown-view";
import { requireObject } from "../../../src/lib/require-content";
import { getRepository } from "../../../src/lib/repo";

export default async function MemoryDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const decoded = decodeURIComponent(id);
  if (isUnsafeId(decoded) || decoded.includes("..")) {
    requireObject(null);
  }
  const item = requireObject(getRepository().getMemory(decoded));
  return (
    <article>
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/memory", label: "记忆" },
          { label: item.title },
        ]}
      />
      <h1 className="text-2xl font-semibold">{item.title}</h1>
      <p className="mt-2 text-sm text-muted">
        {item.sourcePath}
        {item.generated ? " · GENERATED 只读" : ""}
      </p>
      <div className="mt-6">
        <MarkdownView source={item.body} />
      </div>
    </article>
  );
}
