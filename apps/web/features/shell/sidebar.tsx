"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { HOME_NAV, NAV_GROUPS, isActivePath, type NavItem } from "./nav";

function NavLink({ item, pathname }: { item: NavItem; pathname: string }) {
  if (item.href && item.phase === "ready") {
    const active = isActivePath(pathname, item.href);
    return (
      <Link
        href={item.href}
        className={`block rounded-md px-2 py-1.5 ${
          active
            ? "bg-[var(--accent-soft)] font-medium text-ink"
            : "text-ink hover:bg-[var(--card)]"
        }`}
      >
        {item.label}
      </Link>
    );
  }
  return (
    <span
      className="block cursor-not-allowed rounded px-2 py-1 text-muted"
      aria-disabled="true"
      title="尚未开放"
    >
      {item.label}
    </span>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  return (
    <nav aria-label="主导航" className="text-sm">
      <ul className="mb-5 space-y-0.5">
        <li>
          <NavLink item={HOME_NAV} pathname={pathname} />
        </li>
      </ul>
      {NAV_GROUPS.map((group) => (
        <div key={group.id} className="mb-5">
          <p className="mb-2 px-2 text-xs uppercase tracking-wide text-muted">
            {group.label}
          </p>
          <ul className="space-y-0.5">
            {group.items.map((item) => (
              <li key={item.id}>
                <NavLink item={item} pathname={pathname} />
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}
