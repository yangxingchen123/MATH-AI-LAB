"use client";

import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

export interface TocHeading {
  id: string;
  level: number;
  text: string;
}

interface TocState {
  headings: TocHeading[];
  setHeadings: (headings: TocHeading[]) => void;
}

const TocContext = createContext<TocState | null>(null);

export function TocProvider({ children }: { children: ReactNode }) {
  const [headings, setHeadings] = useState<TocHeading[]>([]);
  const value = useMemo(() => ({ headings, setHeadings }), [headings]);
  return <TocContext.Provider value={value}>{children}</TocContext.Provider>;
}

export function useToc() {
  const ctx = useContext(TocContext);
  if (!ctx) {
    throw new Error("useToc must be used within TocProvider");
  }
  return ctx;
}
