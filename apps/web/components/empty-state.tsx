export function EmptyState({ title, detail }: { title: string; detail?: string }) {
  return (
    <div className="border border-dashed border-line px-4 py-6 text-muted">
      <p className="font-medium text-ink">{title}</p>
      {detail ? <p className="mt-2 text-sm">{detail}</p> : null}
    </div>
  );
}
