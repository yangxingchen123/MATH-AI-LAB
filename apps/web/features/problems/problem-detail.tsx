import Link from "next/link";
import { knowledgeMappingLabel, type Problem, type ProblemRelationView } from "@math-ai-lab/domain";
import type { AttemptRecord, ProblemBodyView } from "@math-ai-lab/content";
import type { LeanTheorem, OutputArtifact } from "@math-ai-lab/domain";
import { ArtifactList } from "../../components/artifact-card";
import { Breadcrumb } from "../../components/breadcrumb";
import { LeanBadge } from "../../components/lean-badge";
import { MarkdownView } from "../../components/markdown-view";
import { RelationList } from "../../components/relation-list";
import { StatusPair } from "../../components/status-pair";
import { RecordView } from "../prefs/record-view";
import { DocumentOutline } from "../shell/document-outline";
import type { TocHeading } from "../shell/toc-context";
import { AttemptPanel } from "./attempt-panel";
import { WorkflowPanel } from "./workflow-panel";

export function ProblemDetail({
  problem,
  view,
  attempts,
  relations,
  outline,
  knownIds,
  lean,
  artifacts,
}: {
  problem: Problem;
  view: ProblemBodyView;
  attempts: AttemptRecord[];
  relations: ProblemRelationView | null;
  outline: TocHeading[];
  knownIds: string[];
  lean: LeanTheorem[];
  artifacts: OutputArtifact[];
}) {
  return (
    <article>
      <DocumentOutline headings={outline} />
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/problems", label: "题目" },
          { label: problem.workflowDir ?? "题目" },
          { label: problem.id },
        ]}
      />
      <h1 className="text-2xl font-semibold">
        {problem.id} — {problem.title}
      </h1>
      <RecordView
        kind="problem"
        id={problem.id}
        title={problem.title}
        href={`/problems/${problem.id}`}
      />
      <div className="mt-4">
        <StatusPair
          objectStatus={problem.objectStatus}
          workflowDir={problem.workflowDir}
        />
      </div>
      <p className="mt-3 text-sm">
        <span className="text-muted">knowledge</span>{" "}
        {knowledgeMappingLabel(problem.knowledgeMapping)}
      </p>
      {lean.length > 0 ? (
        <p className="mt-3 text-sm">
          <span className="text-muted">Lean</span>{" "}
          {lean.map((item) => (
            <Link key={item.id} href={`/lean/${item.id}`} className="mr-2">
              {item.id} <LeanBadge status={item.status} />
            </Link>
          ))}
        </p>
      ) : null}

      <section id="statement" className="mt-8">
        <h2 className="text-lg font-semibold">题面</h2>
        <div className="mt-3">
          <MarkdownView source={view.shared} syncToc={false} knownIds={knownIds} />
        </div>
      </section>

      {view.parts.map((part) => (
        <section key={part.id} id={`part-${part.id}`} className="mt-10">
          <h2 className="text-lg font-semibold">Part ({part.id})</h2>
          {part.statement ? (
            <div className="mt-3">
              <h3 className="text-sm font-medium text-muted">题设</h3>
              <MarkdownView source={part.statement} syncToc={false} knownIds={knownIds} />
            </div>
          ) : null}
          {part.notes ? (
            <div className="mt-3">
              <h3 className="text-sm font-medium text-muted">研究记录</h3>
              <MarkdownView source={part.notes} syncToc={false} knownIds={knownIds} />
            </div>
          ) : null}
          {part.solution ? (
            <div className="mt-3">
              <h3 className="text-sm font-medium text-muted">
                解答（AI / canonical ≠ Attempt）
              </h3>
              <MarkdownView source={part.solution} syncToc={false} knownIds={knownIds} />
            </div>
          ) : null}
        </section>
      ))}

      {view.trailing ? (
        <section id="trailing" className="mt-10">
          <MarkdownView source={view.trailing} syncToc={false} knownIds={knownIds} />
        </section>
      ) : null}

      <section id="relations" className="mt-10">
        <h2 className="text-lg font-semibold">Knowledge / Methods</h2>
        <p className="mt-1 text-sm text-muted">
          explicit 来自 YAML；derived 由 Adapter 运行时计算，不是 canonical。
        </p>
        <RelationList title="用到的知识" items={relations?.knowledge ?? []} />
        <RelationList title="相关方法（derived）" items={relations?.methods ?? []} />
        <RelationList title="相关题目（derived）" items={relations?.relatedProblems ?? []} />
      </section>

      <section id="verification" className="mt-10">
        <h2 className="text-lg font-semibold">Verification</h2>
        {lean.length > 0 ? (
          <p className="mt-2 text-sm">
            {lean.map((item) => (
              <Link key={item.id} href={`/lean/${item.id}`} className="mr-2">
                {item.id} <LeanBadge status={item.status} />
              </Link>
            ))}
          </p>
        ) : (
          <p className="mt-2 text-sm text-muted">Not Formalized。没有 correspondence / manifest 证据。</p>
        )}
      </section>

      <ArtifactList items={artifacts} />

      <AttemptPanel
        problemId={problem.id}
        parts={problem.parts ?? view.parts.map((part) => part.id)}
        attempts={attempts}
      />
      <WorkflowPanel problemId={problem.id} current={problem.workflowDir} />
    </article>
  );
}
