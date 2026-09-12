import { METHOD_ID, KNOWLEDGE_ID, PROBLEM_ID } from "./schema.ts";
import { isReservedId, isUnsafeId } from "./types.ts";

export type StableObjectType = "knowledge" | "problem" | "method";

export type ContentRefStatus = "ok" | "broken" | "ignore";

export interface ContentRefResolution {
  status: ContentRefStatus;
  id: string;
  type?: StableObjectType;
  href?: string;
  reason?: "reserved" | "missing" | "unsafe" | "not_an_id";
}

export function parseStableId(raw: string): { type: StableObjectType; id: string } | null {
  const id = raw.trim();
  if (KNOWLEDGE_ID.test(id)) {
    return { type: "knowledge", id };
  }
  if (PROBLEM_ID.test(id)) {
    return { type: "problem", id };
  }
  if (METHOD_ID.test(id)) {
    return { type: "method", id };
  }
  return null;
}

export function hrefForStableId(id: string): string | null {
  const parsed = parseStableId(id);
  if (!parsed) {
    return null;
  }
  if (parsed.type === "knowledge") {
    return `/knowledge/${id}`;
  }
  if (parsed.type === "problem") {
    return `/problems/${id}`;
  }
  return `/methods/${id}`;
}

/**
 * Conservative resolver for Frozen IDs only (K/P/M).
 * Research slugs are not rewritten from bare text.
 * When `catalog` is omitted, a well-formed ID is treated as ok (link shape only).
 * When `catalog` is provided, missing IDs are broken — never invented.
 */
export function resolveContentRef(
  raw: string,
  catalog?: ReadonlySet<string>,
): ContentRefResolution {
  const id = raw.trim();
  if (isUnsafeId(id)) {
    return { status: "broken", id, reason: "unsafe" };
  }
  if (isReservedId(id)) {
    return { status: "broken", id, reason: "reserved" };
  }
  const parsed = parseStableId(id);
  if (!parsed) {
    return { status: "ignore", id, reason: "not_an_id" };
  }
  if (catalog && !catalog.has(id)) {
    return { status: "broken", id, reason: "missing" };
  }
  return {
    status: "ok",
    id,
    type: parsed.type,
    href: hrefForStableId(id) ?? undefined,
  };
}

export function catalogFromIds(ids: Iterable<string>): Set<string> {
  return new Set(ids);
}
