import { getSearchProvider, type SearchType } from "@math-ai-lab/content";
import { NextResponse } from "next/server";
import { getRepository } from "../../../src/lib/repo";

const TYPES = new Set([
  "knowledge",
  "problem",
  "method",
  "research_project",
  "reference",
  "output",
  "memory",
  "prompt",
  "lean",
  "lab",
]);

export function GET(request: Request) {
  const url = new URL(request.url);
  const query = url.searchParams.get("q") ?? "";
  const type = url.searchParams.get("type") ?? undefined;
  const status = url.searchParams.get("status") ?? undefined;
  const domain = url.searchParams.get("domain") ?? undefined;
  const hits = getSearchProvider(getRepository()).search(query, {
    type: type && TYPES.has(type) ? (type as SearchType) : undefined,
    status: status || undefined,
    domain: domain || undefined,
  });
  return NextResponse.json({ hits });
}
