export {
  CANONICAL_LAYER,
  UNIVERSE_LAYER,
  FRONTIER_LAYER,
  EXPLORATION_LAYER,
  MATHEMATICAL_LAYERS,
} from "./layers.ts";
export type { MathematicalLayer } from "./layers.ts";
export { ACTOR_TYPES, createActor, isHuman, isAI, isFormalSystem } from "./actor.ts";
export type { ActorType, ResearchActor, AttributedAction } from "./actor.ts";
export { OBSERVATION_ORIGINS, createObservation, observationKind } from "./observation.ts";
export type { ObservationOrigin, MathematicalObservation } from "./observation.ts";
export { PATTERN_KINDS, PATTERN_CONFIDENCE, createPattern, patternIsTheorem, projectRecurringPatterns } from "./pattern.ts";
export type { PatternKind, PatternConfidence, MathematicalPattern } from "./pattern.ts";
export {
  CONJECTURE_STATES,
  canTransitionConjecture,
  lifecycleFromLabStage,
  labStageFromNotes,
  fromCandidate,
  conjectureIsTheorem,
  transitionConjecture,
} from "./conjecture.ts";
export type { ConjectureState, LifecycleEvent, ConjectureLifecycle } from "./conjecture.ts";
export { EXPERIMENT_METHODS, createExperiment, recordOutcome } from "./experiment.ts";
export type { ExperimentMethod, ExperimentProtocol } from "./experiment.ts";
export { createCounterexample } from "./counterexample.ts";
export type { CounterexampleRecord } from "./counterexample.ts";
export { emptyFailureMemory, rememberFailure, lookupFailures } from "./failure.ts";
export type { FailureRecord, FailureMemorySystem } from "./failure.ts";
export {
  NAMED_PROOF_STRATEGIES,
  createProofStrategy,
  strategyIsProof,
  scanNamedProofStrategies,
} from "./proof-strategy.ts";
export type { NamedProofStrategy, ProofStrategy } from "./proof-strategy.ts";
export {
  REASONING_NODE_KINDS,
  REASONING_EDGE_TYPES,
  emptyReasoningGraph,
  addReasoningNode,
  addReasoningEdge,
  reasoningProvesTheorem,
  projectLemmaReasoning,
} from "./reasoning-graph.ts";
export type {
  ReasoningNodeKind,
  ReasoningEdgeType,
  ReasoningNode,
  ReasoningEdge,
  MathematicalReasoningGraph,
  LemmaDecl,
} from "./reasoning-graph.ts";
export {
  isSafeExplorationId,
  lookupExploration,
  catalogExploration,
  searchExplorationCatalog,
} from "./catalog.ts";
export type { ExplorationCatalogItem } from "./catalog.ts";
export { NullSimilarityEngine, LexicalSimilarityEngine } from "./similarity.ts";
export type { MathematicalSimilarityEngine, TitledItem } from "./similarity.ts";
export { createNotebook, notebookIsCanonical } from "./notebook.ts";
export type { ResearchNotebook } from "./notebook.ts";
export { createSession, recordSessionAction, concludeSession, sessionConclusionIsTheorem } from "./session.ts";
export type { SessionAction, ResearchSession } from "./session.ts";
export { createMemory } from "./memory.ts";
export type { MathematicalMemory } from "./memory.ts";
export { SEARCH_HIT_KINDS, NullSearchProvider, LexicalSearchProvider } from "./search.ts";
export type { SearchHitKind, SearchHit, MathematicalSearchProvider, SearchCatalog } from "./search.ts";
export { EVOLUTION_RELATIONS, emptyEvolutionGraph, addTheoryNode, addTheoryEdge, evolutionProvesTheorem } from "./evolution.ts";
export type { EvolutionRelation, TheoryNode, TheoryEdge, TheoryEvolutionGraph } from "./evolution.ts";
export { FORMAL_STATUSES, recordAssessment } from "./assessment.ts";
export type { FormalStatus, ResearchAssessment } from "./assessment.ts";
export type {
  ExplorerAgent,
  ProofAgent,
  CriticAgent,
  ExperimentAgent,
  FormalizationAgent,
  ExplorationAgents,
} from "./agents.ts";
export {
  PIPELINE_STAGES,
  createPipeline,
  pipelineStageFromLab,
  pipelineFromLabStage,
  markHumanReview,
  markEvidenceEvaluation,
  markFormalVerification,
  advancePipeline,
} from "./pipeline.ts";
export type { PipelineStage, PipelineStep, DiscoveryPipeline, FormalVerificationStatus } from "./pipeline.ts";
export { requestPromotion, executeCanonicalWrite } from "./promotion.ts";
export type { PromotionRequest, PromotionDecision } from "./promotion.ts";
export { emptyExploration } from "./engine.ts";
export type { ExplorationState } from "./engine.ts";
export { projectExploration } from "./project.ts";
export type { BriefingItem, ExplorationAnswers, ExplorationBriefing } from "./project.ts";
