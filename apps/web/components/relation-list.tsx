import Link from "next/link";
import type { RelatedRef } from "@math-ai-lab/domain";

export function RelationList({
  title,
  items,
}: {
  title: string;
  items: RelatedRef[];
}) {
  return (
    <section className="mt-4">
      <h3 className="text-sm font-medium text-muted">{title}</h3>
      {items.length === 0 ? (
        <p className="mt-1 text-sm text-muted">无</p>
      ) : (
        <ul className="mt-1 space-y-1 text-sm">
          {items.map((item) => (
            <li key={`${item.origin}-${item.id}`}>
              <Link href={item.href} className="text-accent">
                {item.id} {item.title}
              </Link>
              <span className="ml-2 text-xs text-muted">{item.origin}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
