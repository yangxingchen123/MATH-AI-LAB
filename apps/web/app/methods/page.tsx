import Link from "next/link";
import { Breadcrumb } from "../../components/breadcrumb";
import { MethodList } from "../../features/methods/method-list";
import { getRepository } from "../../src/lib/repo";

export default function MethodsIndexPage() {
  const items = getRepository().listMethods();
  return (
    <div>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "方法" }]} />
      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-3">
        <h1 className="text-2xl font-semibold">方法</h1>
        <Link href="/methods/new" className="text-sm text-accent">
          创建方法
        </Link>
      </div>
      <MethodList items={items} />
    </div>
  );
}
