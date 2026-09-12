import type { ExplorationBriefing } from "./project.ts";
import { reasoningProvesTheorem, type MathematicalReasoningGraph } from "./reasoning-graph.ts";
import type { ExplorationState } from "./engine.ts";
import { notebookIsCanonical } from "./notebook.ts";
import { sessionConclusionIsTheorem } from "./session.ts";
import { strategyIsProof } from "./proof-strategy.ts";
import { evolutionProvesTheorem, type TheoryEvolutionGraph } from "./evolution.ts";
import type { SearchHit, SearchHitKind } from "./search.ts";

export interface ExplorationCatalogItem {
  id: string;
  title: string;
  group: string;
  detail: string;
  body: string;
  state?: string;
  pipeline?: string;
}

const MAX_ID_LENGTH = 240;

export function isSafeExplorationId(id: string): boolean {
  if (!id || id.length > MAX_ID_LENGTH) return false;
  const normalized = id.replaceAll("\\", "/");
  if (normalized.includes("..") || normalized.includes("/") || normalized.includes("\0")) {
    return false;
  }
  return true;
}

export function lookupExploration(
  items: ExplorationCatalogItem[],
  id: string,
): ExplorationCatalogItem | null {
  if (!isSafeExplorationId(id)) return null;
  return items.find((row) => row.id === id) ?? null;
}

function itemBody(title: string, lines: string[]): string {
  return [`# ${title}`, "", ...lines, "", "Candidate / process record only. Not Canonical.", ""].join("\n");
}

