/** UI-only projections. Not Frozen Schema objects. */

export type RelationOrigin = "explicit" | "derived";

export type LeanVerifyStatus =
  | "not_formalized"
  | "source_exists"
  | "checking"
  | "verified"
  | "failed";

export type HealthLevel = "healthy" | "warning" | "unavailable";

export interface RelatedRef {
  id: string;
  title: string;
  href: string;
  origin: RelationOrigin;
}

export interface KnowledgeRelationView {
  id: string;
  prerequisites: RelatedRef[];
  related: RelatedRef[];
  usedBy: RelatedRef[];
}

export interface ProblemRelationView {
  id: string;
  knowledge: RelatedRef[];
  methods: RelatedRef[];
  relatedProblems: RelatedRef[];
}

export type ReferenceKind = "book" | "paper" | "note" | "website" | "dataset" | "contest";

export interface ReferenceRecord {
  id: string;
  title: string;
  kind: ReferenceKind;
  sourcePath: string;
  authors?: string[];
  year?: string;
  venue?: string;
  domain?: string;
  doi?: string;
  arxiv?: string;
  url?: string;
  bibtex?: string;
  pdfPath?: string;
  relatedKnowledge: string[];
  relatedResearch: string[];
  notes?: string;
}

export interface OutputArtifact {
  id: string;
  title: string;
  kind: "pdf" | "latex" | "markdown" | "other";
  sourcePath: string;
  href: string;
  previewable: boolean;
}

export interface MemoryDocument {
  id: string;
  title: string;
  sourcePath: string;
  generated: boolean;
  role: "current" | "topics" | "research" | "goals" | "milestones" | "index" | "other";
  body: string;
}

export interface InboxItem {
  id: string;
  title: string;
  sourcePath: string;
  suggestion?: string;
  body: string;
}

export interface PromptDocument {
  id: string;
  title: string;
  category: string;
  sourcePath: string;
  body: string;
}

export interface LeanTheorem {
  id: string;
  title: string;
  leanDecl?: string;
  leanFile?: string;
  sourceExists: boolean;
  status: LeanVerifyStatus;
  evidencePath?: string;
  logSummary?: string;
  family?: string;
}

export interface LabRecord {
  id: string;
  title: string;
  kind: "problem" | "conjecture" | "task" | "literature" | "expert";
  sourcePath: string;
  stage?: string;
  novelty?: string;
  leanDecls: string[];
  candidate: true;
  notes?: string;
}

export interface DiagnosticItem {
  type:
    | "broken_ref"
    | "parse_error"
    | "unknown_field"
    | "missing_artifact"
    | "reserved_id"
    | "duplicate_id"
    | "unsafe_path";
  sourcePath?: string;
  target?: string;
  explanation: string;
}

export interface TimelineEvent {
  id: string;
  label: string;
  at?: string;
  origin: RelationOrigin;
  href?: string;
}

export interface EvidenceItem {
  kind: "source" | "reproduction" | "experiment" | "proof" | "formalization" | "artifact";
  label: string;
  sourcePath?: string;
  origin: RelationOrigin;
}

export interface ExplorerEntry {
  name: string;
  path: string;
  kind: "dir" | "file";
}

export interface ExplorerListing {
  path: string;
  entries: ExplorerEntry[];
}

export interface ExplorerFile {
  path: string;
  language: string;
  text?: string;
  binary?: boolean;
  previewKind?: "text" | "pdf" | "unsupported";
}
