import type { Candidate } from "@math-ai-lab/domain-math";

/**
 * Future multi-agent preparation. Interfaces only. No implementation.
 * Every agent output is a Candidate, never a theorem.
 */

export interface ExplorerAgent {
  explore(observationId: string): Candidate;
}

export interface ProofAgent {
  attemptProof(claimId: string): Candidate;
}

export interface CriticAgent {
  critique(targetId: string): Candidate;
}

export interface ExperimentAgent {
  designExperiment(hypothesisId: string): Candidate;
}

export interface FormalizationAgent {
  proposeFormalization(claimId: string): Candidate;
}

export interface ExplorationAgents {
  explorer?: ExplorerAgent;
  proof?: ProofAgent;
  critic?: CriticAgent;
  experiment?: ExperimentAgent;
  formalization?: FormalizationAgent;
}
