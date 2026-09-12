import Link from "next/link";
import type { Method } from "@math-ai-lab/domain";
import { ObjectStatusText } from "../../components/status-pair";

export function MethodList({ items }: { items: Method[] }) {
  if (items.length === 0) {
    return <p className="text-muted">还没有方法条目。</p>;
  }
  return (
    <div className="overflow-x-auto">
    <table className="w-full min-w-[28rem] border-collapse text-sm">
      <thead>
        <tr className="border-b border-line text-left text-muted">
          <th className="py-2 pr-3 font-medium">ID</th>
          <th className="py-2 pr-3 font-medium">标题</th>
          <th className="py-2 font-medium">objectStatus</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id} className="border-b border-line">
            <td className="py-2 pr-3 font-mono">
              <Link href={`/methods/${item.id}`} className="text-accent">
                {item.id}
              </Link>
            </td>
            <td className="py-2 pr-3">{item.title}</td>
            <td className="py-2">
              <ObjectStatusText status={item.objectStatus} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
    </div>
  );
}
