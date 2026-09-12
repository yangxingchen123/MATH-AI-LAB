import Link from "next/link";
import { ThemeToggle } from "./theme-toggle";

export function Topbar() {
  return (
    <header className="flex h-12 items-center justify-between border-b border-line bg-[var(--sidebar)] px-4">
      <Link href="/" className="text-xs font-bold tracking-[0.12em] text-accent">
        MATH-AI-LAB
      </Link>
      <div className="flex items-center gap-2">
        <button
          type="button"
          className="hidden rounded-lg border border-line px-3 py-1 text-sm text-muted hover:border-accent hover:text-ink md:inline"
          data-search-trigger="true"
          aria-label="打开搜索"
        >
          搜索
          <kbd className="ml-2 text-xs">Ctrl K</kbd>
        </button>
        <ThemeToggle />
        <Link
          href="/settings"
          className="rounded-lg border border-line px-2.5 py-1 text-sm text-ink hover:border-accent"
        >
          设置
        </Link>
      </div>
    </header>
  );
}
