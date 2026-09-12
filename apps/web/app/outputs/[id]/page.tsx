import { isUnsafeId } from "@math-ai-lab/domain";
import { Breadcrumb } from "../../../components/breadcrumb";
import { MarkdownView } from "../../../components/markdown-view";
import { requireObject } from "../../../src/lib/require-content";
import { getRepository } from "../../../src/lib/repo";

export default async function OutputDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const decoded = decodeURIComponent(id);
  if (isUnsafeId(decoded) || decoded.includes("..")) {
    requireObject(null);
  }
  const repo = getRepository();
  const item = requireObject(repo.getOutput(decoded));
  const file = item.kind === "markdown" ? repo.readExplorerFile(item.sourcePath) : null;
  return (
    <article>
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/outputs", label: "成果" },
          { label: item.title },
        ]}
      />
      <h1 className="text-2xl font-semibold">{item.title}</h1>
      <p className="mt-2 text-sm text-muted">
        {item.kind} · {item.sourcePath}
      </p>
      {item.kind === "pdf" ? (
        <div className="mt-6">
          <iframe
            title={item.title}
            src={`/api/artifact?path=${encodeURIComponent(item.sourcePath)}`}
            className="h-[70vh] w-full border border-line"
          />
        </div>
      ) : null}
      {file?.text ? (
        <div className="mt-6">
          <MarkdownView source={file.text} />
        </div>
      ) : null}
      <p className="mt-6">
        <a
          href={`/api/artifact?path=${encodeURIComponent(item.sourcePath)}`}
          className="text-accent"
        >
          下载 / 打开
        </a>
      </p>
    </article>
  );
}
