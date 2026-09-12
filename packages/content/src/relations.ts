import type {
  Knowledge,
  KnowledgeRelationView,
  Method,
  Problem,
  ProblemRelationView,
  RelatedRef,
} from "@math-ai-lab/domain";

function knowledgeRef(item: Knowledge, origin: RelatedRef["origin"]): RelatedRef {
  return {
    id: item.id,
    title: item.title,
    href: `/knowledge/${item.id}`,
    origin,
  };
}

function problemRef(item: Problem, origin: RelatedRef["origin"]): RelatedRef {
  return {
    id: item.id,
    title: item.title,
    href: `/problems/${item.id}`,
    origin,
  };
}

function methodRef(item: Method, origin: RelatedRef["origin"]): RelatedRef {
  return {
    id: item.id,
    title: item.title,
    href: `/methods/${item.id}`,
    origin,
  };
}

export function knowledgeRelationsOf(
  knowledge: Knowledge[],
  problems: Problem[],
  methods: Method[],
  id: string,
): KnowledgeRelationView | null {
  const item = knowledge.find((row) => row.id === id);
  if (!item) return null;
  const byId = new Map(knowledge.map((row) => [row.id, row]));
  const prerequisites: RelatedRef[] = [];
  for (const ref of item.prerequisites ?? []) {
    const target = byId.get(ref);
    if (target) {
      prerequisites.push(knowledgeRef(target, "explicit"));
    }
  }
  const related: RelatedRef[] = [];
  for (const ref of item.related ?? []) {
    const target = byId.get(ref);
    if (target) {
      related.push(knowledgeRef(target, "explicit"));
    }
  }
  const usedBy: RelatedRef[] = [];
  for (const other of knowledge) {
    if (other.id === id) continue;
    if ((other.prerequisites ?? []).includes(id) || (other.related ?? []).includes(id)) {
      usedBy.push(knowledgeRef(other, "derived"));
    }
  }
  for (const problem of problems) {
    if ((problem.knowledge ?? []).includes(id)) {
      usedBy.push(problemRef(problem, "derived"));
    }
  }
  for (const method of methods) {
    if ((method.knowledge ?? []).includes(id)) {
      usedBy.push(methodRef(method, "derived"));
    }
  }
  return { id, prerequisites, related, usedBy };
}

export function problemRelationsOf(
  knowledge: Knowledge[],
  problems: Problem[],
  methods: Method[],
  id: string,
): ProblemRelationView | null {
  const item = problems.find((row) => row.id === id);
  if (!item) return null;
  const knowledgeById = new Map(knowledge.map((row) => [row.id, row]));
  const knowledgeRefs: RelatedRef[] = [];
  for (const kid of item.knowledge ?? []) {
    const target = knowledgeById.get(kid);
    if (target) {
      knowledgeRefs.push(knowledgeRef(target, "explicit"));
    }
  }
  const explicit = new Set(item.knowledge ?? []);
  const methodRefs: RelatedRef[] = [];
  for (const method of methods) {
    const overlap = (method.knowledge ?? []).some((kid) => explicit.has(kid));
    if (overlap) {
      methodRefs.push(methodRef(method, "derived"));
    }
  }
  const relatedProblems: RelatedRef[] = [];
  if (explicit.size > 0) {
    for (const other of problems) {
      if (other.id === id) continue;
      const share = (other.knowledge ?? []).some((kid) => explicit.has(kid));
      if (share) {
        relatedProblems.push(problemRef(other, "derived"));
      }
    }
  }
  return {
    id,
    knowledge: knowledgeRefs,
    methods: methodRefs,
    relatedProblems,
  };
}
