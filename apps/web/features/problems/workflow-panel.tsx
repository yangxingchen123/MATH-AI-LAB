"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import type { OperationResult, WorkflowDir } from "@math-ai-lab/domain";
import { WORKFLOW_DIRS } from "@math-ai-lab/domain";
import { submitOperation } from "../operations/client";
import { PreviewDialog } from "../operations/preview-dialog";
import { ValidationResultView } from "../operations/validation-result";

export function WorkflowPanel({
  problemId,
  current,
}: {
  problemId: string;
  current: WorkflowDir | string | null;
}) {
  const router = useRouter();
  const [target, setTarget] = useState<string>(current && current !== "其他" ? current : "研究中");
  const [preview, setPreview] = useState<OperationResult | null>(null);
  const [finalResult, setFinalResult] = useState<OperationResult | null>(null);
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  async function onPreview() {
    setBusy(true);
    const result = await submitOperation({
      operation: "MoveProblemWorkflow",
      preview: true,
      payload: { problemId, targetWorkflow: target },
    });
    setPreview(result);
    setOpen(true);
    setBusy(false);
  }

  async function onConfirm() {
    setBusy(true);
    const result = await submitOperation({
      operation: "MoveProblemWorkflow",
      preview: false,
      payload: { problemId, targetWorkflow: target },
    });
    setFinalResult(result);
    setOpen(false);
    setBusy(false);
    if (result.success) router.refresh();
  }

  return (
    <section id="workflow" className="mt-10">
      <h2 className="text-lg font-semibold">Move workflow</h2>
      <p className="mt-1 text-sm text-muted">
        只移动 <code>02_题目库/</code> 目录。这不是 YAML objectStatus。
      </p>
      <p className="mt-2 text-sm">
        当前 workflowDir：<span className="font-mono">{current ?? "其他"}</span>
      </p>
      <div className="mt-3 flex flex-wrap items-end gap-2">
        <label className="text-sm">
          <span className="text-muted">目标</span>
          <select
            className="ml-2 border border-line bg-canvas px-2 py-1"
            value={target}
            onChange={(event) => setTarget(event.target.value)}
          >
            {WORKFLOW_DIRS.map((dir) => (
              <option key={dir} value={dir}>
                {dir}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          className="rounded border border-accent px-3 py-1.5 text-sm"
          disabled={busy}
          onClick={() => void onPreview()}
        >
          预览移动
        </button>
      </div>
      {finalResult ? (
        <div className="mt-4 border border-line p-3">
          <ValidationResultView result={finalResult} />
        </div>
      ) : null}
      <PreviewDialog
        open={open}
        title="预览 MoveProblemWorkflow"
        result={preview}
        busy={busy}
        onCancel={() => setOpen(false)}
        onConfirm={() => void onConfirm()}
      />
    </section>
  );
}
