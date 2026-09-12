import type { NextConfig } from "next";
import path from "node:path";
import { fileURLToPath } from "node:url";

const explorationEntry = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../../packages/domain-exploration/src/index.ts",
);

const frontierEntry = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../../packages/domain-frontier/src/index.ts",
);

const nextConfig: NextConfig = {
  transpilePackages: [
    "@math-ai-lab/content",
    "@math-ai-lab/domain",
    "@math-ai-lab/domain-math",
    "@math-ai-lab/domain-exploration",
    "@math-ai-lab/domain-frontier",
    "@math-ai-lab/math-renderer",
  ],
  allowedDevOrigins: ["127.0.0.1"],
  experimental: {
    externalDir: true,
  },
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      "@math-ai-lab/domain-exploration": explorationEntry,
      "@math-ai-lab/domain-frontier": frontierEntry,
    };
    return config;
  },
};

export default nextConfig;
