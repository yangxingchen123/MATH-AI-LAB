/**
 * Structured replacement for informal notebooks.
 * Exploration history. Not canonical mathematics.
 */

export interface ResearchNotebook {
  id: string;
  title: string;
  observations: string[];
  questions: string[];
  ideas: string[];
  attempts: string[];
  experiments: string[];
  failures: string[];
  results: string[];
}

export function createNotebook(
  input: Pick<ResearchNotebook, "id" | "title"> & Partial<ResearchNotebook>,
): { ok: true; notebook: ResearchNotebook } | { ok: false; error: string } {
  if (!input.id?.trim() || !input.title?.trim()) {
    return { ok: false, error: "ResearchNotebook requires id and title." };
  }
  return {
    ok: true,
    notebook: {
      id: input.id,
      title: input.title,
      observations: input.observations ?? [],
      questions: input.questions ?? [],
      ideas: input.ideas ?? [],
      attempts: input.attempts ?? [],
      experiments: input.experiments ?? [],
      failures: input.failures ?? [],
      results: input.results ?? [],
    },
  };
}

export function notebookIsCanonical(_notebook: ResearchNotebook): false {
  return false;
}
