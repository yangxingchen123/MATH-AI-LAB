import { parseDocument } from "yaml";

export type FrontMatterIssue =
  | "missing_delimiter"
  | "yaml_error"
  | "duplicate_key"
  | "not_mapping";

export interface FrontMatterResult {
  data: Record<string, unknown> | null;
  body: string;
  rawYaml: string | null;
  issues: FrontMatterIssue[];
}

const FRONT_MATTER = /^---\r?\n(.*?)(?:\r?\n---\r?\n|\r?\n---\s*$)/s;

export function extractFrontMatter(text: string): FrontMatterResult {
  if (!text.startsWith("---")) {
    return { data: null, body: text, rawYaml: null, issues: [] };
  }
  const match = FRONT_MATTER.exec(text);
  if (!match) {
    return {
      data: null,
      body: text,
      rawYaml: null,
      issues: ["missing_delimiter"],
    };
  }
  const rawYaml = match[1] ?? "";
  const body = text.slice(match[0].length);
  return { ...parseYamlMapping(rawYaml), body, rawYaml };
}

function parseYamlMapping(rawYaml: string): Pick<FrontMatterResult, "data" | "issues"> {
  const doc = parseDocument(rawYaml, { uniqueKeys: true });
  if (doc.errors.length > 0) {
    const duplicate = doc.errors.some((err) =>
      /duplicate|unique/i.test(err.message),
    );
    return {
      data: null,
      issues: [duplicate ? "duplicate_key" : "yaml_error"],
    };
  }
  const data = doc.toJSON() as unknown;
  if (data === null || data === undefined) {
    return { data: null, issues: ["not_mapping"] };
  }
  if (typeof data !== "object" || Array.isArray(data)) {
    return { data: null, issues: ["not_mapping"] };
  }
  return { data: data as Record<string, unknown>, issues: [] };
}

export function yamlScalarString(value: unknown): string | undefined {
  if (typeof value === "string") {
    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : undefined;
  }
  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    return value.toISOString().slice(0, 10);
  }
  return undefined;
}

export function yamlStringList(value: unknown): string[] | undefined {
  if (value === undefined) {
    return undefined;
  }
  if (!Array.isArray(value)) {
    return undefined;
  }
  const items: string[] = [];
  for (const item of value) {
    if (typeof item !== "string") {
      return undefined;
    }
    const trimmed = item.trim();
    if (!trimmed) {
      return undefined;
    }
    items.push(trimmed);
  }
  return items;
}

export function unknownFieldNames(
  data: Record<string, unknown>,
  allowlist: readonly string[],
): string[] {
  const allowed = new Set(allowlist);
  return Object.keys(data)
    .filter((key) => !allowed.has(key))
    .sort();
}
