import type { UniverseSnapshot } from "@math-ai-lab/domain-math";
import { theoremCount } from "@math-ai-lab/domain-math";
import { fromCandidate, labStageFromNotes } from "./conjecture.ts";
import { createCounterexample } from "./counterexample.ts";
import { emptyExploration, type ExplorationState } from "./engine.ts";
import { createExperiment } from "./experiment.ts";
import { emptyFailureMemory, rememberFailure } from "./failure.ts";
import { createMemory } from "./memory.ts";
import { createNotebook, notebookIsCanonical } from "./notebook.ts";
import { createObservation } from "./observation.ts";
import { pipelineFromLabStage } from "./pipeline.ts";
import { patternIsTheorem, projectRecurringPatterns } from "./pattern.ts";
import { projectLemmaReasoning, reasoningProvesTheorem } from "./reasoning-graph.ts";
import { createSession, sessionConclusionIsTheorem } from "./session.ts";
import { emptyEvolutionGraph, addTheoryNode, evolutionProvesTheorem } from "./evolution.ts";
import { LexicalSimilarityEngine } from "./similarity.ts";

export interface BriefingItem {
  id: string;
  title: string;
  detail: string;
  state?: string;
  pipeline?: string;
}

export interface ExplorationAnswers {
  what_we_know: string;
  what_we_explore: string;
  why_we_believe: string;
  what_failed: string;
  what_is_next: string;
}

export interface ExplorationBriefing {
  layer: "exploration";
  writesCanonical: false;
  known: BriefingItem[];
  exploring: BriefingItem[];
  belief: BriefingItem[];
  failures: BriefingItem[];
  next: BriefingItem[];
  patterns: BriefingItem[];
  theoremCount: number;
  answers: ExplorationAnswers;
}

const HUMAN = { type: "Human" as const, id: "projection" };

