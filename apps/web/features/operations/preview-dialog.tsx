"use client";

import type { OperationResult } from "@math-ai-lab/domain";
import { ValidationResultView } from "./validation-result";

export function PreviewDialog({
  open,
  title,
  result,
  busy,
  onCancel,
  onConfirm,
}: {
  open: boolean;
  title: string;
  result: OperationResult | null;
  busy?: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  if (!open) return null;
  const canConfirm = Boolean(result?.success && result.preview && result.validation !== "FAIL");
  return (
    <div className="fixed inset-0 z-50">
      <button
        type="button"
        className="absolute inset-0 bg-black/40"
        aria-label="关闭预览"
        onClick={onCancel}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="preview-title"
        className="relative mx-auto mt-[8vh] max-h-[80vh] w-[min(40rem,calc(100%-2rem))] overflow-y-auto border border-line bg-[var(--panel)] p-4 shadow-lg"
      >
        <h2 id="preview-title" className="text-lg font-semibold">
          {title}
        </h2>
        <div className="mt-4">
          {result ? <ValidationResultView result={result} /> : <p className="text-sm text-muted">正在预览…</p>}
        </div>
        <div className="mt-6 flex flex-wrap gap-2">
          <button
            type="button"
            className="rounded border border-line px-3 py-1.5 text-sm"
            onClick={onCancel}
          >
            取消
          </button>
          <button
            type="button"
            className="rounded border border-accent px-3 py-1.5 text-sm"
            disabled={!canConfirm || busy}
            onClick={onConfirm}
          >
            {busy ? "写入中…" : "确认写入"}
          </button>
        </div>
      </div>
    </div>
  );
}
