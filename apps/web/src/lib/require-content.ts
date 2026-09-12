import { notFound } from "next/navigation";
import { isReservedId, isUnsafeId } from "@math-ai-lab/domain";

export function requireObject<T>(item: T | null | undefined): T {
  if (item == null) {
    notFound();
  }
  return item;
}

export function rejectBadId(id: string): void {
  if (isReservedId(id) || isUnsafeId(id)) {
    notFound();
  }
}
