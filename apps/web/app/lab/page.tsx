import { Breadcrumb } from "../../components/breadcrumb";
import { EmptyState } from "../../components/empty-state";
import { LeanBadge } from "../../components/lean-badge";
import { SumFreePanel } from "../../features/lab/sum-free-panel";
import { getRepository } from "../../src/lib/repo";

export default function LabPage() {
  const repo = getRepository();
  const items = repo.listLab();
  const leanByDecl = new Map(repo.listLean().map((row) => [row.leanDecl ?? "", row]));
  return (
    <article>
      <Breadcrumb items={[{ href: "/", label: "工作台" }, { label: "Lab" }]} />
      <h1 className="text-2xl font-semibold">Research Lab</h1>
      <p className="mt-2 text-sm text-muted">
        只读 Candidate / 实验记录。UI 不能把它升级成正式知识源。
      </p>
      {items.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="没有 Lab 记录" />
        </div>
      ) : (
        <ul className="mt-6 space-y-6">
          {items.map((item) => (
            <li key={item.id} id={item.id} className="border-b border-line pb-4">
              <p className="font-mono text-sm">{item.id}</p>
              <h2 className="text-lg font-semibold">{item.title}</h2>
              <p className="mt-1 text-sm">
                <span className="rounded border border-line px-2 py-0.5 text-xs">Candidate</span>
                <span className="ml-2 text-muted">
                  {item.kind}
                  {item.stage ? ` · ${item.stage}` : ""}
                  {item.novelty ? ` · ${item.novelty}` : ""}
                </span>
              </p>
              <p className="mt-2 text-sm text-muted">{item.sourcePath}</p>
              {item.notes ? <p className="mt-2 text-sm">{item.notes}</p> : null}
              {item.leanDecls.length > 0 ? (
                <ul className="mt-2 text-sm">
                  {item.leanDecls.map((decl) => {
                    const lean = leanByDecl.get(decl);
                    return (
                      <li key={decl}>
                        <span className="font-mono">{decl}</span>{" "}
                        {lean ? <LeanBadge status={lean.status} /> : (
                          <span className="text-xs text-muted">Unverified</span>
                        )}
                      </li>
                    );
                  })}
                </ul>
              ) : null}
            </li>
          ))}
        </ul>
      )}
      <SumFreePanel />
    </article>
  );
}
