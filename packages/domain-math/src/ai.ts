import type { Candidate } from "@math-ai-lab/domain-math";

export interface AISuggestion {
  candidates: Candidate[];
  notes: string[];
  warning: string;
}

export interface AIResearchProvider {
  suggest(topic: string): AISuggestion;
  critique(entityId: string): AISuggestion;
  search(query: string): AISuggestion;
  formalize(entityId: string): AISuggestion;
}

const WARNING = "Mock AI output is a Candidate, never mathematical truth, never canonical.";

function stub(originLabel: string, topic: string): AISuggestion {
  const id = `candidate:ai_mock:${originLabel}:${topic.trim() || "untitled"}`;
  return {
    warning: WARNING,
    notes: [`${originLabel} is mock-only. No model was called.`],
    candidates: [
      {
        id,
        title: `AI candidate: ${topic.trim() || "untitled"}`,
        proposedType: "conjecture",
        status: "idea",
        origin: "ai_mock",
        notes: WARNING,
      },
    ],
  };
}

export class MockAIResearchProvider implements AIResearchProvider {
  suggest(topic: string): AISuggestion {
    return stub("suggest", topic);
  }
  critique(entityId: string): AISuggestion {
    return stub("critique", entityId);
  }
  search(query: string): AISuggestion {
    return stub("search", query);
  }
  formalize(entityId: string): AISuggestion {
    return stub("formalize", entityId);
  }
}
