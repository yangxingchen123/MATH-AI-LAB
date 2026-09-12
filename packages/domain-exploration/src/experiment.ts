/**
 * Experiment abstraction. Not a computation engine.
 * Future: symbolic / numerical / counterexample search / automated exploration.
 */

export const EXPERIMENT_METHODS = [
  "symbolic",
  "numerical",
  "counterexample_search",
  "automated_exploration",
  "other",
] as const;

export type ExperimentMethod = (typeof EXPERIMENT_METHODS)[number];

export interface ExperimentProtocol {
  id: string;
  hypothesis: string;
  variables: string[];
  method: ExperimentMethod;
  expectedOutcome: string;
  actualOutcome?: string;
  interpretation?: string;
  evidence: string[];
}

export function createExperiment(
  input: ExperimentProtocol,
): { ok: true; experiment: ExperimentProtocol } | { ok: false; error: string } {
  if (!input.id?.trim() || !input.hypothesis?.trim()) {
    return { ok: false, error: "ExperimentProtocol requires id and hypothesis." };
  }
  if (!EXPERIMENT_METHODS.includes(input.method)) {
    return { ok: false, error: "Unknown experiment method." };
  }
  if (!input.expectedOutcome?.trim()) {
    return { ok: false, error: "ExperimentProtocol requires expectedOutcome." };
  }
  return { ok: true, experiment: input };
}

export function recordOutcome(
  experiment: ExperimentProtocol,
  actualOutcome: string,
  interpretation: string,
): ExperimentProtocol {
  return { ...experiment, actualOutcome, interpretation };
}
