import type { ResearchAssessment } from "./assessment.ts";
import type { ConjectureLifecycle } from "./conjecture.ts";
import type { CounterexampleRecord } from "./counterexample.ts";
import type { ExperimentProtocol } from "./experiment.ts";
import type { FailureRecord } from "./failure.ts";
import type { MathematicalMemory } from "./memory.ts";
import type { ResearchNotebook } from "./notebook.ts";
import type { MathematicalObservation } from "./observation.ts";
import type { MathematicalPattern } from "./pattern.ts";
import type { DiscoveryPipeline } from "./pipeline.ts";
import type { ProofStrategy } from "./proof-strategy.ts";
import type { MathematicalReasoningGraph } from "./reasoning-graph.ts";
import type { ResearchSession } from "./session.ts";
import type { TheoryEvolutionGraph } from "./evolution.ts";

/** In-memory exploration substrate. Does not project from or write to Canonical. */

export interface ExplorationState {
  observations: MathematicalObservation[];
  patterns: MathematicalPattern[];
  conjectures: ConjectureLifecycle[];
  experiments: ExperimentProtocol[];
  counterexamples: CounterexampleRecord[];
  failures: FailureRecord[];
  strategies: ProofStrategy[];
  notebooks: ResearchNotebook[];
  sessions: ResearchSession[];
  pipelines: DiscoveryPipeline[];
  assessments: ResearchAssessment[];
  reasoning: MathematicalReasoningGraph[];
  evolution: TheoryEvolutionGraph[];
  memory?: MathematicalMemory;
}

export function emptyExploration(): ExplorationState {
  return {
    observations: [],
    patterns: [],
    conjectures: [],
    experiments: [],
    counterexamples: [],
    failures: [],
    strategies: [],
    notebooks: [],
    sessions: [],
    pipelines: [],
    assessments: [],
    reasoning: [],
    evolution: [],
  };
}
