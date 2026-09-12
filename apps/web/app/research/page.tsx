import Link from "next/link";
import { Breadcrumb } from "../../components/breadcrumb";
import { getRepository } from "../../src/lib/repo";

export default function ResearchIndexPage() {
  const items = getRepository().listResearch();
  return (
    <div>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "研究" }]} />
      <h1 className="mb-4 text-2xl font-semibold">研究</h1>
      <p className="mb-4 text-sm text-muted">
        这里只列出 <code>07_项目/</code> 的 Dossier。研究中的习题仍在题目库。
      </p>
      {items.length === 0 ? (
        <p className="text-muted">还没有研究项目。</p>
      ) : (
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-line text-left text-muted">
              <th className="py-2 pr-3 font-medium">项目</th>
              <th className="py-2 pr-3 font-medium">标题</th>
              <th className="py-2 font-medium">kind</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.slug} className="border-b border-line">
                <td className="py-2 pr-3 font-mono">
                  <Link
                    href={`/research/${encodeURIComponent(item.slug)}`}
                    className="text-accent"
                  >
                    {item.slug}
                  </Link>
                </td>
                <td className="py-2 pr-3">{item.title}</td>
                <td className="py-2">{item.kind}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
