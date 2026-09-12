import Link from "next/link";
import { Breadcrumb } from "../../components/breadcrumb";
import { KnowledgeList } from "../../features/knowledge/knowledge-list";
import { getRepository } from "../../src/lib/repo";

export default function KnowledgeIndexPage() {
  const items = getRepository().listKnowledge();
  return (
    <div>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "知识" }]} />
      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-3">
        <h1 className="text-2xl font-semibold">知识</h1>
        <Link href="/knowledge/new" className="text-sm text-accent">
          创建知识
        </Link>
      </div>
      <KnowledgeList items={items} />
    </div>
  );
}
