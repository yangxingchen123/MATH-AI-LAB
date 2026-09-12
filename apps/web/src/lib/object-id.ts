import { isReservedId, isUnsafeId } from "@math-ai-lab/domain";

const OBJECT_ID = /^(K|P|M)\d{4}$/;
const CREATE_SEGMENTS = new Set(["new"]);

export function isMissingObjectId(id: string): boolean {
  return isReservedId(id) || isUnsafeId(id) || !OBJECT_ID.test(id);
}

export function isCreateSegment(id: string): boolean {
  return CREATE_SEGMENTS.has(id);
}

export function shouldProbeObject(pathname: string): {
  kind: "knowledge" | "problems" | "methods" | "research";
  id: string;
} | null {
  if (pathname.includes("..")) {
    return null;
  }
  const parts = pathname.split("/").filter(Boolean);
  if (parts.length !== 2) {
    return null;
  }
  const [kind, raw] = parts;
  let id = raw;
  try {
    id = decodeURIComponent(raw);
  } catch {
    return null;
  }
  if (isCreateSegment(id)) {
    return null;
  }
  if (kind === "knowledge" || kind === "problems" || kind === "methods") {
    if (isMissingObjectId(id)) return null;
    return { kind, id };
  }
  if (kind === "research") {
    if (isUnsafeId(id) || id === "_模板") return null;
    return { kind, id };
  }
  return null;
}

export function pathNeedsHttp404(pathname: string): boolean {
  if (pathname.includes("..")) {
    return true;
  }
  const parts = pathname.split("/").filter(Boolean);
  if (parts.length !== 2) {
    return false;
  }
  const [kind, raw] = parts;
  let id = raw;
  try {
    id = decodeURIComponent(raw);
  } catch {
    return true;
  }
  if (isCreateSegment(id)) {
    return false;
  }
  if (kind === "knowledge" || kind === "problems" || kind === "methods") {
    return isMissingObjectId(id);
  }
  if (kind === "research") {
    return isUnsafeId(id) || id === "_模板";
  }
  return false;
}
