import Link from "next/link";
import { Breadcrumb } from "../../components/breadcrumb";
import { EmptyState } from "../../components/empty-state";
import { ExplorationSearch } from "../../features/explore/exploration-search";
import { explorationFromRepository } from "../../src/lib/exploration";

type BriefingRow = { id: string; title: string; detail: string; state?: string; pipeline?: string };

function ItemLink({ item }: { item: BriefingRow }) {
  return (
    <li>
      <Link href={`/explore/${encodeURIComponent(item.id)}`} className="font-medium text-accent">
        {item.title}
      </Link>
      <span className="ml-2 text-muted">{item.detail}</span>
    </li>
  );
}

function Section({
  title,
  items,
}: {
  title: string;
  items: BriefingRow[];
}) {
  return (
    <section className="mt-8">
      <h2 className="text-lg font-semibold">{title}</h2>
      {items.length === 0 ? (
        <div className="mt-4">
          <EmptyState title={`没有${title}`} />
        </div>
      ) : (
        <ul className="mt-3 space-y-2 text-sm">
          {items.map((item) => (
            <ItemLink key={item.id} item={item} />
          ))}
        </ul>
      )}
    </section>
  );
}

function groupedExploring(items: BriefingRow[]) {
  const order = ["idea", "generated", "exploring", "tested", "supported", "challenged", "modified", "resolved", "rejected"];
  const buckets = new Map<string, BriefingRow[]>();
  for (const item of items) {
    const key = item.state || "exploring";
    const list = buckets.get(key) ?? [];
    list.push(item);
    buckets.set(key, list);
  }
  return order.filter((key) => buckets.has(key)).map((key) => ({ key, items: buckets.get(key) ?? [] }));
}

export default function ExplorePage() {
  const { briefing, catalog } = explorationFromRepository();
  const exploringGroups = groupedExploring(briefing.exploring);
  const reasoning = catalog.find((row) => row.id === "reasoning");
  const evolution = catalog.find((row) => row.id === "evolution");
  const frontier = catalog.find((row) => row.id === "frontier");
  return (
    <article>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "探索" }]} />
      <h1 className="text-2xl font-semibold">数学探索</h1>
      <p className="mt-2 text-sm text-muted">
        过程层只读投影。不是 Canonical，不能把 Candidate 写成 Theorem。对象层见{" "}
        <Link href="/universe" className="text-accent">
          宇宙
        </Link>
        。Lab 阶段不会映射到 Promotion。
      </p>
      <dl className="mt-6 grid grid-cols-2 gap-2 text-sm sm:grid-cols-3">
        <div>
          <dt className="text-muted">Exploring</dt>
          <dd className="font-mono">{briefing.exploring.length}</dd>
        </div>
        <div>
          <dt className="text-muted">Belief</dt>
          <dd className="font-mono">{briefing.belief.length}</dd>
        </div>
        <div>
          <dt className="text-muted">Failures</dt>
          <dd className="font-mono">{briefing.failures.length}</dd>
        </div>
        <div>
          <dt className="text-muted">Next</dt>
          <dd className="font-mono">{briefing.next.length}</dd>
        </div>
        <div>
          <dt className="text-muted">Theorems invented</dt>
          <dd className="font-mono">{briefing.theoremCount}</dd>
        </div>
        <div>
          <dt className="text-muted">Wrote Canonical</dt>
          <dd className="font-mono">{String(briefing.writesCanonical)}</dd>
        </div>
      </dl>

      <section className="mt-8">
        <h2 className="text-lg font-semibold">五问</h2>
        <ul className="mt-3 space-y-2 text-sm">
          <li>我们知道什么：{briefing.answers.what_we_know}</li>
          <li>正在探索什么：{briefing.answers.what_we_explore}</li>
          <li>为何相信：{briefing.answers.why_we_believe}</li>
          <li>哪些失败了：{briefing.answers.what_failed}</li>
          <li>下一步可能是什么：{briefing.answers.what_is_next}</li>
        </ul>
      </section>

      <ExplorationSearch items={catalog} />

      <Section title="Known" items={briefing.known} />
      <section className="mt-8">
        <h2 className="text-lg font-semibold">Exploring</h2>
        {exploringGroups.length === 0 ? (
          <div className="mt-4">
            <EmptyState title="没有Exploring" />
          </div>
        ) : (
          exploringGroups.map((group) => (
            <div key={group.key} className="mt-4">
              <h3 className="text-sm font-medium text-muted">lifecycle={group.key}</h3>
              <ul className="mt-2 space-y-2 text-sm">
                {group.items.map((item) => (
                  <ItemLink key={item.id} item={item} />
                ))}
              </ul>
            </div>
          ))
        )}
      </section>
      <Section title="Belief" items={briefing.belief} />
      <Section title="Failures" items={briefing.failures} />
      <Section title="Patterns" items={briefing.patterns} />
      <Section title="Next" items={briefing.next} />
      {reasoning ? (
        <section className="mt-8">
          <h2 className="text-lg font-semibold">推理图</h2>
          <p className="mt-2 text-sm">
            <Link href={`/explore/${encodeURIComponent("reasoning")}`} className="text-accent">
              {reasoning.title}
            </Link>
            <span className="ml-2 text-muted">{reasoning.detail}</span>
          </p>
        </section>
      ) : null}
      <Section title="笔记本" items={catalog.filter((row) => row.group === "笔记本")} />
      <Section title="会话" items={catalog.filter((row) => row.group === "会话")} />
      {catalog.some((row) => row.group === "证明策略") ? (
        <Section title="证明策略" items={catalog.filter((row) => row.group === "证明策略")} />
      ) : null}
      {frontier ? (
        <section className="mt-8">
          <h2 className="text-lg font-semibold">前沿</h2>
          <p className="mt-2 text-sm">
            <Link href={`/explore/${encodeURIComponent("frontier")}`} className="text-accent">
              {frontier.title}
            </Link>
            <span className="ml-2 text-muted">{frontier.detail}</span>
          </p>
        </section>
      ) : null}
      {evolution ? (
        <section className="mt-8">
          <h2 className="text-lg font-semibold">理论模块</h2>
          <p className="mt-2 text-sm">
            <Link href={`/explore/${encodeURIComponent("evolution")}`} className="text-accent">
              {evolution.title}
            </Link>
            <span className="ml-2 text-muted">{evolution.detail}</span>
          </p>
        </section>
      ) : null}
    </article>
  );
}
