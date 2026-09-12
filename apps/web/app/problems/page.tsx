import Link from "next/link";
import { Breadcrumb } from "../../components/breadcrumb";
import { ProblemList } from "../../features/problems/problem-list";
import { getRepository } from "../../src/lib/repo";

export default function ProblemsIndexPage() {
  const items = getRepository().listProblems();
  return (
    <div>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "题目" }]} />
      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-3">
        <h1 className="text-2xl font-semibold">题目</h1>
        <Link href="/problems/new" className="text-sm text-accent">
          创建题目
        </Link>
      </div>
      <p className="mb-4 text-sm text-muted">
        objectStatus 来自 YAML；未解决 / 研究中 / 已解决 只表示目录工作流。
      </p>
      <ProblemList items={items} />
    </div>
  );
}
