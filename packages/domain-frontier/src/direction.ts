/** Frontier Layer: research direction. Not a conjecture, not a theorem. */

export const RESEARCH_DIRECTION_STATUSES = ["open", "active", "paused", "abandoned"] as const;

export type ResearchDirectionStatus = (typeof RESEARCH_DIRECTION_STATUSES)[number];

export interface ResearchDirection {
  id: string;
  title: string;
  regionId: string;
  motivation: string;
  status: ResearchDirectionStatus;
}

export interface OpenQuestion {
  id: string;
  prompt: string;
  regionId: string;
  relatedEntityIds: string[];
}

export function createResearchDirection(
  input: ResearchDirection,
): { ok: true; direction: ResearchDirection } | { ok: false; error: string } {
  if (!input.id?.trim() || !input.title?.trim() || !input.regionId?.trim() || !input.motivation?.trim()) {
    return { ok: false, error: "ResearchDirection requires id, title, regionId, and motivation." };
  }
  if (!RESEARCH_DIRECTION_STATUSES.includes(input.status)) {
    return { ok: false, error: "Unknown ResearchDirection status." };
  }
  return { ok: true, direction: input };
}

export function createOpenQuestion(
  input: OpenQuestion,
): { ok: true; question: OpenQuestion } | { ok: false; error: string } {
  if (!input.id?.trim() || !input.prompt?.trim() || !input.regionId?.trim()) {
    return { ok: false, error: "OpenQuestion requires id, prompt, and regionId." };
  }
  return { ok: true, question: input };
}
