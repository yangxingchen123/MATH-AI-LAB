import type {
  Knowledge,
  LabRecord,
  LeanTheorem,
  Method,
  OutputArtifact,
  Problem,
  ReferenceRecord,
  ResearchProject,
} from "@math-ai-lab/domain";
import type { Candidate } from "./candidate.ts";
import type { EvidenceRecord } from "./evidence.ts";
import { entityId, type MathematicalEntity } from "./entity.ts";
import type { ResearchEvent } from "./event.ts";
import { relationId, validateRelation, type MathematicalRelation } from "./relation.ts";
import type { ResearchSpace } from "./space.ts";

export interface AttemptLike {
  id: string;
  problem: string;
  part?: string;
  outcome: string;
  assistance: string;
  attemptedAt?: string;
}

export interface LeanBinding {
  sourceId: string;
  sourceKind: "knowledge" | "problem" | "method";
  lean: LeanTheorem;
}

export interface UniverseInput {
  knowledge: Knowledge[];
  problems: Problem[];
  methods: Method[];
  attempts?: AttemptLike[];
  lean?: LeanTheorem[];
  leanBindings?: LeanBinding[];
  lab?: LabRecord[];
  outputs?: OutputArtifact[];
  research?: ResearchProject[];
  references?: ReferenceRecord[];
}

export interface UniverseSnapshot {
  entities: MathematicalEntity[];
  relations: MathematicalRelation[];
  evidence: EvidenceRecord[];
  candidates: Candidate[];
  events: ResearchEvent[];
  spaces: ResearchSpace[];
}

function definitionOf(item: Knowledge): MathematicalEntity {
  return {
    id: entityId("definition", "knowledge", item.id),
    title: item.title,
    type: "definition",
    description: item.domain ? `Knowledge projection · domain ${item.domain}` : "Knowledge projection. Not a Theorem.",
    source: { kind: "knowledge", id: item.id, href: `/knowledge/${item.id}`, sourcePath: item.sourcePath },
    status: "projected",
    created: item.createdAt,
    updated: item.updatedAt,
  };
}

function questionOf(item: Problem): MathematicalEntity {
  return {
    id: entityId("question", "problem", item.id),
    title: item.title,
    type: "question",
    description: `Problem projection · workflowDir=${item.workflowDir ?? "其他"} · objectStatus=${item.objectStatus}`,
    source: { kind: "problem", id: item.id, href: `/problems/${item.id}`, sourcePath: item.sourcePath },
    status: "projected",
    created: item.createdAt,
    updated: item.updatedAt,
  };
}

function objectOf(item: Method): MathematicalEntity {
  return {
    id: entityId("object", "method", item.id),
    title: item.title,
    type: "object",
    description: "Method projection (reusable procedure). Not a set-theoretic object declaration.",
    source: { kind: "method", id: item.id, href: `/methods/${item.id}`, sourcePath: item.sourcePath },
    status: "projected",
  };
}

function formalOf(item: LeanTheorem): MathematicalEntity {
  const verified = item.status === "verified";
  return {
    id: entityId("formal_proof", "lean", item.id),
    title: item.title,
    type: "formal_proof",
    description: item.logSummary ?? "Lean correspondence projection.",
    source: {
      kind: "lean",
      id: item.id,
      href: `/lean/${item.id}`,
      sourcePath: item.evidencePath ?? item.leanFile,
    },
    status: verified ? "formal_verified" : "projected",
  };
}

function labEntity(item: LabRecord): MathematicalEntity {
  const type = item.kind === "conjecture" ? "conjecture" : "experiment";
  return {
    id: entityId(type, "lab", item.id),
    title: item.title,
    type,
    description: item.stage
      ? `Research Lab Candidate · kind=${item.kind} · stage=${item.stage}. Not Source.`
      : `Research Lab Candidate · kind=${item.kind}. Not Source.`,
    source: { kind: "lab", id: item.id, href: "/lab", sourcePath: item.sourcePath },
    status: "candidate",
  };
}

function artifactOf(item: OutputArtifact): MathematicalEntity {
  return {
    id: entityId("artifact", "output", item.id),
    title: item.title,
    type: "artifact",
    description: `Output file · ${item.kind}`,
    source: { kind: "output", id: item.id, href: item.href, sourcePath: item.sourcePath },
    status: "projected",
  };
}

