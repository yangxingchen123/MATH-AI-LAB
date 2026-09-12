import { readFileSync } from "node:fs";
import { join } from "node:path";
import {
  isUnsafeId,
  type DiagnosticItem,
  type EvidenceItem,
  type ExplorerFile,
  type ExplorerListing,
  type InboxItem,
  type Knowledge,
  type KnowledgeRelationView,
  type LabRecord,
  type LeanTheorem,
  type MemoryDocument,
  type Method,
  type OutputArtifact,
  type Problem,
  type ProblemRelationView,
  type PromptDocument,
  type ReferenceRecord,
  type ResearchProject,
  type TimelineEvent,
} from "@math-ai-lab/domain";
import { readAttemptLedger, type AttemptRecord } from "./attempts.ts";
import { collectDiagnostics } from "./diagnostics.ts";
import { listExplorer, readExplorerFile } from "./explorer.ts";
import { extractFrontMatter } from "./front-matter.ts";
import { listInbox } from "./inbox.ts";
import { listLabRecords } from "./lab.ts";
import { getLeanTheorem, leanForStableId, listLeanTheorems } from "./lean.ts";
import { getMemory, listMemory } from "./memory.ts";
import { getOutput, listOutputs } from "./outputs.ts";
import { splitProblemBody, type ProblemBodyView } from "./parts.ts";
import { getPrompt, listPrompts } from "./prompts.ts";
import {
  projectKnowledge,
  projectMethod,
  projectProblem,
  type SkipReason,
} from "./project.ts";
import { getReference, listReferences } from "./references.ts";
import { knowledgeRelationsOf, problemRelationsOf } from "./relations.ts";
import { getResearchProject, listResearchProjects } from "./research.ts";
import { researchEvidenceOf, researchTimelineOf } from "./research-view.ts";
import { resolveRepoRoot } from "./root.ts";
import {
  isExcludedKnowledge,
  isExcludedProblem,
  listMarkdown,
  toPosix,
} from "./scan.ts";

export interface ScanSkip {
  sourcePath: string;
  reason: SkipReason | "excluded" | FrontMatterSkip;
}

type FrontMatterSkip = "missing_front_matter" | "parse_error";

export interface ContentRepository {
  readonly writes: false;
  readonly repoRoot: string;
  listKnowledge(): Knowledge[];
  listProblems(): Problem[];
  listMethods(): Method[];
  getKnowledge(id: string): Knowledge | null;
  getProblem(id: string): Problem | null;
  getMethod(id: string): Method | null;
  problemView(id: string): ProblemBodyView | null;
  listAttempts(problemId: string): AttemptRecord[];
  listResearch(): ResearchProject[];
  getResearch(slug: string): ResearchProject | null;
  listReferences(): ReferenceRecord[];
  getReference(id: string): ReferenceRecord | null;
  listOutputs(): OutputArtifact[];
  getOutput(id: string): OutputArtifact | null;
  listMemory(): MemoryDocument[];
  getMemory(id: string): MemoryDocument | null;
  listInbox(): InboxItem[];
  listPrompts(): PromptDocument[];
  getPrompt(id: string): PromptDocument | null;
  listLean(): LeanTheorem[];
  getLean(id: string): LeanTheorem | null;
  leanFor(stableId: string): LeanTheorem[];
  listLab(): LabRecord[];
  listDiagnostics(): DiagnosticItem[];
  knowledgeRelations(id: string): KnowledgeRelationView | null;
  problemRelations(id: string): ProblemRelationView | null;
  researchTimeline(slug: string): TimelineEvent[];
  researchEvidence(slug: string): EvidenceItem[];
  knownIds(): Set<string>;
  listExplorer(relPath?: string): ExplorerListing | null;
  readExplorerFile(relPath: string): ExplorerFile | null;
  skips(): readonly ScanSkip[];
}

class FileContentRepository implements ContentRepository {
  readonly writes = false as const;

  constructor(
    readonly repoRoot: string,
    private readonly knowledge: Knowledge[],
    private readonly problems: Problem[],
    private readonly methods: Method[],
    private readonly skipped: ScanSkip[],
  ) {}

  listKnowledge(): Knowledge[] {
    return this.knowledge.slice();
  }

  listProblems(): Problem[] {
    return this.problems.slice();
  }

  listMethods(): Method[] {
    return this.methods.slice();
  }

  getKnowledge(id: string): Knowledge | null {
    return lookup(this.knowledge, id);
  }

  getProblem(id: string): Problem | null {
    return lookup(this.problems, id);
  }

  getMethod(id: string): Method | null {
    return lookup(this.methods, id);
  }

  problemView(id: string): ProblemBodyView | null {
    const problem = this.getProblem(id);
    if (!problem) {
      return null;
    }
    return splitProblemBody(problem.body, problem.parts);
  }

  listAttempts(problemId: string): AttemptRecord[] {
    return readAttemptLedger(this.repoRoot, problemId);
  }

  listResearch(): ResearchProject[] {
    return listResearchProjects(this.repoRoot);
  }

  getResearch(slug: string): ResearchProject | null {
    return getResearchProject(this.repoRoot, slug);
  }

  listReferences(): ReferenceRecord[] {
    return listReferences(this.repoRoot);
  }

  getReference(id: string): ReferenceRecord | null {
    return getReference(this.repoRoot, id);
  }

