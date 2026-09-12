import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";
import type { HealthLevel } from "@math-ai-lab/domain";
import { getSearchProvider } from "@math-ai-lab/content";
import { getRepository } from "./repo";
import { operationHealth } from "./python-bridge";
import pkg from "../../package.json";

export interface HealthRow {
  id: string;
  label: string;
  level: HealthLevel;
  detail: string;
}

function pythonProbe(): { level: HealthLevel; detail: string } {
  const result = spawnSync("python", ["-c", "import sys; print(sys.version.split()[0])"], {
    encoding: "utf8",
    timeout: 8000,
  });
  if (result.status === 0 && result.stdout.trim()) {
    return { level: "healthy", detail: result.stdout.trim() };
  }
  const py = spawnSync("py", ["-3", "-c", "import sys; print(sys.version.split()[0])"], {
    encoding: "utf8",
    timeout: 8000,
  });
  if (py.status === 0 && py.stdout.trim()) {
    return { level: "healthy", detail: py.stdout.trim() };
  }
  return { level: "unavailable", detail: "本机未检测到 python / py" };
}

function moduleProbe(moduleName: string): HealthLevel {
  const result = spawnSync(
    "python",
    ["-c", `import ${moduleName}`],
    { encoding: "utf8", timeout: 8000 },
  );
  if (result.status === 0) return "healthy";
  const py = spawnSync("py", ["-3", "-c", `import ${moduleName}`], {
    encoding: "utf8",
    timeout: 8000,
  });
  return py.status === 0 ? "healthy" : "unavailable";
}

export function collectHealth(): HealthRow[] {
  const repo = getRepository();
  const python = pythonProbe();
  const ops = operationHealth();
  const search = getSearchProvider(repo);
  const lean = repo.listLean();
  const verified = lean.filter((item) => item.status === "verified").length;
  const failed = lean.filter((item) => item.status === "failed").length;
  const rows: HealthRow[] = [
    {
      id: "adapter",
      label: "Content Adapter",
      level: "healthy",
      detail: `K${repo.listKnowledge().length} P${repo.listProblems().length} M${repo.listMethods().length}`,
    },
    {
      id: "problem-validator",
      label: "Problem Validator",
      level: python.level === "unavailable" ? "unavailable" : moduleProbe("tools.problem_validator"),
      detail: "import tools.problem_validator",
    },
    {
      id: "knowledge-validator",
      label: "Knowledge Validator",
      level: python.level === "unavailable" ? "unavailable" : moduleProbe("tools.knowledge_validator"),
      detail: "import tools.knowledge_validator",
    },
    {
      id: "method-validator",
      label: "Method Validator",
      level: python.level === "unavailable" ? "unavailable" : moduleProbe("tools.method_validator"),
      detail: "import tools.method_validator",
    },
    {
      id: "search",
      label: "Search Index",
      level: "healthy",
      detail: `派生索引，可重建。探测命中 ${search.search("P0002").length}`,
    },
    {
      id: "lean",
      label: "Lean verification",
      level: failed > 0 ? "warning" : verified > 0 ? "healthy" : "warning",
      detail: `${lean.length} 条 correspondence；verified=${verified}（仅 manifest SUCCEEDED）`,
    },
    {
      id: "web",
      label: "Web version",
      level: "healthy",
      detail: pkg.version,
    },
    {
      id: "node",
      label: "Node",
      level: "healthy",
      detail: process.version,
    },
    {
      id: "python",
      label: "Python",
      level: python.level,
      detail: python.detail,
    },
    {
      id: "operations",
      label: "Write operations",
      level: ops.available ? "healthy" : "unavailable",
      detail: ops.available
        ? `gateway ${ops.operations.join(", ")}`
        : `Write operations unavailable · ${ops.detail}`,
    },
  ];
  const studio = existsSync(join(repo.repoRoot, "tools", "studio", "__main__.py"));
  rows.push({
    id: "studio",
    label: "tools.studio fallback",
    level: studio ? "healthy" : "unavailable",
    detail: studio ? "入口存在" : "找不到 tools.studio",
  });
  return rows;
}
