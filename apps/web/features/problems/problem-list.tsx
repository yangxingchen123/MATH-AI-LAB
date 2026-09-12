import Link from "next/link";
import type { Problem } from "@math-ai-lab/domain";
import { ObjectStatusText, WorkflowText } from "../../components/status-pair";

export function ProblemList({ items }: { items: Problem[] }) {
  if (items.length === 0) {
    return <p className="text-muted">还没有题目。</p>;
  }
  return (
    <div className="overflow-x-auto">
    <table className="w-full min-w-[40rem] border-collapse text-sm">
      <thead>
        <tr className="border-b border-line text-left text-muted">
          <th className="py-2 pr-3 font-medium">ID</th>
          <th className="py-2 pr-3 font-medium">标题</th>
          <th className="py-2 pr-3 font-medium">objectStatus</th>
          <th className="py-2 pr-3 font-medium">workflowDir</th>
          <th className="py-2 font-medium">parts</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id} className="border-b border-line">
            <td className="py-2 pr-3 font-mono">
              <Link href={`/problems/${item.id}`} className="text-accent">
                {item.id}
              </Link>
            </td>
            <td className="py-2 pr-3">{item.title}</td>
            <td className="py-2 pr-3">
              <ObjectStatusText status={item.objectStatus} />
            </td>
            <td className="py-2 pr-3">
              <WorkflowText dir={item.workflowDir} />
            </td>
            <td className="py-2 font-mono">
              {item.parts?.length ? item.parts.join(", ") : "—"}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
    </div>
  );
}
