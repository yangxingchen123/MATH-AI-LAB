import type { ReactNode } from "react";

export function SettingsCard({
  kicker,
  title,
  extra,
  children,
}: {
  kicker: string;
  title: string;
  extra?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="settings-card">
      <p className="settings-kicker">{kicker}</p>
      <div className="mt-1 flex items-start justify-between gap-3">
        <h2 className="text-lg font-semibold tracking-tight">{title}</h2>
        {extra}
      </div>
      {children}
    </section>
  );
}

export function StatusBadge({
  tone,
  children,
}: {
  tone: "ok" | "idle" | "err";
  children: ReactNode;
}) {
  return <span className={`status-badge tone-${tone}`}>{children}</span>;
}