export function projectExploration(snapshot: UniverseSnapshot): {
  state: ExplorationState;
  briefing: ExplorationBriefing;
} {
  const state = emptyExploration();
  state.conjectures = snapshot.candidates.map(fromCandidate);
  for (const candidate of snapshot.candidates) {
    const labStage = labStageFromNotes(candidate.notes) ?? "";
    state.pipelines.push(pipelineFromLabStage(`pipe:${candidate.id}`, labStage, candidate.id));
  }

  for (const entity of snapshot.entities) {
    if (entity.type !== "experiment") continue;
    const made = createExperiment({
      id: `experiment:${entity.id}`,
      hypothesis: entity.title,
      variables: [],
      method: "other",
      expectedOutcome: "unspecified (protocol projection only)",
      evidence: [],
    });
    if (made.ok) state.experiments.push(made.experiment);
  }

  for (const event of snapshot.events) {
    if (event.type !== "Observation") continue;
    const made = createObservation({
      id: `obs:${event.id}`,
      description: event.description,
      origin: event.actor === "lab" ? "lab" : "other",
      relatedEntities: [event.relatedEntity],
      evidence: [],
      researchContext: event.relatedEntity,
      timestamp: event.timestamp ?? "",
    });
    if (made.ok) state.observations.push(made.observation);
  }

  const byFamily = new Map<string, string[]>();
  for (const entity of snapshot.entities.filter((row) => row.type === "formal_proof")) {
    const prefix = entity.source.id.split("-")[0] ?? "";
    if (!/^[A-Z]+$/.test(prefix)) continue;
    const list = byFamily.get(prefix) ?? [];
    list.push(entity.id);
    byFamily.set(prefix, list);
  }
  const byOrigin = new Map<string, string[]>();
  for (const observation of state.observations) {
    const list = byOrigin.get(observation.origin) ?? [];
    list.push(observation.id);
    byOrigin.set(observation.origin, list);
  }
  state.patterns = projectRecurringPatterns([
    ...[...byFamily.entries()].map(([family, instances]) => ({
      id: `pattern:family:${family}`,
      pattern: `Correspondence IDs sharing prefix ${family}- recur as a calibration cluster. Not a theorem.`,
      kind: "repeated_relationship" as const,
      instances,
    })),
    ...[...byOrigin.entries()].map(([origin, instances]) => ({
      id: `pattern:origin:${origin}`,
      pattern: `Observations with origin=${origin} recur. Not a conjecture.`,
      kind: "repeated_relationship" as const,
      instances,
    })),
  ]);

  let failureMemory = emptyFailureMemory();
  for (const row of snapshot.evidence) {
    if (row.status !== "contradicting" && row.status !== "rejected") continue;
    const remembered = rememberFailure(failureMemory, {
      id: `fail:${row.id}`,
      failedAttempt: row.source,
      reason: `${row.evidenceType}:${row.status}`,
      lesson: "Contradicting or rejected evidence is retained. Not a theorem.",
      relatedFutureResearch: [row.claim],
    });
    if (remembered.ok) failureMemory = remembered.memory;
    const cex = createCounterexample({
      id: `cex:${row.id}`,
      claim: row.claim,
      counterexample: row.source,
      construction: "Projected from contradicting/rejected evidence.",
      whyFailure: row.status,
      lesson: `${row.evidenceType} does not support the claim`,
      futureDirection: "",
    });
    if (cex.ok) state.counterexamples.push(cex.record);
  }
  state.failures = failureMemory.records;

  const notebook = createNotebook({
    id: "notebook:projected",
    title: "Projected exploration notebook",
    observations: state.observations.map((row) => row.id),
    questions: snapshot.entities.filter((row) => row.type === "question").map((row) => row.id),
    ideas: snapshot.candidates.map((row) => row.id),
    experiments: state.experiments.map((row) => row.id),
    failures: state.failures.map((row) => row.id),
    results: snapshot.evidence.filter((row) => row.status === "supporting").map((row) => row.id),
  });
  if (notebook.ok) state.notebooks.push(notebook.notebook);

  const session = createSession({
    id: "session:projected",
    researcher: HUMAN,
    goal: "Read-only projection of current exploration. Not a new research claim.",
    inputs: snapshot.candidates.map((row) => row.id),
    outputs: snapshot.candidates.map((row) => row.id),
  });
  if (session.ok) state.sessions.push(session.session);

  let evolution = emptyEvolutionGraph();
  const seenModules = new Set<string>();
  for (const entity of snapshot.entities.filter((row) => row.type === "formal_proof")) {
    const file = entity.source.sourcePath?.replaceAll("\\", "/");
    if (!file?.endsWith(".lean") || seenModules.has(file)) continue;
    seenModules.add(file);
    const added = addTheoryNode(evolution, { id: `theory:${file}`, title: file });
    if (added.ok) evolution = added.graph;
  }
  if (evolution.nodes.length) state.evolution.push(evolution);

  const verified = snapshot.entities.filter((row) => row.status === "formal_verified").map((row) => row.id);
  const memory = createMemory({
    shortTerm: { sessionId: "session:projected", notebookId: notebook.ok ? notebook.notebook.id : undefined },
    longTerm: { verifiedEntityIds: verified },
    failure: { recordIds: state.failures.map((row) => row.id) },
  });
  if (memory.ok) state.memory = memory.memory;

  const leanEntities = snapshot.entities.filter((row) => row.type === "formal_proof");
  const leanIds = new Set(leanEntities.map((row) => row.id));
  state.reasoning.push(
    projectLemmaReasoning(
      leanEntities.map((entity) => ({
        id: entity.id,
        content: entity.title,
        dependsOn: snapshot.relations
          .filter((rel) => rel.type === "depends_on" && rel.source === entity.id && leanIds.has(rel.target))
          .map((rel) => rel.target),
      })),
    ),
  );

  const theorems = theoremCount(snapshot);
  const definitions = snapshot.entities.filter((row) => row.type === "definition").length;
  const questions = snapshot.entities.filter((row) => row.type === "question").length;
  const briefing: ExplorationBriefing = {
    layer: "exploration",
    writesCanonical: false,
    theoremCount: theorems,
    known: [
      {
        id: "known:definitions",
        title: "Canonical projections",
        detail: `${definitions} definitions, ${questions} questions, ${verified.length} formal-verified proofs. Theorem count from KM projection: ${theorems}.`,
      },
      {
        id: "known:reasoning",
        title: "Lemma reasoning graph",
        detail: `${state.reasoning[0]?.nodes.length ?? 0} nodes, ${state.reasoning[0]?.edges.length ?? 0} requires-edges, proves_theorem=${reasoningProvesTheorem(state.reasoning[0] ?? { nodes: [], edges: [] })}. File order is not a reasoning edge.`,
      },
      {
        id: "known:patterns",
        title: "Projected patterns",
        detail: `${state.patterns.length} recurring structures. Pattern ≠ theorem. confidence=heuristic.`,
      },
      {
        id: "known:notebook",
        title: "Projected notebook",
        detail: `canonical=${notebook.ok ? notebookIsCanonical(notebook.notebook) : false}. Exploration history only.`,
      },
      {
        id: "known:evolution",
        title: "Theory modules",
        detail: `${state.evolution[0]?.nodes.length ?? 0} Lean-path nodes, ${state.evolution[0]?.edges.length ?? 0} evolution edges, proves_theorem=${evolutionProvesTheorem(state.evolution[0] ?? { nodes: [], edges: [] })}.`,
      },
    ],
    exploring: state.conjectures.map((row) => {
      const candidate = snapshot.candidates.find((item) => item.id === row.candidateId);
      const pipe = state.pipelines.find((item) => item.candidateId === row.candidateId);
      return {
        id: row.id,
        title: candidate?.title ?? row.candidateId,
        detail: `lifecycle=${row.state} · pipeline=${pipe?.stage ?? "exploration"} · origin=${candidate?.origin ?? "unknown"} · not a theorem`,
        state: row.state,
        pipeline: pipe?.stage ?? "exploration",
      };
    }),
    belief: snapshot.evidence.map((row) => ({
      id: row.id,
      title: row.claim,
      detail: `${row.evidenceType} · ${row.status} · confidence=${row.confidence}`,
    })),
    failures: state.failures.map((row) => ({
      id: row.id,
      title: row.reason,
      detail: row.lesson,
    })),
    patterns: state.patterns.map((row) => ({
      id: row.id,
      title: row.pattern,
      detail: `kind=${row.kind} · instances=${row.instances.length} · confidence=${row.confidence} · theorem=${patternIsTheorem(row)}`,
    })),
    next: [
      ...snapshot.spaces
        .filter((row) => row.origin === "research_project" || row.origin === "unclassified")
        .map((row) => ({
          id: row.id,
          title: row.title,
          detail: `Frontier-facing space (${row.origin}). Not promoted.`,
        })),
      ...snapshot.candidates.map((row) => ({
        id: `next:${row.id}`,
        title: row.title,
        detail: "Candidate remains in Exploration until Human Review + Domain Operation.",
      })),
    ],
    answers: {
      what_we_know: `Canonical projections only: ${definitions} definitions, ${questions} questions, ${verified.length} formal-verified proofs, ${theorems} theorems invented from KM (must stay 0). Reasoning graph ${state.reasoning[0]?.nodes.length ?? 0} nodes / ${state.reasoning[0]?.edges.length ?? 0} edges, proves_theorem=false. Patterns ${state.patterns.length}, none are theorems. Notebook canonical=${notebook.ok ? notebookIsCanonical(notebook.notebook) : false}. Session conclusion is theorem=${session.ok ? sessionConclusionIsTheorem(session.session) : false}. Theory evolution edges=${state.evolution[0]?.edges.length ?? 0}.`,
      what_we_explore: `${state.conjectures.length} candidate lifecycles. None are theorems.`,
      why_we_believe: `${snapshot.evidence.length} evidence records; AI confidence is never mathematical truth.`,
      what_failed: `${state.failures.length} retained dead-ends from contradicting or rejected evidence.`,
      what_is_next: "Open candidates and research spaces. Promotion is not automatic.",
    },
  };

  const analogSeed = snapshot.entities[0];
  if (analogSeed) {
    const lexical = new LexicalSimilarityEngine(
      snapshot.entities.map((row) => ({ id: row.id, title: row.title })),
    );
    for (const candidate of lexical.findPotentialConnections(analogSeed.id).slice(0, 3)) {
      briefing.next.push({
        id: candidate.id,
        title: candidate.title,
        detail: candidate.notes ?? "Lexical candidate only.",
      });
    }
  }

  return { state, briefing };
}
