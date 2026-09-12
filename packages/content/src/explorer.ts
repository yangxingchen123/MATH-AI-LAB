import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { extname, join } from "node:path";
import type { ExplorerFile, ExplorerListing } from "@math-ai-lab/domain";
import {
  EXPLORER_ROOTS,
  isDeniedSegment,
  resolveSafeRel,
  toPosixRel,
} from "./safe-path.ts";

const TEXT_EXT = new Set([
  ".md",
  ".tex",
  ".lean",
  ".py",
  ".yaml",
  ".yml",
  ".json",
  ".txt",
  ".ts",
  ".tsx",
  ".css",
  ".html",
  ".bat",
  ".vbs",
]);

const MAX_TEXT = 200_000;

function languageOf(path: string): string {
  const ext = extname(path).toLowerCase();
  return ext.replace(".", "") || "text";
}

export function listExplorer(
  repoRoot: string,
  relPath = "",
): ExplorerListing | null {
  const posix = toPosixRel(relPath).replace(/^\/+/, "");
  if (!posix) {
    return {
      path: "",
      entries: EXPLORER_ROOTS.filter((name) => existsSync(join(repoRoot, name))).map(
        (name) => ({
          name,
          path: name,
          kind: "dir" as const,
        }),
      ),
    };
  }
  const safe = resolveSafeRel(repoRoot, posix);
  if (!safe) {
    return null;
  }
  const abs = join(repoRoot, ...safe.split("/"));
  if (!existsSync(abs) || !statSync(abs).isDirectory()) {
    return null;
  }
  let entries;
  try {
    entries = readdirSync(abs, { withFileTypes: true });
  } catch {
    return null;
  }
  const rows = entries
    .filter((entry) => !entry.name.startsWith(".") && !isDeniedSegment(entry.name))
    .map((entry) => ({
      name: entry.name,
      path: `${safe}/${entry.name}`,
      kind: entry.isDirectory() ? ("dir" as const) : ("file" as const),
    }))
    .sort((a, b) => {
      if (a.kind !== b.kind) return a.kind === "dir" ? -1 : 1;
      return a.name.localeCompare(b.name, "zh");
    });
  return { path: safe, entries: rows };
}

export function readExplorerFile(
  repoRoot: string,
  relPath: string,
): ExplorerFile | null {
  const safe = resolveSafeRel(repoRoot, relPath);
  if (!safe) {
    return null;
  }
  const abs = join(repoRoot, ...safe.split("/"));
  if (!existsSync(abs) || !statSync(abs).isFile()) {
    return null;
  }
  const ext = extname(safe).toLowerCase();
  if (ext === ".pdf") {
    return {
      path: safe,
      language: "pdf",
      binary: true,
      previewKind: "pdf",
    };
  }
  if (!TEXT_EXT.has(ext)) {
    return {
      path: safe,
      language: languageOf(safe),
      binary: true,
      previewKind: "unsupported",
    };
  }
  const text = readFileSync(abs, "utf8");
  return {
    path: safe,
    language: languageOf(safe),
    text: text.length > MAX_TEXT ? `${text.slice(0, MAX_TEXT)}\n\n…截断…` : text,
    previewKind: "text",
  };
}
