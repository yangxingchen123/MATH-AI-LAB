/** Frontier projection from Universe spaces. ID references only; no entity merge. */

import { createUnknownRegion, type UnknownRegion } from "./region.ts";
import { createResearchDirection, type ResearchDirection } from "./direction.ts";

export interface SpaceLike {
  id: string;
  title: string;
  origin: string;
  entityIds: string[];
}

export function projectFrontier(spaces: SpaceLike[]): {
  regions: UnknownRegion[];
  directions: ResearchDirection[];
} {
  const regions: UnknownRegion[] = [];
  const directions: ResearchDirection[] = [];
  for (const space of spaces) {
    if (space.origin !== "research_project" && space.origin !== "unclassified") continue;
    const regionId = `region:${space.id}`;
    const directionId = `dir:${space.id}`;
    const region = createUnknownRegion({
      id: regionId,
      title: space.title,
      description: `Unknown or project region from ${space.origin}. Not a Universe entity.`,
      relatedEntityIds: space.entityIds,
      openQuestionIds: [],
      directionIds: [directionId],
      status: "open",
    });
    if (region.ok) regions.push(region.region);
    const direction = createResearchDirection({
      id: directionId,
      title: `Explore ${space.title}`,
      regionId,
      motivation: "Projected from a research space. Candidate direction only.",
      status: "open",
    });
    if (direction.ok) directions.push(direction.direction);
  }
  return { regions, directions };
}