function evidenceForAttempt(attempt: AttemptLike, questionId: string): EvidenceRecord {
  const supporting = attempt.outcome === "correct";
  const contradicting = attempt.outcome === "incorrect";
  return {
    id: `evidence:attempt:${attempt.id}`,
    claim: questionId,
    evidenceType: "HumanProof",
    source: `11_学习证据/尝试记录/${attempt.problem}.md`,
    status: supporting ? "supporting" : contradicting ? "contradicting" : "unverified",
    confidence: "human_claimed",
  };
}

function evidenceForLean(item: LeanTheorem, claim: string): EvidenceRecord {
  const verified = item.status === "verified";
  return {
    id: `evidence:lean:${item.id}`,
    claim,
    evidenceType: "LeanProof",
    source: item.evidencePath ?? item.leanFile ?? `06_LEAN形式化/correspondence.yaml#${item.id}`,
    status: verified ? "supporting" : item.status === "failed" ? "contradicting" : "unverified",
    confidence: verified ? "machine_checked" : "none",
  };
}

export function projectUniverse(input: UniverseInput): UniverseSnapshot {
  const knowledgeById = new Map(input.knowledge.map((row) => [row.id, row]));
  const entities: MathematicalEntity[] = [
    ...input.knowledge.map(definitionOf),
    ...input.problems.map(questionOf),
    ...input.methods.map(objectOf),
    ...(input.lean ?? []).map(formalOf),
    ...(input.lab ?? []).map(labEntity),
    ...(input.outputs ?? []).map(artifactOf),
  ];
  const entityIndex = new Map(entities.map((row) => [row.id, row]));
  const questionId = (pid: string) => entityId("question", "problem", pid);
  const definitionId = (kid: string) => entityId("definition", "knowledge", kid);
  const objectId = (mid: string) => entityId("object", "method", mid);
  const formalId = (lid: string) => entityId("formal_proof", "lean", lid);

  const relations: MathematicalRelation[] = [];
  const push = (rel: MathematicalRelation) => {
    if (!entityIndex.has(rel.source) || !entityIndex.has(rel.target)) return;
    relations.push(rel);
  };

  for (const item of input.knowledge) {
    const src = definitionId(item.id);
    for (const kid of item.prerequisites ?? []) {
      if (!knowledgeById.has(kid)) continue;
      const target = definitionId(kid);
      push({
        id: relationId("depends_on", src, target),
        type: "depends_on",
        source: src,
        target,
        origin: "explicit",
        evidence: { kind: "explicit_field", sourcePath: item.sourcePath, note: "prerequisites" },
      });
      push({
        id: relationId("derived_from", target, src),
        type: "derived_from",
        source: target,
        target: src,
        origin: "derived",
        evidence: { kind: "derived_reverse", note: "reverse of depends_on" },
      });
    }
  }

  for (const item of input.problems) {
    const src = questionId(item.id);
    for (const kid of item.knowledge ?? []) {
      if (!knowledgeById.has(kid)) continue;
      const target = definitionId(kid);
      push({
        id: relationId("uses", src, target),
        type: "uses",
        source: src,
        target,
        origin: "explicit",
        evidence: { kind: "explicit_field", sourcePath: item.sourcePath, note: "knowledge" },
      });
      push({
        id: relationId("derived_from", target, src),
        type: "derived_from",
        source: target,
        target: src,
        origin: "derived",
        evidence: { kind: "derived_reverse", note: "reverse of uses" },
      });
    }
  }

  for (const item of input.methods) {
    const src = objectId(item.id);
    for (const kid of item.knowledge ?? []) {
      if (!knowledgeById.has(kid)) continue;
      const target = definitionId(kid);
      push({
        id: relationId("uses", src, target),
        type: "uses",
        source: src,
        target,
        origin: "explicit",
        evidence: { kind: "explicit_field", sourcePath: item.sourcePath, note: "knowledge" },
      });
    }
  }

  for (const binding of input.leanBindings ?? []) {
    if (binding.lean.status !== "verified") continue;
    const source =
      binding.sourceKind === "problem"
        ? questionId(binding.sourceId)
        : binding.sourceKind === "knowledge"
          ? definitionId(binding.sourceId)
          : objectId(binding.sourceId);
    const target = formalId(binding.lean.id);
    push({
      id: relationId("verified_by", source, target),
      type: "verified_by",
      source,
      target,
      origin: "derived",
      evidence: {
        kind: "lean_manifest",
        sourcePath: binding.lean.evidencePath,
        note: "Lean Verified requires manifest SUCCEEDED",
      },
    });
  }

  const evidence: EvidenceRecord[] = [];
  const events: ResearchEvent[] = [];

  for (const attempt of input.attempts ?? []) {
    const qid = questionId(attempt.problem);
    if (!entityIndex.has(qid)) continue;
    evidence.push(evidenceForAttempt(attempt, qid));
    events.push({
      id: `event:attempt:${attempt.id}`,
      type: "ProofAttempt",
      timestamp: attempt.attemptedAt,
      actor: "human",
      relatedEntity: qid,
      description: `${attempt.id} outcome=${attempt.outcome}`,
    });
  }

  for (const item of input.lean ?? []) {
    const fid = formalId(item.id);
    evidence.push(evidenceForLean(item, fid));
    if (item.status === "verified") {
      events.push({
        id: `event:lean:${item.id}`,
        type: "FormalVerified",
        actor: "system",
        relatedEntity: fid,
        description: item.logSummary ?? "manifest SUCCEEDED",
      });
    }
  }

  const candidates: Candidate[] = (input.lab ?? []).map((item) => ({
    id: `candidate:lab:${item.id}`,
    title: item.title,
    proposedType: item.kind === "conjecture" ? "conjecture" : "experiment",
    status: "exploring",
    origin: "lab",
    sourcePath: item.sourcePath,
    notes: item.stage
      ? `Research Lab Candidate. Not Source. lab_stage=${item.stage}`
      : "Research Lab Candidate. Not Source.",
  }));

  for (const item of input.lab ?? []) {
    const eid = entityId(item.kind === "conjecture" ? "conjecture" : "experiment", "lab", item.id);
    events.push({
      id: `event:lab:${item.id}`,
      type: item.kind === "conjecture" ? "ConjectureCreated" : "ExperimentRun",
      actor: "lab",
      relatedEntity: eid,
      description: `Lab ${item.kind} ${item.id}`,
    });
  }

  for (const item of input.references ?? []) {
    evidence.push({
      id: `evidence:literature:${item.id}`,
      claim: item.id,
      evidenceType: "Literature",
      source: item.sourcePath,
      status: "unverified",
      confidence: "none",
    });
  }

  const spaces: ResearchSpace[] = [];
  const byDomain = new Map<string, string[]>();
  for (const item of input.knowledge) {
    const key = item.domain?.trim() || "";
    const list = byDomain.get(key) ?? [];
    list.push(definitionId(item.id));
    byDomain.set(key, list);
  }
  for (const [domain, ids] of [...byDomain.entries()].sort((a, b) => a[0].localeCompare(b[0], "zh"))) {
    spaces.push({
      id: domain ? `space:domain:${domain}` : "space:unclassified",
      title: domain || "Unclassified",
      origin: domain ? "knowledge_domain" : "unclassified",
      entityIds: ids.sort(),
    });
  }
  for (const project of input.research ?? []) {
    spaces.push({
      id: `space:research:${project.slug}`,
      title: project.title,
      origin: "research_project",
      entityIds: [],
    });
  }

  const knownIds = new Set(entityIndex.keys());
  const cleanedRelations = relations.filter((rel) => validateRelation(rel, knownIds).ok);
  entities.sort((a, b) => a.id.localeCompare(b.id));
  cleanedRelations.sort((a, b) => a.id.localeCompare(b.id));
  evidence.sort((a, b) => a.id.localeCompare(b.id));
  candidates.sort((a, b) => a.id.localeCompare(b.id));
  events.sort((a, b) => (a.timestamp ?? "").localeCompare(b.timestamp ?? "") || a.id.localeCompare(b.id));

  return {
    entities,
    relations: cleanedRelations,
    evidence,
    candidates,
    events,
    spaces,
  };
}

/** Attempt.correct must never yield a Theorem or proves relation. */
export function theoremCount(snapshot: UniverseSnapshot): number {
  return snapshot.entities.filter((row) => row.type === "theorem").length;
}

export function provesCount(snapshot: UniverseSnapshot): number {
  return snapshot.relations.filter((row) => row.type === "proves").length;
}
