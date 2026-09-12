import { existsSync, readFileSync } from "node:fs";
import { basename, join } from "node:path";
import type { PromptDocument } from "@math-ai-lab/domain";
import { listMarkdown, toPosix } from "./scan.ts";

const ROOT = "10_提示词";

function categoryOf(name: string): string {
  if (name.includes("Research_Lab")) return "研究实验室";
  if (name.includes("Research_Project")) return "研究项目";
  if (name.includes("Modeling") || name.includes("Literature")) {
    return "建模与文献";
  }
  if (name.includes("Normal_Operation")) return "日常操作";
  if (name.includes("数学研究")) return "数学研究";
  return "其他";
}

function titleOf(body: string, fallback: string): string {
  const heading = body.match(/^#\s+(.+)$/m);
  return heading?.[1]?.trim() || fallback.replace(/\.md$/, "");
}

export function listPrompts(repoRoot: string): PromptDocument[] {
  const base = join(repoRoot, ROOT);
  if (!existsSync(base)) {
    return [];
  }
  return listMarkdown(base).map((abs) => {
    const sourcePath = toPosix(repoRoot, abs);
    const body = readFileSync(abs, "utf8");
    const name = basename(abs);
    return {
      id: name.replace(/\.md$/, ""),
      title: titleOf(body, name),
      category: categoryOf(name),
      sourcePath,
      body,
    };
  });
}

export function getPrompt(
  repoRoot: string,
  id: string,
): PromptDocument | null {
  if (!id || id.includes("..") || id.includes("/") || id.includes("\\")) {
    return null;
  }
  return listPrompts(repoRoot).find((row) => row.id === id) ?? null;
}
