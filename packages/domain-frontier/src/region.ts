/** Frontier Layer: unknown region. Not a Universe entity, not exploration process. */

export const FRONTIER_LAYER = "frontier" as const;

export const UNKNOWN_REGION_STATUSES = ["open", "narrowed", "paused", "abandoned"] as const;

export type UnknownRegionStatus = (typeof UNKNOWN_REGION_STATUSES)[number];

export interface UnknownRegion {
  id: string;
  title: string;
  description: string;
  relatedEntityIds: string[];
  openQuestionIds: string[];
  directionIds: string[];
  status: UnknownRegionStatus;
}

export function createUnknownRegion(
  input: UnknownRegion,
): { ok: true; region: UnknownRegion } | { ok: false; error: string } {
  if (!input.id?.trim() || !input.title?.trim() || !input.description?.trim()) {
    return { ok: false, error: "UnknownRegion requires id, title, and description." };
  }
  if (!UNKNOWN_REGION_STATUSES.includes(input.status)) {
    return { ok: false, error: "Unknown UnknownRegion status." };
  }
  return { ok: true, region: input };
}
