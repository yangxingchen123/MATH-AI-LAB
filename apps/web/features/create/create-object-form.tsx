"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import type { DomainOperation, OperationResult } from "@math-ai-lab/domain";
import { submitOperation } from "../operations/client";
import { PreviewDialog } from "../operations/preview-dialog";
import { ValidationResultView } from "../operations/validation-result";

export function CreateObjectForm({
  operation,
  heading,
  extra,
}: {
  operation: Extract<DomainOperation, "CreateProblem" | "CreateKnowledge" | "CreateMethod">;
  heading: string;
  extra?: "domain" | "parts";
}) {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [domain, setDomain] = useState("");
  const [parts, setParts] = useState("");
  const [preview, setPreview] = useState<OperationResult | null>(null);
  const [finalResult, setFinalResult] = useState<OperationResult | null>(null);
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  function payload(): Record<string, unknown> {
    const data: Record<string, unknown> = { title, body };
    if (extra === "domain" && domain.trim()) data.domain = domain.trim();
    if (extra === "parts" && parts.trim()) {
      data.parts = parts
        .split(/[\s,]+/)
        .map((item) => item.trim())
        .filter(Boolean);
    }
    return data;
  }

  async function onPreview() {
    setBusy(true);
    const result = await submitOperation({ operation, preview: true, payload: payload() });
    setPreview(result);
    setOpen(true);
    setBusy(false);
  }

  async function onConfirm() {
    setBusy(true);
    const result = await submitOperation({ operation, preview: false, payload: payload() });
    setFinalResult(result);
    setOpen(false);
    setBusy(false);
    const created = result.planned?.id;
    if (result.success && typeof created === "string") {
      if (operation === "CreateProblem") router.push(`/problems/${created}`);
      if (operation === "CreateKnowledge") router.push(`/knowledge/${created}`);
      if (operation === "CreateMethod") router.push(`/methods/${created}`);
      router.refresh();
    }
  }

  return (
    <form
      className="mt-6 space-y-4"
      onSubmit={(event) => {
        event.preventDefault();
        void onPreview();
      }}
    >
      <h1 className="text-2xl font-semibold">{heading}</h1>
      <p className="text-sm text-muted">
        只收集 Frozen Schema 已有字段。ID 由 Python 分配。预览通过后再确认写入。
      </p>
      <label className="block text-sm">
        <span className="text-muted">title</span>
        <input
          required
          className="mt-1 block w-full border border-line bg-canvas px-2 py-1"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
        />
      </label>
      {extra === "domain" ? (
        <label className="block text-sm">
          <span className="text-muted">domain（可选，draft 可不填）</span>
          <input
            className="mt-1 block w-full border border-line bg-canvas px-2 py-1"
            value={domain}
            onChange={(event) => setDomain(event.target.value)}
          />
        </label>
      ) : null}
      {extra === "parts" ? (
        <label className="block text-sm">
          <span className="text-muted">parts（可选，空格或逗号分隔，仅真实 multipart）</span>
          <input
            className="mt-1 block w-full border border-line bg-canvas px-2 py-1"
            value={parts}
            onChange={(event) => setParts(event.target.value)}
          />
        </label>
      ) : null}
      <label className="block text-sm">
        <span className="text-muted">正文</span>
        <textarea
          required
          rows={12}
          className="mt-1 block w-full border border-line bg-canvas px-2 py-1 font-mono text-sm"
          value={body}
          onChange={(event) => setBody(event.target.value)}
        />
      </label>
      <button type="submit" className="rounded border border-accent px-3 py-1.5 text-sm" disabled={busy}>
        预览
      </button>
      {finalResult ? (
        <div className="border border-line p-3">
          <ValidationResultView result={finalResult} />
        </div>
      ) : null}
      <PreviewDialog
        open={open}
        title={`预览 ${operation}`}
        result={preview}
        busy={busy}
        onCancel={() => setOpen(false)}
        onConfirm={() => void onConfirm()}
      />
    </form>
  );
}
