import Link from "next/link";
import { Breadcrumb } from "../../components/breadcrumb";
import { EmptyState } from "../../components/empty-state";
import { MarkdownView } from "../../components/markdown-view";
import { getRepository } from "../../src/lib/repo";

export default function MemoryPage() {
  const items = getRepository().listMemory();
  const current = items.find((item) => item.role === "current");
  const topics = items.filter((item) => item.role === "topics");
  const research = items.filter((item) => item.role === "research");
  const goals = items.filter((item) => item.role === "goals");
  const milestones = items.filter((item) => item.role === "milestones");
  const generated = items.filter((item) => item.generated);
  const source = items.filter((item) => !item.generated);
  return (
    <article>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "记忆" }]} />
      <h1 className="text-2xl font-semibold">学习状态</h1>
      <p className="mt-2 text-sm text-muted">
        映射 <code>09_长期记忆/</code>。自动索引只读，不是普通文件浏览器。
      </p>
      {items.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="没有学习状态文件" />
        </div>
      ) : null}
      {current ? (
        <section className="mt-8">
          <h2 className="text-lg font-semibold">当前状态</h2>
          <MarkdownView source={current.body} syncToc={false} />
        </section>
      ) : null}
      <Section title="主题" items={topics} />
      <Section title="研究状态" items={research} />
      <Section title="目标" items={goals} />
      <Section title="里程碑" items={milestones} />
      <section className="mt-8">
        <h2 className="text-lg font-semibold">源文件</h2>
        <FileList items={source} />
      </section>
      <section className="mt-8">
        <h2 className="text-lg font-semibold">自动索引（只读 / GENERATED）</h2>
        <FileList items={generated} />
      </section>
    </article>
  );
}

function Section({
  title,
  items,
}: {
  title: string;
  items: { id: string; title: string; sourcePath: string }[];
}) {
  if (items.length === 0) return null;
  return (
    <section className="mt-8">
      <h2 className="text-lg font-semibold">{title}</h2>
      <FileList items={items} />
    </section>
  );
}

function FileList({
  items,
}: {
  items: { id: string; title: string; sourcePath: string }[];
}) {
  return (
    <ul className="mt-2 space-y-1 text-sm">
      {items.map((item) => (
        <li key={item.id}>
          <Link href={`/memory/${encodeURIComponent(item.id)}`} className="text-accent">
            {item.title}
          </Link>
          <span className="ml-2 text-muted">{item.sourcePath}</span>
        </li>
      ))}
    </ul>
  );
}
