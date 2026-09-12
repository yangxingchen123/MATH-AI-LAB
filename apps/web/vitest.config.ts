import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

const explorationEntry = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../../packages/domain-exploration/src/index.ts",
);

const frontierEntry = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../../packages/domain-frontier/src/index.ts",
);

export default defineConfig({
  resolve: {
    alias: {
      "@math-ai-lab/domain-exploration": explorationEntry,
      "@math-ai-lab/domain-frontier": frontierEntry,
    },
  },
  test: {
    include: ["tests/**/*.test.ts"],
  },
});
