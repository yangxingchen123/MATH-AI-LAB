import Link from "next/link";
import { ContinuePanel } from "../features/home/continue-panel";
import { getRepository } from "../src/lib/repo";

export default function HomePage() {
  const repo = getRepository();
  const knowledge = repo.listKnowledge();
  const problems = repo.listProblems();
  const methods = repo.listMethods();
  const research = repo.listResearch();
  const inbox = repo.listInbox().filter((item) => item.id.toLowerCase() !== "readme.md");
  const currentProblems = problems.filter((item) => item.workflowDir === "研究中");
  const openProblems = problems.filter((item) => item.workflowDir === "未解决");
  const workflow = {
    未解决: problems.filter((item) => item.workflowDir === "未解决").length,
    研究中: problems.filter((item) => item.workflowDir === "研究中").length,
    已解决: problems.filter((item) => item.workflowDir === "已解决").length,
  };
  const currentResearch = research[0];

  return (
    <article className="mx-auto max-w-prose">
      <h1 className="text-2xl font-semibold">工作台</h1>
      <p className="mt-2 text-sm text-muted">下一步做什么。写入走 Domain Operation，不直接改 Markdown。</p>

      <ContinuePanel />

      <section className="mt-8">
        <h2 className="text-lg font-semibold">当前题目</h2>
        {currentProblems.length === 0 && openProblems.length === 0 ? (
          <p className="mt-2 text-sm text-muted">没有研究中或未解决的题目。</p>
        ) : (
          <ul className="mt-2 space-y-1 text-sm">
            {currentProblems.map((item) => (
              <li key={item.id}>
                <Link href={`/problems/${item.id}`} className="text-accent">
                  {item.id} {item.title}
                </Link>
                <span className="ml-2 text-muted">研究中</span>
              </li>
            ))}
            {openProblems.slice(0, 5).map((item) => (
              <li key={item.id}>
                <Link href={`/problems/${item.id}`} className="text-accent">
                  {item.id} {item.title}
                </Link>
                <span className="ml-2 text-muted">未解决</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      {currentResearch ? (
        <section className="mt-8">
          <h2 className="text-lg font-semibold">当前研究</h2>
          <p className="mt-2">
            <Link
              href={`/research/${encodeURIComponent(currentResearch.slug)}`}
              className="text-accent"
            >
              {currentResearch.title}
            </Link>
            <span className="ml-2 text-sm text-muted">{currentResearch.kind}</span>
          </p>
        </section>
      ) : null}

      <section className="mt-8">
        <h2 className="text-lg font-semibold">收件箱</h2>
        <p className="mt-2 text-sm">
          <Link href="/inbox" className="text-accent">
            {inbox.length} 条待处理
          </Link>
        </p>
      </section>

      <section className="settings-card">
        <p className="settings-kicker">仓库</p>
        <h2 className="mt-1 text-lg font-semibold tracking-tight">真实计数</h2>
        <dl className="mt-3 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
          <div>
            <dt className="text-xs text-muted">知识</dt>
            <dd className="text-xl font-semibold tracking-tight">{knowledge.length}</dd>
          </div>
          <div>
            <dt className="text-xs text-muted">题目</dt>
            <dd className="text-xl font-semibold tracking-tight">{problems.length}</dd>
          </div>
          <div>
            <dt className="text-xs text-muted">方法</dt>
            <dd className="text-xl font-semibold tracking-tight">{methods.length}</dd>
          </div>
          <div>
            <dt className="text-xs text-muted">研究</dt>
            <dd className="text-xl font-semibold tracking-tight">{research.length}</dd>
          </div>
        </dl>
        <p className="mt-3 text-sm text-muted">
          题目目录：未解决 {workflow.未解决} · 研究中 {workflow.研究中} · 已解决 {workflow.已解决}
        </p>
      </section>
    </article>
  );
}
