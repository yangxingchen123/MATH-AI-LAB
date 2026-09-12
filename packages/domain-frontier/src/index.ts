export { FRONTIER_LAYER, UNKNOWN_REGION_STATUSES, createUnknownRegion } from "./region.ts";
export type { UnknownRegionStatus, UnknownRegion } from "./region.ts";
export {
  RESEARCH_DIRECTION_STATUSES,
  createResearchDirection,
  createOpenQuestion,
} from "./direction.ts";
export type { ResearchDirectionStatus, ResearchDirection, OpenQuestion } from "./direction.ts";
export { projectFrontier } from "./project.ts";
export {
  loadErdosIndex,
  projectErdosFrontier,
  catalogErdosFrontier,
  questionIsTheorem,
  erdosPrompt,
  erdosTitle,
} from "./erdos.ts";
export type { ErdősQuestionRecord, ErdősFrontierIndex, FrontierCatalogItem } from "./erdos.ts";
