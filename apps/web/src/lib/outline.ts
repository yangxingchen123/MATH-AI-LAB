import { extractHeadings } from "@math-ai-lab/math-renderer";
import type { ProblemBodyView } from "@math-ai-lab/content";
import type { ResearchProject } from "@math-ai-lab/domain";
import type { TocHeading } from "../../features/shell/toc-context";

export function problemOutline(view: ProblemBodyView): TocHeading[] {
  const headings: TocHeading[] = [{ id: "statement", level: 2, text: "题面" }];
  const used = new Set(headings.map((item) => item.id));
  for (const part of view.parts) {
    const id = `part-${part.id}`;
    headings.push({ id, level: 2, text: `Part (${part.id})` });
    used.add(id);
    const nested = extractHeadings(
      [part.statement, part.notes, part.solution].filter(Boolean).join("\n\n"),
    );
    for (const heading of nested) {
      let next = heading.id;
      if (used.has(next)) {
        next = `${id}-${heading.id}`;
      }
      used.add(next);
      headings.push({
        id: next,
        level: Math.min(6, heading.level + 2),
        text: heading.text,
      });
    }
  }
  if (view.trailing?.trim()) {
    headings.push({ id: "trailing", level: 2, text: "附录" });
  }
  headings.push({ id: "relations", level: 2, text: "关系" });
  headings.push({ id: "attempts", level: 2, text: "User Attempt" });
  return headings;
}

export function researchOutline(project: ResearchProject): TocHeading[] {
  return [
    ...project.sections.map((section) => ({
      id: section.id,
      level: 2,
      text: section.title,
    })),
    { id: "timeline", level: 2, text: "时间线" },
    { id: "evidence", level: 2, text: "证据" },
  ];
}