  listOutputs(): OutputArtifact[] {
    return listOutputs(this.repoRoot);
  }

  getOutput(id: string): OutputArtifact | null {
    return getOutput(this.repoRoot, id);
  }

  listMemory(): MemoryDocument[] {
    return listMemory(this.repoRoot);
  }

  getMemory(id: string): MemoryDocument | null {
    return getMemory(this.repoRoot, id);
  }

  listInbox(): InboxItem[] {
    return listInbox(this.repoRoot);
  }

  listPrompts(): PromptDocument[] {
    return listPrompts(this.repoRoot);
  }

  getPrompt(id: string): PromptDocument | null {
    return getPrompt(this.repoRoot, id);
  }

  listLean(): LeanTheorem[] {
    return listLeanTheorems(this.repoRoot);
  }

  getLean(id: string): LeanTheorem | null {
    return getLeanTheorem(this.repoRoot, id);
  }

  leanFor(stableId: string): LeanTheorem[] {
    return leanForStableId(this.repoRoot, stableId);
  }

  listLab(): LabRecord[] {
    return listLabRecords(this.repoRoot);
  }

  listDiagnostics(): DiagnosticItem[] {
    return collectDiagnostics({
      repoRoot: this.repoRoot,
      knowledge: this.knowledge,
      problems: this.problems,
      methods: this.methods,
      skips: this.skipped,
    });
  }

  knowledgeRelations(id: string): KnowledgeRelationView | null {
    return knowledgeRelationsOf(this.knowledge, this.problems, this.methods, id);
  }

  problemRelations(id: string): ProblemRelationView | null {
    return problemRelationsOf(this.knowledge, this.problems, this.methods, id);
  }

  researchTimeline(slug: string): TimelineEvent[] {
    const project = this.getResearch(slug);
    return project ? researchTimelineOf(this.repoRoot, project) : [];
  }

  researchEvidence(slug: string): EvidenceItem[] {
    const project = this.getResearch(slug);
    return project ? researchEvidenceOf(project) : [];
  }

  knownIds(): Set<string> {
    return new Set([
      ...this.knowledge.map((row) => row.id),
      ...this.problems.map((row) => row.id),
      ...this.methods.map((row) => row.id),
    ]);
  }

  listExplorer(relPath = ""): ExplorerListing | null {
    return listExplorer(this.repoRoot, relPath);
  }

  readExplorerFile(relPath: string): ExplorerFile | null {
    return readExplorerFile(this.repoRoot, relPath);
  }

  skips(): readonly ScanSkip[] {
    return this.skipped;
  }
}

function lookup<T extends { id: string }>(items: T[], id: string): T | null {
  if (isUnsafeId(id)) {
    return null;
  }
  return items.find((item) => item.id === id) ?? null;
}

export function createRepository(explicitRoot?: string): ContentRepository {
  const repoRoot = resolveRepoRoot(explicitRoot);
  const skipped: ScanSkip[] = [];
  const knowledge: Knowledge[] = [];
  const problems: Problem[] = [];
  const methods: Method[] = [];

  for (const abs of listMarkdown(join(repoRoot, "01_知识库"))) {
    const sourcePath = toPosix(repoRoot, abs);
    if (isExcludedKnowledge(sourcePath)) {
      skipped.push({ sourcePath, reason: "excluded" });
      continue;
    }
    const projected = readAndProject(abs, sourcePath, projectKnowledge);
    if ("skip" in projected) {
      skipped.push({ sourcePath, reason: projected.skip });
    } else {
      knowledge.push(projected.object);
    }
  }

  for (const abs of listMarkdown(join(repoRoot, "02_题目库"))) {
    const sourcePath = toPosix(repoRoot, abs);
    if (isExcludedProblem(sourcePath)) {
      skipped.push({ sourcePath, reason: "excluded" });
      continue;
    }
    const projected = readAndProject(abs, sourcePath, projectProblem);
    if ("skip" in projected) {
      skipped.push({ sourcePath, reason: projected.skip });
    } else {
      problems.push(projected.object);
    }
  }

  for (const abs of listMarkdown(join(repoRoot, "12_方法库"))) {
    const sourcePath = toPosix(repoRoot, abs);
    const projected = readAndProject(abs, sourcePath, projectMethod);
    if ("skip" in projected) {
      skipped.push({ sourcePath, reason: projected.skip });
    } else {
      methods.push(projected.object);
    }
  }

  knowledge.sort((a, b) => a.id.localeCompare(b.id));
  problems.sort((a, b) => a.id.localeCompare(b.id));
  methods.sort((a, b) => a.id.localeCompare(b.id));

  return new FileContentRepository(
    repoRoot,
    knowledge,
    problems,
    methods,
    skipped,
  );
}

function readAndProject<T>(
  absPath: string,
  sourcePath: string,
  project: (
    data: Record<string, unknown>,
    sourcePath: string,
    body: string,
  ) => { object: T } | { skip: SkipReason },
): { object: T } | { skip: SkipReason | FrontMatterSkip } {
  const text = readFileSync(absPath, "utf8");
  const parsed = extractFrontMatter(text);
  if (parsed.issues.length > 0 || parsed.data === null) {
    return {
      skip: parsed.rawYaml === null && parsed.issues.length === 0
        ? "missing_front_matter"
        : "parse_error",
    };
  }
  return project(parsed.data, sourcePath, parsed.body);
}
