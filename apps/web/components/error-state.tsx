export function ErrorState({ title, detail }: { title: string; detail?: string }) {
  return (
    <div className="border border-danger px-4 py-6" role="alert">
      <p className="font-medium">{title}</p>
      {detail ? <p className="mt-2 text-sm text-muted">{detail}</p> : null}
    </div>
  );
}
