import Link from "next/link";
import { Breadcrumb } from "../../components/breadcrumb";
import { EmptyState } from "../../components/empty-state";
import { getRepository } from "../../src/lib/repo";

export default function ReferencesPage() {
  const items = getRepository().listReferences();
  return (
    <div>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "参考" }]} />
      <h1 className="text-2xl font-semibold">参考</h1>
      <p className="mt-2 text-sm text-muted">
        只映射 <code>03_参考资料/</code> 已有 identity。缺失字段不制造。
      </p>
      {items.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="还没有参考资料身份记录" detail="不是文献管理器。有 identity.md 才会出现。" />
        </div>
      ) : (
        <table className="mt-6 w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-line text-left text-muted">
              <th className="py-2 pr-3">ID</th>
              <th className="py-2 pr-3">标题</th>
              <th className="py-2 pr-3">类型</th>
              <th className="py-2">年份</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b border-line">
                <td className="py-2 pr-3 font-mono">
                  <Link href={`/references/${encodeURIComponent(item.id)}`} className="text-accent">
                    {item.id}
                  </Link>
                </td>
                <td className="py-2 pr-3">{item.title}</td>
                <td className="py-2 pr-3">{item.kind}</td>
                <td className="py-2">{item.year ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
