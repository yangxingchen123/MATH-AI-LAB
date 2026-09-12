import { existsSync, readFileSync } from "node:fs";
import { basename, join } from "node:path";
import type { MemoryDocument } from "@math-ai-lab/domain";
import { listMarkdown, toPosix } from "./scan.ts";

const ROOT = "09_长期记忆";
const GENERATED_PREFIX = "09_长期记忆/自动索引/";

function roleOf(sourcePath: string, title: string): MemoryDocument["role"] {
  if (sourcePath.startsWith(GENERATED_PREFIX)) return "index";
  if (sourcePath.endsWith("当前学习状态.md")) return "current";
  if (sourcePath.endsWith("数学知识地图.md") || title.includes("知识地图")) {
    return "topics";
  }
  if (sourcePath.endsWith("项目进度.md")) return "research";
  if (sourcePath.endsWith("待办事项.md")) return "goals";
  if (sourcePath.endsWith("已解决问题索引.md")) return "milestones";
  return "other";
}

function titleOf(body: string, fallback: string): string {
  const heading = body.match(/^#\s+(.+)$/m);
  return heading?.[1]?.trim() || fallback.replace(/\.md$/, "");
}

export function listMemory(repoRoot: string): MemoryDocument[] {
  const base = join(repoRoot, ROOT);
  if (!existsSync(base)) {
    return [];
  }
  const rows: MemoryDocument[] = [];
  for (const abs of listMarkdown(base)) {
    const sourcePath = toPosix(repoRoot, abs);
    const body = readFileSync(abs, "utf8");
    const title = titleOf(body, basename(abs));
    rows.push({
      id: sourcePath.replaceAll("/", "--"),
      title,
      sourcePath,
      generated: sourcePath.startsWith(GENERATED_PREFIX),
      role: roleOf(sourcePath, title),
      body,
    });
  }
  return rows.sort((a, b) => {
    if (a.generated !== b.generated) {
      return a.generated ? 1 : -1;
    }
    return a.sourcePath.localeCompare(b.sourcePath, "zh");
  });
}

export function getMemory(
  repoRoot: string,
  idOrPath: string,
): MemoryDocument | null {
  const decoded = decodeURIComponent(idOrPath);
  return (
    listMemory(repoRoot).find(
      (row) => row.id === idOrPath || row.sourcePath === decoded,
    ) ?? null
  );
}
