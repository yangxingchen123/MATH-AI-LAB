import { ProblemDetail } from "../../../features/problems/problem-detail";
import { problemOutline } from "../../../src/lib/outline";
import { rejectBadId, requireObject } from "../../../src/lib/require-content";
import { getRepository } from "../../../src/lib/repo";

export default async function ProblemDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  rejectBadId(id);
  const repo = getRepository();
  const problem = requireObject(repo.getProblem(id));
  const view = requireObject(repo.problemView(id));
  const artifacts = repo
    .listOutputs()
    .filter((item) => item.title.includes(id) || item.sourcePath.includes(id));
  return (
    <ProblemDetail
      problem={problem}
      view={view}
      attempts={repo.listAttempts(id)}
      relations={repo.problemRelations(id)}
      outline={problemOutline(view)}
      knownIds={[...repo.knownIds()]}
      lean={repo.leanFor(id)}
      artifacts={artifacts}
    />
  );
}
