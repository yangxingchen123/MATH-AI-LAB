import Link from "next/link";
import type { OutputArtifact } from "@math-ai-lab/domain";

export function ArtifactCard({ item }: { item: OutputArtifact }) {
  return (
    <li className="border border-line px-3 py-2 text-sm">
      <Link href={item.href} className="text-accent">
        {item.title}
      </Link>
      <p className="text-xs text-muted">
        {item.kind} · {item.sourcePath}
      </p>
    </li>
  );
}

export function ArtifactList({ items }: { items: OutputArtifact[] }) {
  if (items.length === 0) return null;
  return (
    <section id="artifacts" className="mt-10">
      <h2 className="text-lg font-semibold">Artifacts</h2>
      <ul className="mt-3 space-y-2">
        {items.map((item) => (
          <ArtifactCard key={item.id} item={item} />
        ))}
      </ul>
    </section>
  );
}
