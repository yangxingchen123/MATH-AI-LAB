export interface ProblemPartView {
  id: string;
  statement?: string;
  notes?: string;
  solution?: string;
}

export interface ProblemBodyView {
  shared: string;
  parts: ProblemPartView[];
  trailing?: string;
}

const SOLUTION_RE =
  /<!-- MATH-AI-LAB:SOLUTION target=P\d{4}\/([A-Za-z0-9]+) BEGIN -->([\s\S]*?)<!-- MATH-AI-LAB:SOLUTION target=P\d{4}\/\1 END -->/g;

const STATUS_RE =
  /^### \(([A-Za-z0-9]+)\)[^\n]*\n([\s\S]*?)(?=^### |\n## |\n<!-- MATH-AI-LAB:SOLUTION|\s*$)/gm;

const STATEMENT_RE =
  /\*\*\(([A-Za-z0-9]+)\)\*\*([^\n]*(?:\n(?!\*\*\([A-Za-z0-9]+\)\*\*)[^\n]*)*)/g;

export function splitProblemBody(
  body: string,
  partIds?: string[],
): ProblemBodyView {
  if (!partIds || partIds.length === 0) {
    return { shared: body, parts: [] };
  }

  const solutions = new Map<string, string>();
  for (const match of body.matchAll(SOLUTION_RE)) {
    solutions.set(match[1], match[2].trim());
  }

  const notes = new Map<string, string>();
  for (const match of body.matchAll(STATUS_RE)) {
    notes.set(match[1], match[2].trim());
  }

  const statements = new Map<string, string>();
  for (const match of body.matchAll(STATEMENT_RE)) {
    statements.set(match[1], `**(${match[1]})**${match[2].trimEnd()}`);
  }

  const firstPartHeading = body.search(/^### \(/m);
  const firstSolution = body.search(/<!-- MATH-AI-LAB:SOLUTION/);
  const cuts = [firstPartHeading, firstSolution].filter((index) => index >= 0);
  const cut = cuts.length > 0 ? Math.min(...cuts) : body.length;
  const shared = body.slice(0, cut).trim();
  const trailingMatch = body.slice(cut).match(/^## 整题归档状态[\s\S]*?(?=\n## 解答|\n<!-- MATH-AI-LAB:SOLUTION|$)/);
  const trailing = trailingMatch?.[0]?.trim();

  return {
    shared,
    trailing,
    parts: partIds.map((id) => {
      const part: ProblemPartView = { id };
      const statement = statements.get(id);
      const note = notes.get(id);
      const solution = solutions.get(id);
      if (statement) part.statement = statement;
      if (note) part.notes = note;
      if (solution) part.solution = solution;
      return part;
    }),
  };
}
