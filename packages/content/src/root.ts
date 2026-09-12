import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const SCHEMA_MARKER = "元数据规范.md";
const KNOWLEDGE_DIR = "01_知识库";

export function isProjectRoot(path: string): boolean {
  return existsSync(join(path, SCHEMA_MARKER)) && existsSync(join(path, KNOWLEDGE_DIR));
}

export function findProjectRoot(start = process.cwd()): string {
  let current = resolve(start);
  while (true) {
    if (isProjectRoot(current)) {
      return current;
    }
    const parent = dirname(current);
    if (parent === current) {
      throw new Error(
        `Cannot find MATH-AI-LAB root from ${start}. Expected ${SCHEMA_MARKER} and ${KNOWLEDGE_DIR}/.`,
      );
    }
    current = parent;
  }
}

export function defaultPackageAnchor(): string {
  return dirname(fileURLToPath(import.meta.url));
}

export function resolveRepoRoot(explicit?: string): string {
  const candidate = explicit ?? process.env.MATH_AI_LAB_ROOT;
  if (candidate) {
    const root = resolve(candidate);
    if (!isProjectRoot(root)) {
      throw new Error(`Invalid repo root: ${root}`);
    }
    return root;
  }
  try {
    return findProjectRoot(process.cwd());
  } catch {
    return findProjectRoot(defaultPackageAnchor());
  }
}
