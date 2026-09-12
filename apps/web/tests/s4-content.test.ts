import { describe, expect, it } from "vitest";
import { createRepository } from "@math-ai-lab/content";
import { allNavItems } from "../features/shell/nav";

describe("S4 knowledge and methods", () => {
  const repo = createRepository();

  it("exposes knowledge and methods in the shell", () => {
    expect(allNavItems().find((item) => item.id === "knowledge")?.phase).toBe("ready");
    expect(allNavItems().find((item) => item.id === "methods")?.phase).toBe("ready");
    expect(allNavItems().find((item) => item.id === "references")?.phase).toBe("ready");
    expect(allNavItems().find((item) => item.id === "lean")?.phase).toBe("ready");
  });

  it("loads golden knowledge without templates", () => {
    expect(repo.listKnowledge().map((row) => row.id)).toEqual(["K0001", "K0002"]);
    expect(repo.getKnowledge("K0000")).toBeNull();
    expect(repo.getKnowledge("K0001")?.body.startsWith("---")).toBe(false);
    expect(repo.getKnowledge("K0001")?.domain).toBe("凸分析");
    expect(repo.getKnowledge("K0002")?.prerequisites).toEqual([]);
  });

  it("loads golden methods with Frozen Method fields only", () => {
    expect(repo.listMethods().map((row) => row.id)).toEqual(["M0001", "M0002"]);
    expect(repo.getMethod("M0001")?.createdAt).toBeUndefined();
    expect(repo.getMethod("M0002")?.knowledge).toBeUndefined();
  });
});
