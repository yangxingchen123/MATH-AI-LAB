import type { ContentRepository } from "@math-ai-lab/content";
import { projectUniverse, type LeanBinding, type UniverseSnapshot } from "@math-ai-lab/domain-math";

export function universeFromRepository(repo: ContentRepository): UniverseSnapshot {
  const knowledge = repo.listKnowledge();
  const problems = repo.listProblems();
  const methods = repo.listMethods();
  const leanBindings: LeanBinding[] = [];
  for (const item of [...knowledge, ...problems, ...methods]) {
    const kind = item.type === "knowledge" ? "knowledge" : item.type === "problem" ? "problem" : "method";
    for (const lean of repo.leanFor(item.id)) {
      leanBindings.push({ sourceId: item.id, sourceKind: kind, lean });
    }
  }
  const attempts = problems.flatMap((item) => repo.listAttempts(item.id));
  return projectUniverse({
    knowledge,
    problems,
    methods,
    attempts,
    lean: repo.listLean(),
    leanBindings,
    lab: repo.listLab(),
    outputs: repo.listOutputs(),
    research: repo.listResearch(),
    references: repo.listReferences(),
  });
}
