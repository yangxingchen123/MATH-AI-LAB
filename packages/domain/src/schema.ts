/**
 * Frozen field allowlists copied from Python Core constants.
 * Not a new Schema. If these drift, tests fail and this file must change
 * to match Python — never the other way around.
 *
 * Sources:
 * - tools/knowledge_validator/constants.py → KNOWN_FIELDS
 * - tools/problem_validator/constants.py → FROZEN_FIELDS
 * - tools/method_validator/constants.py → FROZEN_FIELDS
 */

export const OBJECT_STATUSES = ["draft", "reviewed", "archived"] as const;
export type ObjectStatus = (typeof OBJECT_STATUSES)[number];

export const WORKFLOW_DIRS = ["未解决", "研究中", "已解决"] as const;
export type WorkflowDir = (typeof WORKFLOW_DIRS)[number];

export const RESERVED_IDS = ["K0000", "P0000", "M0000"] as const;

export const KNOWLEDGE_FIELDS = [
  "schema_version",
  "id",
  "type",
  "title",
  "aliases",
  "status",
  "created",
  "updated",
  "domain",
  "prerequisites",
  "related",
] as const;

export const PROBLEM_FIELDS = [
  "schema_version",
  "id",
  "type",
  "title",
  "status",
  "created",
  "updated",
  "knowledge",
  "parts",
] as const;

/** Method v1 has no created/updated. */
export const METHOD_FIELDS = [
  "schema_version",
  "id",
  "type",
  "title",
  "status",
  "knowledge",
] as const;

export const CONTENT_TYPES = [
  "knowledge",
  "problem",
  "method",
  "research_project",
] as const;

export type ContentType = (typeof CONTENT_TYPES)[number];

export const RESEARCH_PROJECT_KINDS = [
  "research",
  "literature",
  "contest_modeling",
] as const;

export type ResearchProjectKind = (typeof RESEARCH_PROJECT_KINDS)[number];

export const KNOWLEDGE_ID = /^K\d{4}$/;
export const PROBLEM_ID = /^P\d{4}$/;
export const METHOD_ID = /^M\d{4}$/;
