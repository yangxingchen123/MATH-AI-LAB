import { describe, expect, it } from "vitest";
import { projectProblem } from "../src/project.ts";

describe("unknown YAML keys", () => {
  it("does not promote difficulty/tags/research_status to Problem fields", () => {
    const result = projectProblem(
      {
        schema_version: 1,
        id: "P0099",
        type: "problem",
        title: "synthetic",
        status: "draft",
        created: "2026-01-01",
        updated: "2026-01-01",
        difficulty: "hard",
        tags: ["algebra"],
        research_status: "exploring",
      },
      "02_题目库/研究中/P0099.md",
      "body",
    );
    expect("object" in result).toBe(true);
    if (!("object" in result)) {
      return;
    }
    expect(result.object.unknownFields).toEqual([
      "difficulty",
      "research_status",
      "tags",
    ]);
    expect(result.object).not.toHaveProperty("difficulty");
    expect(result.object).not.toHaveProperty("tags");
    expect(result.object).not.toHaveProperty("research_status");
    expect(result.object.objectStatus).toBe("draft");
    expect(result.object.workflowDir).toBe("研究中");
  });
});
