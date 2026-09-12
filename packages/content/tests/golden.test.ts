import { describe, expect, it } from "vitest";
import { knowledgeMappingLabel } from "@math-ai-lab/domain";
import { createRepository } from "../src/index.ts";

describe("golden objects from the real repo", () => {
  const repo = createRepository();

  it("is read-only", () => {
    expect(repo.writes).toBe(false);
    expect(repo).not.toHaveProperty("writeProblem");
    expect(repo).not.toHaveProperty("writeKnowledge");
    expect(repo).not.toHaveProperty("writeMethod");
  });

  it("lists the six golden IDs and no sentinels", () => {
    expect(repo.listKnowledge().map((row) => row.id)).toEqual(["K0001", "K0002"]);
    expect(repo.listProblems().map((row) => row.id)).toEqual(["P0001", "P0002"]);
    expect(repo.listMethods().map((row) => row.id)).toEqual(["M0001", "M0002"]);
    expect(repo.getProblem("P0000")).toBeNull();
    expect(repo.getKnowledge("K0000")).toBeNull();
    expect(repo.getMethod("M0000")).toBeNull();
  });

  it("skips templates and generated knowledge index", () => {
    const skipped = repo.skips().map((row) => row.sourcePath);
    expect(skipped).toContain("02_题目库/题目模板.md");
    expect(skipped).toContain("01_知识库/知识库模板.md");
    expect(skipped.some((path) => path.startsWith("01_知识库/_索引/"))).toBe(
      true,
    );
  });

  it("projects P0001 from YAML id, not the P001 filename", () => {
    const problem = repo.getProblem("P0001");
    expect(problem).not.toBeNull();
    expect(problem?.title).toBe("为什么勒让德变换这样定义");
    expect(problem?.objectStatus).toBe("reviewed");
    expect(problem?.workflowDir).toBe("已解决");
    expect(problem?.knowledge).toEqual(["K0001", "K0002"]);
    expect(problem?.parts).toBeUndefined();
    expect(problem?.sourcePath).toBe(
      "02_题目库/已解决/P001_为什么勒让德变换这样定义.md",
    );
    expect(problem?.body.startsWith("---")).toBe(false);
    expect(problem?.unknownFields).toEqual([]);
  });

  it("keeps P0002 empty knowledge as mapping-complete, with parts", () => {
    const problem = repo.getProblem("P0002");
    expect(problem?.objectStatus).toBe("reviewed");
    expect(problem?.workflowDir).toBe("已解决");
    expect(problem?.knowledge).toEqual([]);
    expect(problem?.knowledgeMapping).toEqual({ state: "complete_empty" });
    expect(knowledgeMappingLabel(problem!.knowledgeMapping)).toBe(
      "mapping 已完成，当前没有直接对象",
    );
    expect(problem?.parts).toEqual(["a", "b", "c"]);
    expect(problem?.objectStatus).not.toBe(problem?.workflowDir);
  });

  it("projects K0001 / K0002 Frozen fields", () => {
    const k1 = repo.getKnowledge("K0001");
    const k2 = repo.getKnowledge("K0002");
    expect(k1?.title).toBe("勒让德变换");
    expect(k1?.objectStatus).toBe("reviewed");
    expect(k1?.domain).toBe("凸分析");
    expect(k1?.aliases).toEqual(["Legendre transform"]);
    expect(k1?.prerequisites).toEqual(["K0002"]);
    expect(k1?.related).toEqual([]);
    expect(k2?.title).toBe("凸函数");
    expect(k2?.prerequisites).toEqual([]);
    expect(k2?.related).toEqual([]);
    expect(k1?.unknownFields).toEqual([]);
    expect(k2?.unknownFields).toEqual([]);
  });

  it("projects Method without inventing created/updated", () => {
    const m1 = repo.getMethod("M0001");
    const m2 = repo.getMethod("M0002");
    expect(m1?.title).toBe("经典 Legendre 反解代回");
    expect(m1?.objectStatus).toBe("draft");
    expect(m1?.knowledge).toEqual(["K0001"]);
    expect(m1?.createdAt).toBeUndefined();
    expect(m1?.updatedAt).toBeUndefined();
    expect(m2?.title).toBe("左右特征结构的秩一对象构造");
    expect(m2?.knowledge).toBeUndefined();
    expect(m2?.unknownFields).toEqual([]);
  });

  it("never treats an ID as a filesystem path", () => {
    expect(repo.getProblem("../P0001")).toBeNull();
    expect(repo.getProblem("P0002/a")).toBeNull();
    expect(repo.getProblem("已解决/P0002")).toBeNull();
    expect(repo.getProblem("P0002")?.id).toBe("P0002");
  });
});
