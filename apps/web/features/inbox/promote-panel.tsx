"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import type { OperationResult } from "@math-ai-lab/domain";
import { submitOperation } from "../operations/client";
import { PreviewDialog } from "../operations/preview-dialog";
import { ValidationResultView } from "../operations/validation-result";

export function PromotePanel({
  inboxId,
  defaultTitle,
  defaultBody,
}: {
  inboxId: string;
  defaultTitle: string;
  defaultBody: string;
}) {
  const router = useRouter();
  const [targetType, setTargetType] = useState<"problem" | "knowledge" | "method">("problem");
  const [title, setTitle] = useState(defaultTitle);
  const [body, setBody] = useState(defaultBody);
  const [preview, setPreview] = useState<OperationResult | null>(null);
  const [finalResult, setFinalResult] = useState<OperationResult | null>(null);
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  const payload = { inboxId, targetType, title, body };

  async function onPreview() {
    setBusy(true);
    const result = await submitOperation({
      operation: "PromoteInboxItem",
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
      operation: "PromoteInboxItem",
      preview: false,
      payload,
    });
    setFinalResult(result);
    setOpen(false);
    setBusy(false);
    const created = result.planned?.id;
    if (result.success && typeof created === "string") {
      if (targetType === "problem") router.push(`/problems/${created}`);
      if (targetType === "knowledge") router.push(`/knowledge/${created}`);
      if (targetType === "method") router.push(`/methods/${created}`);
    }
  }

  if (inboxId.toLowerCase() === "readme.md") {
    return null;
  }

  return (
    <form
      className="mt-4 space-y-3 border border-line p-3"
      onSubmit={(event) => {
        event.preventDefault();
        void onPreview();
      }}
    >
      <h3 className="text-sm font-semibold">提升为正式对象</h3>
      <p className="text-xs text-muted">
        建议类型只是 Derived。写入走 Create*；收件箱原文件按现有生命周期保留。
      </p>
      <label className="block text-sm">
        <span className="text-muted">targetType</span>
        <select
          className="mt-1 block w-full border border-line bg-canvas px-2 py-1"
          value={targetType}
          onChange={(event) => setTargetType(event.target.value as typeof targetType)}
        >
          <option value="problem">Problem</option>
          <option value="knowledge">Knowledge</option>
          <option value="method">Method</option>
        </select>
      </label>
      <label className="block text-sm">
        <span className="text-muted">title</span>
        <input
          className="mt-1 block w-full border border-line bg-canvas px-2 py-1"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          required
        />
      </label>
      <label className="block text-sm">
        <span className="text-muted">正文</span>
        <textarea
          className="mt-1 block w-full border border-line bg-canvas px-2 py-1 font-mono text-sm"
          rows={6}
          value={body}
          onChange={(event) => setBody(event.target.value)}
          required
        />
      </label>
      <button type="submit" className="rounded border border-accent px-3 py-1.5 text-sm" disabled={busy}>
        预览提升
      </button>
      {finalResult ? <ValidationResultView result={finalResult} /> : null}
      <PreviewDialog
        open={open}
        title="预览 PromoteInboxItem"
        result={preview}
        busy={busy}
        onCancel={() => setOpen(false)}
        onConfirm={() => void onConfirm()}
      />
    </form>
  );
}
