"use client";

import { useEffect, useState } from "react";
import {
  isPinned,
  recordView,
  togglePin,
  type PrefKind,
} from "./local-prefs";

export function RecordView({
  kind,
  id,
  title,
  href,
}: {
  kind: PrefKind;
  id: string;
  title: string;
  href: string;
}) {
  const [pinned, setPinned] = useState(false);

  useEffect(() => {
    recordView({ kind, id, title, href });
    setPinned(isPinned(kind, id));
  }, [kind, id, title, href]);

  return (
    <button
      type="button"
      className="mt-3 rounded border border-line px-2 py-1 text-sm"
      aria-pressed={pinned}
      onClick={() => setPinned(togglePin({ kind, id, title, href }))}
    >
      {pinned ? "取消固定" : "固定"}
    </button>
  );
}
