import type {
  ContentType,
  ObjectStatus,
  ResearchProjectKind,
  WorkflowDir,
} from "./schema.ts";

export type {
  ContentType,
  ObjectStatus,
  ResearchProjectKind,
  WorkflowDir,
} from "./schema.ts";

/** Shared UI projection. Not Frozen Schema. */
export interface ContentRef {
  id: string;
  title: string;
  type: ContentType;
  objectStatus: ObjectStatus;
  sourcePath: string;
  createdAt?: string;
  updatedAt?: string;
}

export type KnowledgeMapping =
  | { state: "omitted" }
  | { state: "complete_empty" }
  | { state: "mapped"; ids: string[] };

export interface Knowledge extends ContentRef {
  type: "knowledge";
  domain?: string;
  aliases?: string[];
  prerequisites?: string[];
  related?: string[];
  body: string;
  unknownFields: string[];
}

export interface Problem extends ContentRef {
  type: "problem";
  workflowDir: WorkflowDir | null;
  parts?: string[];
  knowledge?: string[];
  knowledgeMapping: KnowledgeMapping;
  body: string;
  unknownFields: string[];
}

export interface Method extends ContentRef {
  type: "method";
  knowledge?: string[];
  body: string;
  unknownFields: string[];
}

export interface ResearchSection {
  id: string;
  title: string;
  sourcePath: string;
  body: string;
}

/**
 * Dossier-level project. Never a Problem, never a new R000x YAML type.
 * objectStatus is omitted: dossiers are not Frozen K/P/M objects.
 */
export interface ResearchProject {
  type: "research_project";
  id: string;
  slug: string;
  title: string;
  kind: ResearchProjectKind;
  sourcePath: string;
  sections: ResearchSection[];
}

export function isReservedId(id: string): boolean {
  return id === "K0000" || id === "P0000" || id === "M0000";
}

export function isUnsafeId(id: string): boolean {
  return id.length === 0 || /[\\/]/.test(id) || id.includes("..");
}
