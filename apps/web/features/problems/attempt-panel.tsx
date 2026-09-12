"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import type { AttemptRecord } from "@math-ai-lab/content";
import type { OperationResult } from "@math-ai-lab/domain";
import { MarkdownView } from "../../components/markdown-view";
import { submitOperation } from "../operations/client";
import { PreviewDialog } from "../operations/preview-dialog";
import { ValidationResultView } from "../operations/validation-result";

const OUTCOMES = ["unassessed", "partial", "correct", "incorrect", "unsolved", "abandoned"] as const;

export function AttemptPanel({
  problemId,
  parts,
  attempts,
}: {
  problemId: string;
  parts: string[];
  attempts: AttemptRecord[];
}) {
  const router = useRouter();
  const [narrative, setNarrative] = useState("");
  const [outcome, setOutcome] = useState<(typeof OUTCOMES)[number]>("unassessed");
  const [part, setPart] = useState(parts[0] ?? "");
  const [preview, setPreview] = useState<OperationResult | null>(null);
  const [finalResult, setFinalResult] = useState<OperationResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [open, setOpen] = useState(false);

  const payload = {
    problemId,
    narrative,
    outcome,
    assistance: "independent",
    ...(part ? { part } : {}),
  };

  async function onPreview() {
    setBusy(true);
    setFinalResult(null);
    const result = await submitOperation({
      operation: "RecordAttempt",
      preview: true,
      payload,
    });
    setPreview(result);
    setOpen(true);
    setBusy(false);
  }

  async function onConfirm() {
    setBusy(true);
    const result = await submitOperation({
      operation: "RecordAttempt",
      preview: false,
      payload,
    });
    setFinalResult(result);
    setOpen(false);
    setBusy(false);
    if (result.success) {
      setNarrative("");
      router.refresh();
    }
  }

  return (
    <section id="attempts" className="mt-10">
      <h2 className="text-lg font-semibold">My Attempts</h2>
      <p className="mt-1 text-sm text-muted">
        只记录你自己的作答。canonical / AI 解答不会进入 Attempt ledger。append-only。
      </p>
      {attempts.length === 0 ? (
        <p className="mt-3 text-sm text-muted">还没有 Attempt。</p>
      ) : (
        <ol className="mt-4 space-y-4">
          {attempts.map((row) => (
            <li key={row.id} className="border border-line p-3">
              <p className="font-mono text-sm">
                {row.id}
                {row.part ? ` · part ${row.part}` : ""} · {row.outcome} · {row.assistance}
              </p>
              {row.attemptedAt ? <p className="text-xs text-muted">{row.attemptedAt}</p> : null}
              {row.narrative ? (
                <div className="mt-2">
                  <MarkdownView source={row.narrative} syncToc={false} />
                </div>
              ) : null}
            </li>
          ))}
        </ol>
      )}

      <form
        className="mt-6 space-y-3"
        onSubmit={(event) => {
          event.preventDefault();
          void onPreview();
        }}
      >
        <h3 className="text-base font-semibold">New Attempt</h3>
        {parts.length > 0 ? (
          <label className="block text-sm">
            <span className="text-muted">part</span>
            <select
              className="mt-1 block w-full border border-line bg-canvas px-2 py-1"
              value={part}
              onChange={(event) => setPart(event.target.value)}
            >
              <option value="">（整题）</option>
              {parts.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
        ) : null}
        <label className="block text-sm">
          <span className="text-muted">outcome</span>
          <select
            className="mt-1 block w-full border border-line bg-canvas px-2 py-1"
            value={outcome}
            onChange={(event) => setOutcome(event.target.value as (typeof OUTCOMES)[number])}
          >
            {OUTCOMES.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="text-muted">作答</span>
          <textarea
            required
            rows={8}
            className="mt-1 block w-full border border-line bg-canvas px-2 py-1 font-mono text-sm"
            value={narrative}
            onChange={(event) => setNarrative(event.target.value)}
          />
        </label>
        <button type="submit" className="rounded border border-accent px-3 py-1.5 text-sm" disabled={busy}>
          预览 Attempt
        </button>
      </form>
      {finalResult ? (
        <div className="mt-4 border border-line p-3">
          <ValidationResultView result={finalResult} />
        </div>
      ) : null}
      <PreviewDialog
        open={open}
        title="预览 RecordAttempt"
        result={preview}
        busy={busy}
        onCancel={() => setOpen(false)}
        onConfirm={() => void onConfirm()}
      />
    </section>
  );
}
