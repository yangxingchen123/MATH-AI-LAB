import { isUnsafeId } from "@math-ai-lab/domain";
import { Breadcrumb } from "../../../components/breadcrumb";
import { CopyButton } from "../../../components/copy-button";
import { MarkdownView } from "../../../components/markdown-view";
import { requireObject } from "../../../src/lib/require-content";
import { getRepository } from "../../../src/lib/repo";

export default async function PromptDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const decoded = decodeURIComponent(id);
  if (isUnsafeId(decoded)) {
    requireObject(null);
  }
  const item = requireObject(getRepository().getPrompt(decoded));
  return (
    <article>
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/prompts", label: "提示词" },
          { label: item.title },
        ]}
      />
      <h1 className="text-2xl font-semibold">{item.title}</h1>
      <p className="mt-2 text-sm text-muted">
        {item.category} · {item.sourcePath}
      </p>
      <div className="mt-4">
        <CopyButton text={item.body} label="复制全文" />
      </div>
      <div className="mt-6">
        <MarkdownView source={item.body} />
      </div>
    </article>
  );
}
