import { createRepository, type ContentRepository } from "@math-ai-lab/content";

export function getRepository(): ContentRepository {
  return createRepository();
}
