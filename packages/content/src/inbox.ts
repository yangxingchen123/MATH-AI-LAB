import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { basename, join } from "node:path";
import type { InboxItem } from "@math-ai-lab/domain";
import { toPosix } from "./scan.ts";

const ROOT = "00_收件箱";

function suggestionOf(name: string, body: string): string | undefined {
  const text = `${name}\n${body}`;
  if (/习题|定理|P\d{4}/.test(text)) {
    return "可能进入题目库（仅视觉建议，未写回）";
  }
  if (/论文|arxiv|doi/i.test(text)) {
    return "可能进入参考资料 / 文献精读（仅视觉建议，未写回）";
  }
  if (/建模|美赛|国赛/.test(text)) {
    return "可能进入研究项目（仅视觉建议，未写回）";
  }
  if (/知识|定义|定理陈述/.test(text)) {
    return "可能进入知识库（仅视觉建议，未写回）";
  }
  return undefined;
}

export function listInbox(repoRoot: string): InboxItem[] {
  const base = join(repoRoot, ROOT);
  if (!existsSync(base)) {
    return [];
  }
  let entries;
  try {
    entries = readdirSync(base, { withFileTypes: true });
  } catch {
    return [];
  }
  const rows: InboxItem[] = [];
  for (const entry of entries) {
    if (!entry.isFile() || entry.name.startsWith(".")) {
      continue;
    }
    const abs = join(base, entry.name);
    if (!statSync(abs).isFile()) {
      continue;
    }
    const sourcePath = toPosix(repoRoot, abs);
    const readable = entry.name.endsWith(".md") || entry.name.endsWith(".txt");
    const body = readable ? readFileSync(abs, "utf8") : "";
    rows.push({
      id: entry.name,
      title: basename(entry.name, ".md"),
      sourcePath,
      suggestion: suggestionOf(entry.name, body),
      body,
    });
  }
  return rows.sort((a, b) => a.id.localeCompare(b.id, "zh"));
}
