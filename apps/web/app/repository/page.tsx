import Link from "next/link";
import { Breadcrumb } from "../../components/breadcrumb";
import { EmptyState } from "../../components/empty-state";
import { getRepository } from "../../src/lib/repo";

export default async function RepositoryPage({
  searchParams,
}: {
  searchParams: Promise<{ path?: string }>;
}) {
  const { path = "" } = await searchParams;
  const repo = getRepository();
  const listing = repo.listExplorer(path);
  const file = path && !listing ? repo.readExplorerFile(path) : null;
  return (
    <article>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "仓库" }]} />
      <h1 className="text-2xl font-semibold">仓库浏览</h1>
      <p className="mt-2 text-sm text-muted">
        高级只读视图。不执行源码，不写文件。一次只列一层目录。
      </p>
      {!listing && !file ? (
        <div className="mt-6">
          <EmptyState title="路径不可用" detail="只允许仓库内白名单目录，禁止 .. 与隐藏缓存。" />
        </div>
      ) : null}
      {listing ? (
        <ul className="mt-6 space-y-1 text-sm">
          {path ? (
            <li>
              <Link
                href={`/repository?path=${encodeURIComponent(parentOf(path))}`}
                className="text-accent"
              >
                ..
              </Link>
            </li>
          ) : null}
          {listing.entries.map((entry) => (
            <li key={entry.path}>
              <Link
                href={
                  entry.kind === "dir"
                    ? `/repository?path=${encodeURIComponent(entry.path)}`
                    : `/repository?path=${encodeURIComponent(entry.path)}`
                }
                className="text-accent"
              >
                {entry.kind === "dir" ? `${entry.name}/` : entry.name}
              </Link>
            </li>
          ))}
        </ul>
      ) : null}
      {file ? (
        <div className="mt-6">
          <p className="text-sm text-muted">{file.path}</p>
          {file.previewKind === "pdf" ? (
            <iframe
              title={file.path}
              src={`/api/artifact?path=${encodeURIComponent(file.path)}`}
              className="mt-3 h-[70vh] w-full border border-line"
            />
          ) : null}
          {file.text ? (
            <pre className="mt-3 overflow-x-auto border border-line bg-[var(--sidebar)] p-3 text-sm">
              <code>{file.text}</code>
            </pre>
          ) : null}
          {file.previewKind === "unsupported" ? (
            <p className="mt-3 text-sm text-muted">此类型不预览。</p>
          ) : null}
        </div>
      ) : null}
    </article>
  );
}

function parentOf(path: string): string {
  const parts = path.split("/").filter(Boolean);
  parts.pop();
  return parts.join("/");
}
