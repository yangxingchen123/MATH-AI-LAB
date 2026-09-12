import { Breadcrumb } from "../../components/breadcrumb";
import { EmptyState } from "../../components/empty-state";
import { MarkdownView } from "../../components/markdown-view";
import { PromotePanel } from "../../features/inbox/promote-panel";
import { getRepository } from "../../src/lib/repo";

export default function InboxPage() {
  const items = getRepository().listInbox();
  return (
    <article>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "收件箱" }]} />
      <h1 className="text-2xl font-semibold">收件箱</h1>
      <p className="mt-2 text-sm text-muted">
        映射 <code>00_收件箱/</code>。建议类型是 Derived，不是 canonical。
      </p>
      {items.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="收件箱是空的" />
        </div>
      ) : (
        <ul className="mt-6 space-y-8">
          {items.map((item) => (
            <li key={item.id}>
              <h2 className="text-lg font-semibold">{item.title}</h2>
              <p className="text-sm text-muted">{item.sourcePath}</p>
              {item.suggestion ? (
                <p className="mt-2 text-sm">Suggested（Derived）：{item.suggestion}</p>
              ) : (
                <p className="mt-2 text-sm text-muted">尚未分类。不会自动写回。</p>
              )}
              {item.body ? (
                <div className="mt-3">
                  <MarkdownView source={item.body} syncToc={false} />
                </div>
              ) : null}
              <PromotePanel
                inboxId={item.id}
                defaultTitle={item.title}
                defaultBody={item.body ?? ""}
              />
            </li>
          ))}
        </ul>
      )}
    </article>
  );
}
