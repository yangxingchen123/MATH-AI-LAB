"use client";

import { useEffect } from "react";
import { useToc, type TocHeading } from "./toc-context";

export function DocumentOutline({ headings }: { headings: TocHeading[] }) {
  const { setHeadings } = useToc();
  useEffect(() => {
    setHeadings(headings);
    return () => setHeadings([]);
  }, [headings, setHeadings]);
  return null;
}
