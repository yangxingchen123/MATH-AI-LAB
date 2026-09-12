"use client";

import { useToc } from "./toc-context";

export function Toc() {
  const { headings } = useToc();
  return (
    <nav aria-label="本页目录" className="text-sm">
      <p className="mb-2 text-xs uppercase tracking-wide text-muted">本页</p>
      {headings.length === 0 ? (
        <p className="text-muted">此页没有目录。</p>
      ) : (
        <ol className="space-y-1">
          {headings
            .filter((item) => item.level <= 3)
            .map((item) => (
              <li
                key={item.id}
                style={{ paddingLeft: `${Math.max(0, item.level - 1) * 0.75}rem` }}
              >
                <a href={`#${item.id}`} className="text-ink hover:text-accent">
                  {item.text}
                </a>
              </li>
            ))}
        </ol>
      )}
    </nav>
  );
}
