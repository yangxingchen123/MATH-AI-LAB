import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import {
  RESEARCH_PROJECT_KINDS,
  type ResearchProject,
  type ResearchProjectKind,
  type ResearchSection,
} from "@math-ai-lab/domain";

const PROJECTS = "07_项目";
const TEMPLATE = "_模板";

const SECTION_FILES: { file: string; id: string; title: string }[] = [
  { file: "research_dossier.md", id: "overview", title: "概览" },
  { file: "problem.md", id: "question", title: "研究问题" },
  { file: "assumptions.md", id: "assumptions", title: "假设" },
  { file: "model_selection.md", id: "model", title: "选模" },
  { file: "experiment_plan.md", id: "experiments", title: "实验" },
  { file: "evidence.md", id: "evidence", title: "证据" },
  { file: "decisions.md", id: "decisions", title: "决策" },
  { file: "negative_results.md", id: "negative", title: "否定结果" },
  { file: "literature.md", id: "references", title: "文献" },
  { file: "novelty.md", id: "novelty", title: "新颖性" },
  { file: "paper_outline.md", id: "writing", title: "论文大纲" },
  { file: "governance.md", id: "governance", title: "治理" },
];

export function isUnsafeSlug(slug: string): boolean {
  return (
    slug.length === 0 ||
    slug.includes("..") ||
    slug.includes("/") ||
    slug.includes("\\") ||
    slug === TEMPLATE
  );
}

export function inferKind(dir: string): ResearchProjectKind {
  if (existsSync(join(dir, "model_selection.md"))) {
    return "contest_modeling";
  }
  if (existsSync(join(dir, "reading_notes.md"))) {
    return "literature";
  }
  return "research";
}

function titleOf(dir: string, slug: string, dossier: string): string {
  const problemPath = join(dir, "problem.md");
  if (existsSync(problemPath)) {
    const text = readFileSync(problemPath, "utf8");
    const titled = text.match(/^-\s*标题:\s*(.+)$/m);
    if (titled?.[1]) {
      return titled[1].trim();
    }
  }
  const heading = dossier.match(/^#\s+(.+)$/m);
  return heading?.[1]?.trim() || slug;
}

function loadSections(repoRoot: string, slug: string, dir: string): ResearchSection[] {
  const sections: ResearchSection[] = [];
  for (const spec of SECTION_FILES) {
    const abs = join(dir, spec.file);
    if (!existsSync(abs) || !statSync(abs).isFile()) {
      continue;
    }
    const body = readFileSync(abs, "utf8").trim();
    if (!body) {
      continue;
    }
    sections.push({
      id: spec.id,
      title: spec.title,
      sourcePath: `${PROJECTS}/${slug}/${spec.file}`,
      body,
    });
  }
  return sections;
}

export function listResearchProjects(repoRoot: string): ResearchProject[] {
  const base = join(repoRoot, PROJECTS);
  if (!existsSync(base)) {
    return [];
  }
  const rows: ResearchProject[] = [];
  for (const entry of readdirSync(base, { withFileTypes: true })) {
    if (!entry.isDirectory() || entry.name === TEMPLATE) {
      continue;
    }
    const dir = join(base, entry.name);
    const dossierPath = join(dir, "research_dossier.md");
    if (!existsSync(dossierPath)) {
      continue;
    }
    const dossier = readFileSync(dossierPath, "utf8");
    const slug = entry.name;
    rows.push({
      type: "research_project",
      id: slug,
      slug,
      title: titleOf(dir, slug, dossier),
      kind: inferKind(dir),
      sourcePath: `${PROJECTS}/${slug}/research_dossier.md`,
      sections: loadSections(repoRoot, slug, dir),
    });
  }
  return rows.sort((a, b) => a.slug.localeCompare(b.slug, "zh"));
}

export function getResearchProject(
  repoRoot: string,
  slug: string,
): ResearchProject | null {
  if (isUnsafeSlug(slug)) {
    return null;
  }
  return listResearchProjects(repoRoot).find((row) => row.slug === slug) ?? null;
}

export function assertKnownKind(kind: string): kind is ResearchProjectKind {
  return (RESEARCH_PROJECT_KINDS as readonly string[]).includes(kind);
}
