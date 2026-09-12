import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  KNOWLEDGE_FIELDS,
  METHOD_FIELDS,
  OBJECT_STATUSES,
  PROBLEM_FIELDS,
} from "@math-ai-lab/domain";
import { extractPythonStringSet } from "../src/python-fields.ts";
import { resolveRepoRoot } from "../src/root.ts";

function sorted(values: readonly string[]): string[] {
  return [...values].sort();
}

describe("TS allowlists track Python Core", () => {
  const root = resolveRepoRoot();

  it("matches Problem FROZEN_FIELDS", () => {
    const py = readFileSync(
      join(root, "tools/problem_validator/constants.py"),
      "utf8",
    );
    expect(sorted(PROBLEM_FIELDS)).toEqual(
      extractPythonStringSet(py, "FROZEN_FIELDS"),
    );
    expect(sorted(OBJECT_STATUSES)).toEqual(
      extractPythonStringSet(py, "ALLOWED_STATUSES"),
    );
  });

  it("matches Knowledge KNOWN_FIELDS", () => {
    const py = readFileSync(
      join(root, "tools/knowledge_validator/constants.py"),
      "utf8",
    );
    expect(sorted(KNOWLEDGE_FIELDS)).toEqual(
      extractPythonStringSet(py, "KNOWN_FIELDS"),
    );
    expect(sorted(OBJECT_STATUSES)).toEqual(
      extractPythonStringSet(py, "ALLOWED_STATUSES"),
    );
  });

  it("matches Method FROZEN_FIELDS", () => {
    const py = readFileSync(
      join(root, "tools/method_validator/constants.py"),
      "utf8",
    );
    expect(sorted(METHOD_FIELDS)).toEqual(
      extractPythonStringSet(py, "FROZEN_FIELDS"),
    );
    expect(sorted(OBJECT_STATUSES)).toEqual(
      extractPythonStringSet(py, "ALLOWED_STATUSES"),
    );
  });
});
