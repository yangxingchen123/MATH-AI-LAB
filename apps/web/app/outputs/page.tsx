import Link from "next/link";
import { Breadcrumb } from "../../components/breadcrumb";
import { EmptyState } from "../../components/empty-state";
import { getRepository } from "../../src/lib/repo";

export default function OutputsPage() {
  const items = getRepository().listOutputs();
  return (
    <div>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "成果" }]} />
      <h1 className="text-2xl font-semibold">成果</h1>
      <p className="mt-2 text-sm text-muted">
        只列出 <code>08_成果输出/</code> 的真实文件。没有就不编。
      </p>
      {items.length === 0 ? (
        <div className="mt-6">
          <EmptyState
            title="还没有正式成果文件"
            detail="发布 PDF / 讲义后会出现在这里。不会把整个 PDF 塞进首页 HTML。"
          />
        </div>
      ) : (
        <ul className="mt-6 space-y-2 text-sm">
          {items.map((item) => (
            <li key={item.id}>
              <Link href={item.href} className="text-accent">
                {item.title}
              </Link>
              <span className="ml-2 text-muted">
                {item.kind} · {item.sourcePath}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
