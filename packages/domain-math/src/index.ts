export {
  MATH_ENTITY_TYPES,
  MATH_ENTITY_STATUSES,
  MATH_SOURCE_KINDS,
  entityId,
  parseEntityId,
  createMathematicalEntity,
} from "./entity.ts";
export type { MathEntityType, MathEntityStatus, MathSourceKind, MathEntitySource, MathematicalEntity } from "./entity.ts";
export { MATH_RELATION_TYPES, RELATION_EVIDENCE_KINDS, relationId, validateRelation } from "./relation.ts";
export type { MathRelationType, RelationEvidenceKind, RelationEvidence, MathematicalRelation } from "./relation.ts";
export { EVIDENCE_TYPES, EVIDENCE_STATUSES, EVIDENCE_CONFIDENCE, isMathematicalTruth } from "./evidence.ts";
export type { EvidenceType, EvidenceStatus, EvidenceConfidence, EvidenceRecord } from "./evidence.ts";
export {
  CANDIDATE_STATUSES,
  canTransition,
  transitionCandidate,
  promoteToCanonical,
} from "./candidate.ts";
export type { CandidateStatus, Candidate } from "./candidate.ts";
export { RESEARCH_EVENT_TYPES } from "./event.ts";
export type { ResearchEventType, ResearchActor, ResearchEvent } from "./event.ts";
export type { ResearchSpace } from "./space.ts";
export { relatedIds, dependencyIds, historyOf } from "./graph.ts";
export type { MathGraph } from "./graph.ts";
export { MockAIResearchProvider } from "./ai.ts";
export type { AIResearchProvider, AISuggestion } from "./ai.ts";
export { projectUniverse, theoremCount, provesCount } from "./project.ts";
export type { AttemptLike, LeanBinding, UniverseInput, UniverseSnapshot } from "./project.ts";
