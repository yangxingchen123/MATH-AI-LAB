import { catalogExploration, lookupExploration, projectExploration } from "@math-ai-lab/domain-exploration";
import { catalogErdosFrontier } from "@math-ai-lab/domain-frontier";
import { universeFromRepository } from "./universe";
import { getRepository } from "./repo";

export function explorationFromRepository() {
  const projected = projectExploration(universeFromRepository(getRepository()));
  return {
    ...projected,
    catalog: [...catalogExploration(projected), ...catalogErdosFrontier()],
  };
}

export function explorationItem(id: string) {
  const { catalog } = explorationFromRepository();
  return lookupExploration(catalog, id);
}
