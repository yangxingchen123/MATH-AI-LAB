export const RESEARCH_EVENT_TYPES = [
  "Idea",
  "Observation",
  "ConjectureCreated",
  "ExperimentRun",
  "CounterexampleFound",
  "ProofAttempt",
  "ProofCompleted",
  "FormalVerified",
] as const;

export type ResearchEventType = (typeof RESEARCH_EVENT_TYPES)[number];

export type ResearchActor = "human" | "system" | "lab" | "ai_mock";

export interface ResearchEvent {
  id: string;
  type: ResearchEventType;
  timestamp?: string;
  actor: ResearchActor;
  relatedEntity: string;
  description: string;
}
