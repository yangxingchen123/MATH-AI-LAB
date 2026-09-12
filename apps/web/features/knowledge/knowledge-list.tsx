import Link from "next/link";
import type { Knowledge } from "@math-ai-lab/domain";
import { ObjectStatusText } from "../../components/status-pair";

export function KnowledgeList({ items }: { items: Knowledge[] }) {
  if (items.length === 0) {
    return <p className="text-muted">还没有知识条目。</p>;
  }
  return (
    <div className="overflow-x-auto">
    <table className="w-full min-w-[36rem] border-collapse text-sm">
      <thead>
        <tr className="border-b border-line text-left text-muted">
          <th className="py-2 pr-3 font-medium">ID</th>
          <th className="py-2 pr-3 font-medium">标题</th>
          <th className="py-2 pr-3 font-medium">objectStatus</th>
          <th className="py-2 font-medium">domain</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id} className="border-b border-line">
            <td className="py-2 pr-3 font-mono">
              <Link href={`/knowledge/${item.id}`} className="text-accent">
                {item.id}
              </Link>
            </td>
            <td className="py-2 pr-3">{item.title}</td>
            <td className="py-2 pr-3">
              <ObjectStatusText status={item.objectStatus} />
            </td>
            <td className="py-2">{item.domain ?? "—"}</td>
          </tr>
        ))}
      </tbody>
    </table>
    </div>
  );
}
