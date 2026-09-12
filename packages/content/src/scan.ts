import { readdirSync } from "node:fs";
import { join, relative, sep } from "node:path";

const KNOWLEDGE_TEMPLATE = "01_知识库/知识库模板.md";
const PROBLEM_TEMPLATE = "02_题目库/题目模板.md";
const KNOWLEDGE_INDEX_PREFIX = "01_知识库/_索引/";

export function toPosix(repoRoot: string, absPath: string): string {
  return relative(repoRoot, absPath).split(sep).join("/");
}

export function listMarkdown(absDir: string): string[] {
  const out: string[] = [];
  walk(absDir, out);
  return out.sort();
}

function walk(dir: string, out: string[]): void {
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full, out);
    } else if (entry.isFile() && entry.name.endsWith(".md")) {
      out.push(full);
    }
  }
}

export function isExcludedKnowledge(sourcePath: string): boolean {
  return (
    sourcePath === KNOWLEDGE_TEMPLATE ||
    sourcePath.startsWith(KNOWLEDGE_INDEX_PREFIX)
  );
}

export function isExcludedProblem(sourcePath: string): boolean {
  return sourcePath === PROBLEM_TEMPLATE;
}

export function workflowDirOf(
  sourcePath: string,
): "未解决" | "研究中" | "已解决" | null {
  const parts = sourcePath.split("/");
  if (parts[0] === "02_题目库" && parts[1]) {
    if (parts[1] === "未解决" || parts[1] === "研究中" || parts[1] === "已解决") {
      return parts[1];
    }
  }
  return null;
}
