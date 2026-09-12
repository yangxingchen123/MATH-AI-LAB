import { describe, expect, it } from "vitest";
import { extractFrontMatter } from "../src/front-matter.ts";
import { projectKnowledge, projectProblem } from "../src/project.ts";

describe("front matter", () => {
  it("splits YAML from the body", () => {
    const parsed = extractFrontMatter(
      "---\nschema_version: 1\nid: P0003\n---\n\n# Title\n",
    );
    expect(parsed.issues).toEqual([]);
    expect(parsed.data).toMatchObject({ schema_version: 1, id: "P0003" });
    expect(parsed.body).toBe("\n# Title\n");
  });

  it("reports a missing closing delimiter", () => {
    const parsed = extractFrontMatter("---\nid: P0003\n");
    expect(parsed.issues).toContain("missing_delimiter");
    expect(parsed.data).toBeNull();
  });

  it("reports duplicate keys", () => {
    const parsed = extractFrontMatter("---\nid: P0003\nid: P0004\n---\n");
    expect(parsed.issues).toContain("duplicate_key");
    expect(parsed.data).toBeNull();
  });

  it("skips reserved and invalid identities", () => {
    expect(
      projectProblem(
        {
          schema_version: 1,
          id: "P0000",
          type: "problem",
          title: "template",
          status: "draft",
        },
        "02_题目库/题目模板.md",
        "",
      ),
    ).toEqual({ skip: "reserved_id" });

    expect(
      projectKnowledge(
        {
          schema_version: 1,
          id: "K0001",
          type: "knowledge",
          title: "x",
          status: "published",
        },
        "01_知识库/x.md",
        "",
      ),
    ).toEqual({ skip: "invalid_identity" });
  });
});
