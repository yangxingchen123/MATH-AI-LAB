/** Erdős open-problem pointers. Metadata only. Not theorems. */

import erdosIndex from "./erdos-additive.json" with { type: "json" };
import { createUnknownRegion, type UnknownRegion } from "./region.ts";
import { createOpenQuestion, createResearchDirection, type OpenQuestion, type ResearchDirection } from "./direction.ts";

export interface ErdősQuestionRecord {
  id: string;
  number: string;
  status: string;
  tags: string[];
  formalized: string;
  prize?: string | number | boolean | null;
  oeis: string[];
  url: string;
  nickname?: string;
  not_a_theorem: true;
  not_an_open_question?: true;
}

export interface ErdősFrontierIndex {
  version: string;
  upstream: string;
  pin: string;
  source: string;
  scope_tag: string;
  not_a_theorem: true;
  writes_canonical: false;
  network: false;
  region: { id: string; title: string; description: string };
  direction: { id: string; title: string; motivation: string };
  counts: {
    vendor_records: number;
    additive_records: number;
    open_questions: number;
    audit_records: number;
  };
  additive_status_counts: Record<string, number>;
  questions: ErdősQuestionRecord[];
  audit: ErdősQuestionRecord[];
}

export interface FrontierCatalogItem {
  id: string;
  title: string;
  group: string;
  detail: string;
  body: string;
  state?: string;
}

export function loadErdosIndex(): ErdősFrontierIndex {
  return erdosIndex as ErdősFrontierIndex;
}

export function questionIsTheorem(_question: OpenQuestion): false {
  return false;
}

export function projectErdosFrontier(): {
  region: UnknownRegion;
  direction: ResearchDirection;
  questions: OpenQuestion[];
} {
  const data = loadErdosIndex();
  const regionMade = createUnknownRegion({
    id: data.region.id,
    title: data.region.title,
    description: data.region.description,
    relatedEntityIds: [],
    openQuestionIds: data.questions.map((row) => row.id),
    directionIds: [data.direction.id],
    status: "open",
  });
  const directionMade = createResearchDirection({
    id: data.direction.id,
    title: data.direction.title,
    regionId: data.region.id,
    motivation: data.direction.motivation,
    status: "open",
  });
  const questions: OpenQuestion[] = [];
  for (const row of data.questions) {
    const made = createOpenQuestion({
      id: row.id,
      prompt: erdosPrompt(row),
      regionId: data.region.id,
      relatedEntityIds: [],
    });
    if (made.ok) questions.push(made.question);
  }
  if (!regionMade.ok || !directionMade.ok) {
    throw new Error("Erdős frontier index failed validation.");
  }
  return { region: regionMade.region, direction: directionMade.direction, questions };
}

export function erdosPrompt(row: Pick<ErdősQuestionRecord, "number" | "status" | "url">): string {
  return `Erdős problem ${row.number} is listed ${row.status} in additive combinatorics. See ${row.url}. Not a theorem in this warehouse.`;
}

export function erdosTitle(row: Pick<ErdősQuestionRecord, "number" | "nickname">): string {
  return row.nickname ? `Erdős problem ${row.number} (${row.nickname})` : `Erdős problem ${row.number}`;
}

export function catalogErdosFrontier(): FrontierCatalogItem[] {
  const data = loadErdosIndex();
  const projected = projectErdosFrontier();
  const rows: FrontierCatalogItem[] = [
    {
      id: "frontier",
      title: data.region.title,
      group: "前沿",
      detail: `${data.counts.open_questions} open pointers · pin=${data.pin.slice(0, 7)} · theorem=false`,
      body: [
        "# Additive combinatorics (external open index)",
        "",
        `upstream: ${data.upstream}`,
        `pin: ${data.pin}`,
        `source: ${data.source}`,
        `open_questions: ${data.counts.open_questions}`,
        `audit_records: ${data.counts.audit_records}`,
        `additive_records: ${data.counts.additive_records}`,
        `vendor_records: ${data.counts.vendor_records}`,
        `writes_canonical: ${data.writes_canonical}`,
        `network: ${data.network}`,
        `not_a_theorem: ${data.not_a_theorem}`,
        "",
        "Local vendor pin. Runtime reads data/problems.yaml. No GitHub API. Not Canonical.",
        "",
      ].join("\n"),
    },
    {
      id: projected.region.id,
      title: projected.region.title,
      group: "前沿",
      state: projected.region.status,
      detail: `UnknownRegion · questions=${projected.questions.length}`,
      body: frontierBody(projected.region.title, [
        `- id: \`${projected.region.id}\``,
        `- status: \`${projected.region.status}\``,
        `- direction: \`${projected.direction.id}\``,
        "- UnknownRegion ≠ Universe entity.",
        "- OpenQuestion ≠ theorem.",
      ]),
    },
    {
      id: "frontier-audit",
      title: "Additive combinatorics (vendor audit)",
      group: "前沿备查",
      detail: `${data.counts.audit_records} non-open additive rows · not OpenQuestions`,
      body: frontierBody("Additive combinatorics (vendor audit)", [
        "Non-open additive-combinatorics rows from the local pin. Not OpenQuestions. Not theorems.",
        "",
        `audit_records: ${data.counts.audit_records}`,
        `additive_records: ${data.counts.additive_records}`,
        "",
        ...Object.keys(data.additive_status_counts)
          .sort()
          .map((name) => `- ${name}: ${data.additive_status_counts[name]}`),
      ]),
    },
  ];
  for (const row of data.questions) {
    rows.push(pointerRow(row, "前沿", true));
  }
  for (const row of data.audit) {
    rows.push(pointerRow(row, "前沿备查", false));
  }
  return rows;
}

function pointerRow(row: ErdősQuestionRecord, group: string, openQuestion: boolean): FrontierCatalogItem {
  const title = erdosTitle(row);
  const extra = openQuestion
    ? []
    : [
        "- not_an_open_question: true",
        "- OpenQuestion projection skipped; this is local audit of the vendor YAML.",
      ];
  const nick = row.nickname ? [`- nickname: ${row.nickname}`] : [];
  return {
    id: row.id,
    title,
    group,
    state: openQuestion ? "open" : row.status,
    detail: `status=${row.status} · formalized=${row.formalized} · not a theorem`,
    body: frontierBody(title, [
      `- id: \`${row.id}\``,
      `- status: ${row.status}`,
      ...nick,
      `- tags: ${row.tags.join(", ")}`,
      `- formalized (upstream flag): ${row.formalized}`,
      `- url: ${row.url}`,
      "- not_a_theorem: true",
      ...extra,
      "",
      erdosPrompt(row),
      "",
      "External formalized=yes is not Lean verification in this warehouse.",
    ]),
  };
}

function frontierBody(title: string, lines: string[]): string {
  return [`# ${title}`, "", ...lines, "", "Candidate / process record only. Not Canonical.", ""].join("\n");
}
