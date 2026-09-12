import { existsSync, readdirSync, statSync } from "node:fs";
import { basename, join } from "node:path";
import type { OutputArtifact } from "@math-ai-lab/domain";
import { toPosix } from "./scan.ts";

const ROOT = "08_成果输出";
const SKIP = new Set([".gitkeep"]);

function kindOf(name: string): OutputArtifact["kind"] {
  const lower = name.toLowerCase();
  if (lower.endsWith(".pdf")) return "pdf";
  if (lower.endsWith(".tex") || lower.endsWith(".sty") || lower.endsWith(".cls")) {
    return "latex";
  }
  if (lower.endsWith(".md")) return "markdown";
  return "other";
}

function walk(absDir: string, out: string[]): void {
  let entries;
  try {
    entries = readdirSync(absDir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    if (entry.name.startsWith(".") || SKIP.has(entry.name)) {
      continue;
    }
    const full = join(absDir, entry.name);
    if (entry.isDirectory()) {
      walk(full, out);
    } else if (entry.isFile()) {
      out.push(full);
    }
  }
}

export function listOutputs(repoRoot: string): OutputArtifact[] {
  const base = join(repoRoot, ROOT);
  if (!existsSync(base)) {
    return [];
  }
  const files: string[] = [];
  walk(base, files);
  return files
    .filter((abs) => {
      try {
        return statSync(abs).isFile();
      } catch {
        return false;
      }
    })
    .map((abs) => {
      const sourcePath = toPosix(repoRoot, abs);
      const name = basename(abs);
      const kind = kindOf(name);
      return {
        id: sourcePath.replaceAll("/", "--"),
        title: name,
        kind,
        sourcePath,
        href: `/outputs/${encodeURIComponent(sourcePath)}`,
        previewable: kind === "pdf" || kind === "markdown",
      };
    })
    .sort((a, b) => a.sourcePath.localeCompare(b.sourcePath, "zh"));
}

export function getOutput(
  repoRoot: string,
  idOrPath: string,
): OutputArtifact | null {
  const decoded = decodeURIComponent(idOrPath);
  return (
    listOutputs(repoRoot).find(
      (row) => row.id === idOrPath || row.sourcePath === decoded,
    ) ?? null
  );
}
