"use client";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <article className="mx-auto max-w-prose">
      <h1 className="text-2xl font-semibold">页面出错</h1>
      <p className="mt-3 text-muted">这一页失败了，应用其它部分仍可使用。</p>
      <pre className="mt-4 overflow-x-auto border border-line bg-[var(--sidebar)] p-3 text-sm">
        {error.message}
      </pre>
      <button
        type="button"
        onClick={reset}
        className="mt-4 rounded border border-line px-3 py-1"
      >
        重试
      </button>
    </article>
  );
}
