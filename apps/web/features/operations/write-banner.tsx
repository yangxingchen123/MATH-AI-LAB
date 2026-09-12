"use client";

import { useEffect, useState } from "react";

export function WriteBanner() {
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/operations/health")
      .then((response) => response.json())
      .then((data: { writes?: boolean; detail?: string }) => {
        if (!data.writes) {
          setMessage(`Write operations unavailable. ${data.detail ?? ""}`.trim());
        }
      })
      .catch(() => setMessage("Write operations unavailable."));
  }, []);

  if (!message) return null;
  return (
    <p className="border-b border-line bg-[var(--sidebar)] px-4 py-2 text-sm" role="status">
      {message} 界面仍可阅读。
    </p>
  );
}
