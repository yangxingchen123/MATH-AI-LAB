import type { ObjectStatus, WorkflowDir } from "@math-ai-lab/domain";

export function ObjectStatusText({ status }: { status: ObjectStatus }) {
  const label =
    status === "draft" ? "draft" : status === "reviewed" ? "reviewed" : "archived";
  return <span className="font-mono text-sm">{label}</span>;
}

export function WorkflowText({ dir }: { dir: WorkflowDir | null }) {
  return <span className="font-mono text-sm">{dir ?? "—"}</span>;
}

export function StatusPair({
  objectStatus,
  workflowDir,
}: {
  objectStatus: ObjectStatus;
  workflowDir?: WorkflowDir | null;
}) {
  return (
    <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-sm">
      <dt className="text-muted">objectStatus</dt>
      <dd>
        <ObjectStatusText status={objectStatus} />
      </dd>
      {workflowDir !== undefined ? (
        <>
          <dt className="text-muted">workflowDir</dt>
          <dd>
            <WorkflowText dir={workflowDir} />
          </dd>
        </>
      ) : null}
    </dl>
  );
}
