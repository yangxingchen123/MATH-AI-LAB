import Link from "next/link";
import { Breadcrumb } from "../../components/breadcrumb";
import { EmptyState } from "../../components/empty-state";
import { LeanBadge } from "../../components/lean-badge";
import { getRepository } from "../../src/lib/repo";

export default function LeanPage() {
  const items = getRepository().listLean();
  return (
    <article>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "Lean" }]} />
      <h1 className="text-2xl font-semibold">Lean 验证</h1>
      <p className="mt-2 text-sm text-muted">
        Verified 只来自 manifest 的 <code>build.status=SUCCEEDED</code>。源文件存在不等于已验证。
      </p>
      {items.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="没有 correspondence 记录" />
        </div>
      ) : (
        <table className="mt-6 w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-line text-left text-muted">
              <th className="py-2 pr-3">ID</th>
              <th className="py-2 pr-3">陈述</th>
              <th className="py-2">状态</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b border-line">
                <td className="py-2 pr-3 font-mono">
                  <Link href={`/lean/${encodeURIComponent(item.id)}`} className="text-accent">
                    {item.id}
                  </Link>
                </td>
                <td className="py-2 pr-3">{item.title}</td>
                <td className="py-2">
                  <LeanBadge status={item.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </article>
  );
}
