import { existsSync, statSync } from "node:fs";
import { join } from "node:path";
import type { EvidenceItem, ResearchProject, TimelineEvent } from "@math-ai-lab/domain";

function isoDay(mtimeMs: number): string {
  return new Date(mtimeMs).toISOString().slice(0, 10);
}

export function researchTimelineOf(
  repoRoot: string,
  project: ResearchProject,
): TimelineEvent[] {
  const events: TimelineEvent[] = [];
  for (const section of project.sections) {
    const abs = join(repoRoot, ...section.sourcePath.split("/"));
    let at: string | undefined;
    if (existsSync(abs)) {
      at = isoDay(statSync(abs).mtimeMs);
    }
    events.push({
      id: section.id,
      label: section.title,
      at,
      origin: "derived",
      href: `#${section.id}`,
    });
  }
  return events;
}

export function researchEvidenceOf(project: ResearchProject): EvidenceItem[] {
  const items: EvidenceItem[] = [];
  const map: Record<string, EvidenceItem["kind"]> = {
    overview: "source",
    question: "source",
    assumptions: "source",
    model: "source",
    experiments: "experiment",
    evidence: "reproduction",
    decisions: "source",
    negative: "reproduction",
    references: "source",
    writing: "artifact",
    governance: "source",
  };
  for (const section of project.sections) {
    items.push({
      kind: map[section.id] ?? "source",
      label: section.title,
      sourcePath: section.sourcePath,
      origin: "derived",
    });
  }
  return items;
}
