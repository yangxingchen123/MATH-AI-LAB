import { createHash } from "node:crypto";
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  createRepository,
  getSearchProvider,
  resolveSafeRel,
} from "../src/index.ts";

describe("Phase 2/3A projections", () => {
  const repo = createRepository();

  it("maps the real MCM identity without inventing authors", () => {
    const items = repo.listReferences();
    expect(items.map((row) => row.id)).toContain("2026-A");
    const item = repo.getReference("2026-A");
    expect(item?.title).toContain("2026");
    expect(item?.kind).toBe("contest");
    expect(item?.authors).toBeUndefined();
    expect(item?.pdfPath).toBe("03_参考资料/竞赛/美赛/2026-A/source.pdf");
    expect(item?.relatedResearch).toContain("美赛2026-A");
    expect(repo.getReference("../x")).toBeNull();
  });

  it("treats an empty outputs tree as empty, not fake artifacts", () => {
    expect(Array.isArray(repo.listOutputs())).toBe(true);
  });

  it("marks generated memory as read-only generated", () => {
    const memory = repo.listMemory();
    expect(memory.some((row) => row.role === "current")).toBe(true);
    expect(memory.filter((row) => row.generated).every((row) => row.sourcePath.includes("自动索引"))).toBe(
      true,
    );
  });

  it("lists inbox and prompts without writing", () => {
    expect(repo.listInbox().length).toBeGreaterThan(0);
    expect(repo.listPrompts().some((row) => row.id.includes("Research"))).toBe(true);
    expect(repo.getPrompt("../x")).toBeNull();
  });

  it("computes knowledge reverse relations as derived", () => {
    const k1 = repo.knowledgeRelations("K0001");
    expect(k1?.prerequisites[0]?.id).toBe("K0002");
    expect(k1?.prerequisites[0]?.origin).toBe("explicit");
    expect(k1?.usedBy.some((row) => row.id === "P0001" && row.origin === "derived")).toBe(
      true,
    );
    const p1 = repo.problemRelations("P0001");
    expect(p1?.knowledge.map((row) => row.id)).toEqual(["K0001", "K0002"]);
    expect(p1?.methods.some((row) => row.id === "M0001" && row.origin === "derived")).toBe(
      true,
    );
    const p2 = repo.problemRelations("P0002");
    expect(p2?.knowledge).toEqual([]);
    expect(p2?.relatedProblems).toEqual([]);
  });

  it("maps Lean Verified only from manifest SUCCEEDED", () => {
    const alg = repo.getLean("ALG-001");
    expect(alg?.sourceExists).toBe(true);
    expect(alg?.status).toBe("verified");
    expect(alg?.evidencePath).toContain("manifests/ALG-001.yaml");
    expect(repo.listLean().every((row) => row.status !== "verified" || row.evidencePath)).toBe(
      true,
    );
  });

  it("keeps Research Lab records as Candidate", () => {
    const lab = repo.listLab();
    expect(lab.some((row) => row.id === "PROB-SF-001")).toBe(true);
    expect(lab.every((row) => row.candidate === true)).toBe(true);
  });

  it("lists diagnostics without mutating content", () => {
    expect(Array.isArray(repo.listDiagnostics())).toBe(true);
  });

  it("weights exact IDs above body text in search v2", () => {
    const search = getSearchProvider(repo);
    expect(search.search("P0002")[0]?.id).toBe("P0002");
    expect(search.search("勒让德")[0]?.id).toBe("K0001");
    expect(search.search("P0002", { type: "knowledge" })).toEqual([]);
    expect(search.search("勒让德", { domain: "凸分析" })[0]?.id).toBe("K0001");
    expect(search.search("美赛")[0]?.type).toBe("research_project");
  });

  it("refuses explorer path traversal", () => {
    expect(resolveSafeRel(repo.repoRoot, "../README.md")).toBeNull();
    expect(resolveSafeRel(repo.repoRoot, "node_modules/x")).toBeNull();
    expect(repo.listExplorer("01_知识库")).not.toBeNull();
    expect(repo.readExplorerFile("../../etc/passwd")).toBeNull();
  });
});

describe("content immutability", () => {
  it("does not modify canonical directories while projecting", () => {
    const root = createRepository().repoRoot;
    const before = hashCanonical(root);
    const repo = createRepository();
    repo.listDiagnostics();
    getSearchProvider(repo).search("K0001");
    repo.listReferences();
    repo.listLean();
    expect(hashCanonical(root)).toBe(before);
  });
});

function hashCanonical(root: string): string {
  const dirs = ["01_知识库", "02_题目库", "07_项目", "12_方法库"];
  const hash = createHash("sha256");
  for (const dir of dirs) {
    walk(join(root, dir), hash);
  }
  return hash.digest("hex");
}

function walk(dir: string, hash: ReturnType<typeof createHash>): void {
  if (!existsSync(dir)) return;
  for (const entry of readdirSync(dir, { withFileTypes: true }).sort((a, b) =>
    a.name.localeCompare(b.name),
  )) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full, hash);
    } else if (entry.isFile()) {
      const stat = statSync(full);
      hash.update(full);
      hash.update(String(stat.size));
      hash.update(readFileSync(full));
    }
  }
}
