import {
  KNOWLEDGE_FIELDS,
  KNOWLEDGE_ID,
  METHOD_FIELDS,
  METHOD_ID,
  OBJECT_STATUSES,
  PROBLEM_FIELDS,
  PROBLEM_ID,
  isReservedId,
  knowledgeMappingOf,
  type Knowledge,
  type Method,
  type ObjectStatus,
  type Problem,
} from "@math-ai-lab/domain";
import {
  unknownFieldNames,
  yamlScalarString,
  yamlStringList,
} from "./front-matter.ts";
import { workflowDirOf } from "./scan.ts";

export type SkipReason =
  | "reserved_id"
  | "invalid_identity"
  | "wrong_type"
  | "parse_error";

function asStatus(value: unknown): ObjectStatus | undefined {
  return typeof value === "string" &&
    (OBJECT_STATUSES as readonly string[]).includes(value)
    ? (value as ObjectStatus)
    : undefined;
}

function asSchemaVersion(value: unknown): number | undefined {
  if (typeof value === "boolean") {
    return undefined;
  }
  return typeof value === "number" && value === 1 ? 1 : undefined;
}

function identity(
  data: Record<string, unknown>,
  type: "knowledge" | "problem" | "method",
  idPattern: RegExp,
): { id: string; title: string; objectStatus: ObjectStatus } | null {
  if (data.type !== type) {
    return null;
  }
  if (asSchemaVersion(data.schema_version) !== 1) {
    return null;
  }
  const id = yamlScalarString(data.id);
  const title = yamlScalarString(data.title);
  const objectStatus = asStatus(data.status);
  if (!id || !title || !objectStatus || !idPattern.test(id)) {
    return null;
  }
  return { id, title, objectStatus };
}

export function projectKnowledge(
  data: Record<string, unknown>,
  sourcePath: string,
  body: string,
): { object: Knowledge } | { skip: SkipReason } {
  const base = identity(data, "knowledge", KNOWLEDGE_ID);
  if (!base) {
    return { skip: data.type && data.type !== "knowledge" ? "wrong_type" : "invalid_identity" };
  }
  if (isReservedId(base.id)) {
    return { skip: "reserved_id" };
  }
  return {
    object: {
      ...base,
      type: "knowledge",
      sourcePath,
      createdAt: yamlScalarString(data.created),
      updatedAt: yamlScalarString(data.updated),
      domain: yamlScalarString(data.domain),
      aliases: yamlStringList(data.aliases),
      prerequisites: yamlStringList(data.prerequisites),
      related: yamlStringList(data.related),
      body,
      unknownFields: unknownFieldNames(data, KNOWLEDGE_FIELDS),
    },
  };
}

export function projectProblem(
  data: Record<string, unknown>,
  sourcePath: string,
  body: string,
): { object: Problem } | { skip: SkipReason } {
  const base = identity(data, "problem", PROBLEM_ID);
  if (!base) {
    return { skip: data.type && data.type !== "problem" ? "wrong_type" : "invalid_identity" };
  }
  if (isReservedId(base.id)) {
    return { skip: "reserved_id" };
  }
  const knowledge = Object.prototype.hasOwnProperty.call(data, "knowledge")
    ? yamlStringList(data.knowledge)
    : undefined;
  return {
    object: {
      ...base,
      type: "problem",
      sourcePath,
      createdAt: yamlScalarString(data.created),
      updatedAt: yamlScalarString(data.updated),
      workflowDir: workflowDirOf(sourcePath),
      parts: yamlStringList(data.parts),
      knowledge,
      knowledgeMapping: knowledgeMappingOf(knowledge),
      body,
      unknownFields: unknownFieldNames(data, PROBLEM_FIELDS),
    },
  };
}

export function projectMethod(
  data: Record<string, unknown>,
  sourcePath: string,
  body: string,
): { object: Method } | { skip: SkipReason } {
  const base = identity(data, "method", METHOD_ID);
  if (!base) {
    return { skip: data.type && data.type !== "method" ? "wrong_type" : "invalid_identity" };
  }
  if (isReservedId(base.id)) {
    return { skip: "reserved_id" };
  }
  const knowledgePresent = Object.prototype.hasOwnProperty.call(data, "knowledge");
  return {
    object: {
      ...base,
      type: "method",
      sourcePath,
      knowledge: knowledgePresent ? yamlStringList(data.knowledge) : undefined,
      body,
      unknownFields: unknownFieldNames(data, METHOD_FIELDS),
    },
  };
}
