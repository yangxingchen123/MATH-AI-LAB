import { describe, expect, it } from "vitest";
import {
  knowledgeMappingLabel,
  knowledgeMappingOf,
  isReservedId,
  isUnsafeId,
  OBJECT_STATUSES,
  PROBLEM_FIELDS,
  METHOD_FIELDS,
  KNOWLEDGE_FIELDS,
  DOMAIN_OPERATIONS,
  OPERATION_CONTRACT_VERSION,
  isDomainOperation,
} from "../src/index.ts";

describe("knowledge mapping projection", () => {
  it("treats omitted knowledge as draft-optional, not unknown", () => {
    const mapping = knowledgeMappingOf(undefined);
    expect(mapping).toEqual({ state: "omitted" });
    expect(knowledgeMappingLabel(mapping)).toContain("可省略");
  });

  it("treats empty list as mapping complete", () => {
    const mapping = knowledgeMappingOf([]);
    expect(mapping).toEqual({ state: "complete_empty" });
    expect(knowledgeMappingLabel(mapping)).toBe(
      "mapping 已完成，当前没有直接对象",
    );
  });

  it("keeps mapped ids", () => {
    expect(knowledgeMappingOf(["K0001", "K0002"])).toEqual({
      state: "mapped",
      ids: ["K0001", "K0002"],
    });
  });
});

describe("identity guards", () => {
  it("reserves sentinel IDs", () => {
    expect(isReservedId("P0000")).toBe(true);
    expect(isReservedId("K0000")).toBe(true);
    expect(isReservedId("M0000")).toBe(true);
    expect(isReservedId("P0001")).toBe(false);
  });

  it("rejects path-like IDs", () => {
    expect(isUnsafeId("../P0001")).toBe(true);
    expect(isUnsafeId("P0002/a")).toBe(true);
    expect(isUnsafeId("P0002")).toBe(false);
  });
});

describe("Frozen allowlists (TS copy; Python is authority)", () => {
  it("uses only draft/reviewed/archived for object status", () => {
    expect([...OBJECT_STATUSES]).toEqual(["draft", "reviewed", "archived"]);
  });

  it("does not put difficulty or tags on Problem fields", () => {
    expect(PROBLEM_FIELDS).not.toContain("difficulty");
    expect(PROBLEM_FIELDS).not.toContain("tags");
    expect(PROBLEM_FIELDS).not.toContain("research_status");
  });

  it("does not invent Method created/updated", () => {
    expect(METHOD_FIELDS).not.toContain("created");
    expect(METHOD_FIELDS).not.toContain("updated");
  });

  it("keeps Knowledge relation fields optional in the allowlist", () => {
    expect(KNOWLEDGE_FIELDS).toContain("prerequisites");
    expect(KNOWLEDGE_FIELDS).toContain("related");
    expect(KNOWLEDGE_FIELDS).not.toContain("tags");
  });
});

describe("operation contract v1", () => {
  it("whitelists workbench writes including body update", () => {
    expect(OPERATION_CONTRACT_VERSION).toBe(1);
    expect([...DOMAIN_OPERATIONS]).toEqual([
      "RecordAttempt",
      "MoveProblemWorkflow",
      "CreateProblem",
      "CreateKnowledge",
      "CreateMethod",
      "PromoteInboxItem",
      "UpdateMarkdownBody",
    ]);
    expect(isDomainOperation("UpdateMarkdownBody")).toBe(true);
    expect(isDomainOperation("DeleteFile")).toBe(false);
  });
});