export function catalogExploration(input: {
  briefing: ExplorationBriefing;
  state: ExplorationState;
}): ExplorationCatalogItem[] {
  const { briefing, state } = input;
  const reasoning = state.reasoning[0];
  const rows: ExplorationCatalogItem[] = [
    {
      id: "overview",
      title: "探索总览",
      group: "总览",
      detail: "五问只读简报",
      body: [
        "# 数学探索（过程层）",
        "",
        "只读。不是 Canonical。Lab 记录仍是 Candidate。禁止自动 Promotion。",
        "",
        "## 五问",
        "",
        `- 我们知道什么：${briefing.answers.what_we_know}`,
        `- 正在探索什么：${briefing.answers.what_we_explore}`,
        `- 为何相信：${briefing.answers.why_we_believe}`,
        `- 哪些失败了：${briefing.answers.what_failed}`,
        `- 下一步可能是什么：${briefing.answers.what_is_next}`,
        "",
        `Theorems invented: ${briefing.theoremCount}`,
        "Wrote Canonical: false",
        "",
      ].join("\n"),
    },
  ];
  const push = (
    group: string,
    item: { id: string; title: string; detail: string; state?: string; pipeline?: string },
    extra: string[] = [],
  ) => {
    rows.push({
      id: item.id,
      title: item.title,
      group,
      detail: item.detail,
      state: item.state,
      pipeline: item.pipeline,
      body: itemBody(item.title, [
        `- id: \`${item.id}\``,
        `- detail: ${item.detail}`,
        ...(item.state ? [`- lifecycle: \`${item.state}\``] : []),
        ...(item.pipeline ? [`- pipeline: \`${item.pipeline}\``] : []),
        ...extra,
      ]),
    });
  };
  for (const item of briefing.known) push("Known", item);
  for (const item of briefing.exploring) {
    push(`正在探索 · ${item.state ?? "exploring"}`, item, ["- not_a_theorem: true"]);
  }
  for (const item of briefing.belief) push("Belief", item);
  for (const item of briefing.failures) {
    push("失败记忆", item, ["- Failure is retained. Not a theorem."]);
  }
  for (const item of briefing.patterns) {
    push("模式", item, ["- Pattern ≠ theorem.", "- confidence is not mathematical truth."]);
  }
  for (const item of briefing.next) {
    push("下一步", item, ["- Promotion is not automatic."]);
  }
  if (reasoning) {
    rows.push(reasoningCatalogItem(reasoning));
    for (const node of reasoning.nodes) {
      const requires = reasoning.edges
        .filter((edge) => edge.source === node.id && edge.type === "requires")
        .map((edge) => edge.target);
      rows.push({
        id: `reasoning:${node.id}`,
        title: node.content,
        group: "推理图",
        detail: `kind=${node.kind} · requires ${requires.length} premises`,
        body: itemBody(node.content, [
          `- id: \`${node.id}\``,
          `- kind: \`${node.kind}\``,
          `- requires: ${requires.length ? requires.map((id) => `\`${id}\``).join(", ") : "（无）"}`,
          "- reasoningProvesTheorem: false",
        ]),
      });
    }
  }
  for (const notebook of state.notebooks) {
    rows.push({
      id: notebook.id,
      title: notebook.title,
      group: "笔记本",
      detail: `canonical=${notebookIsCanonical(notebook)} · questions=${notebook.questions.length} · failures=${notebook.failures.length}`,
      body: itemBody(notebook.title, [
        `- id: \`${notebook.id}\``,
        `- notebookIsCanonical: ${notebookIsCanonical(notebook)}`,
        `- observations: ${notebook.observations.length}`,
        `- questions: ${notebook.questions.length}`,
        `- ideas: ${notebook.ideas.length}`,
        `- failures: ${notebook.failures.length}`,
        `- results: ${notebook.results.length}`,
        "- Notebook is exploration history. Not Canonical.",
      ]),
    });
  }
  for (const session of state.sessions) {
    rows.push({
      id: session.id,
      title: session.goal,
      group: "会话",
      detail: `conclusion_is_theorem=${sessionConclusionIsTheorem(session)} · actions=${session.actions.length}`,
      body: itemBody(session.goal, [
        `- id: \`${session.id}\``,
        `- researcher: ${session.researcher.type}/${session.researcher.id}`,
        `- sessionConclusionIsTheorem: ${sessionConclusionIsTheorem(session)}`,
        `- inputs: ${session.inputs.length}`,
        `- actions: ${session.actions.length}`,
        `- outputs: ${session.outputs.length}`,
        "- Session conclusion is not a theorem.",
      ]),
    });
  }
  for (const strategy of state.strategies) {
    rows.push({
      id: strategy.id,
      title: strategy.strategy,
      group: "证明策略",
      detail: `cases=${strategy.successfulCases.length} · proof=${strategyIsProof(strategy)}`,
      body: itemBody(strategy.strategy, [
        `- id: \`${strategy.id}\``,
        `- strategyIsProof: ${strategyIsProof(strategy)}`,
        `- successfulCases: ${strategy.successfulCases.map((id) => `\`${id}\``).join(", ") || "（无）"}`,
        ...strategy.applicableConditions.map((line) => `- condition: ${line}`),
        ...strategy.limitations.map((line) => `- limitation: ${line}`),
        "- Lexical scan ≠ stored proof. Not Canonical.",
      ]),
    });
  }
  const evolution = state.evolution[0];
  if (evolution) {
    rows.push(evolutionCatalogItem(evolution));
  }
  return rows;
}

function hitKind(group: string): SearchHitKind {
  if (group.includes("失败")) return "failure";
  if (group.includes("推理")) return "proof";
  if (group.includes("策略")) return "strategy";
  if (group.includes("模式") || group.includes("演化")) return "analogy";
  return "concept";
}

/** Substring match over catalog fields. Hits stay candidates. No embeddings. */
export function searchExplorationCatalog(
  items: ExplorationCatalogItem[],
  query: string,
): SearchHit[] {
  const needle = query.trim().toLowerCase();
  if (!needle) return [];
  const hits: SearchHit[] = [];
  for (const row of items) {
    if (!isSafeExplorationId(row.id)) continue;
    const hay = [row.id, row.title, row.group, row.detail, row.body].join("\n").toLowerCase();
    if (!hay.includes(needle)) continue;
    hits.push({ id: row.id, kind: hitKind(row.group), title: row.title, status: "candidate" });
  }
  return hits;
}

function reasoningCatalogItem(graph: MathematicalReasoningGraph): ExplorationCatalogItem {
  const nodeLines = graph.nodes.map((node) => `- \`${node.id}\` · ${node.kind} · ${node.content}`);
  const edgeLines = graph.edges.map(
    (edge) => `- \`${edge.source}\` -${edge.type}-> \`${edge.target}\``,
  );
  return {
    id: "reasoning",
    title: "推理图（引理依赖）",
    group: "推理图",
    detail: `${graph.nodes.length} nodes, ${graph.edges.length} edges, proves_theorem=${reasoningProvesTheorem(graph)}`,
    body: [
      "# 推理图（引理依赖）",
      "",
      "只投影 correspondence / Lean `depends_on`。文件顺序不是推理边。图的存在不等于定理已证。",
      "",
      `proves_theorem: ${reasoningProvesTheorem(graph)}`,
      "",
      "## Nodes",
      "",
      ...(nodeLines.length ? nodeLines : ["（无）"]),
      "",
      "## Requires",
      "",
      ...(edgeLines.length ? edgeLines : ["（无声明依赖）"]),
      "",
      "Not Canonical.",
      "",
    ].join("\n"),
  };
}

function evolutionCatalogItem(graph: TheoryEvolutionGraph): ExplorationCatalogItem {
  const nodeLines = graph.nodes.map((node) => `- \`${node.id}\` · ${node.title}`);
  return {
    id: "evolution",
    title: "理论模块（无演化边）",
    group: "理论演化",
    detail: `${graph.nodes.length} nodes, ${graph.edges.length} edges, proves_theorem=${evolutionProvesTheorem(graph)}`,
    body: [
      "# 理论模块（无演化边）",
      "",
      "One node per Lean module. No extends/simplifies/unifies/specializes is claimed.",
      "",
      `proves_theorem: ${evolutionProvesTheorem(graph)}`,
      `edges: ${graph.edges.length}`,
      "",
      "## Nodes",
      "",
      ...(nodeLines.length ? nodeLines : ["（无）"]),
      "",
      "Not Canonical.",
      "",
    ].join("\n"),
  };
}
