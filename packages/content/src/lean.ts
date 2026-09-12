import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { parse as parseYaml } from "yaml";
import type { LeanTheorem, LeanVerifyStatus } from "@math-ai-lab/domain";

const LEAN_ROOT = "06_LEAN形式化";

interface CorrespondenceItem {
  id?: unknown;
  natural_language?: unknown;
  lean_decl?: unknown;
  lean_file?: unknown;
  family?: unknown;
}

interface ManifestBuild {
  status?: unknown;
  log_ref?: unknown;
}

function asString(value: unknown): string | undefined {
  return typeof value === "string" && value.trim() ? value.trim() : undefined;
}

function loadCorrespondence(repoRoot: string): CorrespondenceItem[] {
  const path = join(repoRoot, LEAN_ROOT, "correspondence.yaml");
  if (!existsSync(path)) {
    return [];
  }
  const data = parseYaml(readFileSync(path, "utf8")) as {
    theorems?: unknown;
  };
  return Array.isArray(data.theorems) ? (data.theorems as CorrespondenceItem[]) : [];
}

function loadManifestStatus(
  repoRoot: string,
  id: string,
): { status?: string; log?: string; path?: string } {
  const path = join(repoRoot, LEAN_ROOT, "manifests", `${id}.yaml`);
  if (!existsSync(path)) {
    return {};
  }
  const data = parseYaml(readFileSync(path, "utf8")) as { build?: ManifestBuild };
  const status = asString(data.build?.status);
  const log = asString(data.build?.log_ref);
  return { status, log, path: `${LEAN_ROOT}/manifests/${id}.yaml` };
}

function mapStatus(
  sourceExists: boolean,
  buildStatus: string | undefined,
): LeanVerifyStatus {
  if (!sourceExists) {
    return "not_formalized";
  }
  if (buildStatus === "SUCCEEDED") {
    return "verified";
  }
  if (buildStatus === "FAILED") {
    return "failed";
  }
  if (buildStatus === "CHECKING" || buildStatus === "RUNNING") {
    return "checking";
  }
  return "source_exists";
}

export function listLeanTheorems(repoRoot: string): LeanTheorem[] {
  const rows: LeanTheorem[] = [];
  for (const item of loadCorrespondence(repoRoot)) {
    const id = asString(item.id);
    if (!id) continue;
    const leanFile = asString(item.lean_file);
    const absLean = leanFile
      ? join(repoRoot, LEAN_ROOT, leanFile.replaceAll("\\", "/"))
      : null;
    const sourceExists = Boolean(absLean && existsSync(absLean));
    const manifest = loadManifestStatus(repoRoot, id);
    const status = mapStatus(sourceExists, manifest.status);
    rows.push({
      id,
      title: asString(item.natural_language) || id,
      leanDecl: asString(item.lean_decl),
      leanFile: leanFile ? `${LEAN_ROOT}/${leanFile}` : undefined,
      sourceExists,
      status,
      evidencePath: status === "verified" || status === "failed" ? manifest.path : undefined,
      logSummary:
        status === "verified"
          ? `manifest build.status=${manifest.status}`
          : status === "failed"
            ? `manifest build.status=${manifest.status}`
            : sourceExists
              ? "源文件存在，但没有 SUCCEEDED 验证证据"
              : "correspondence 有记录，源文件不存在",
      family: asString(item.family),
    });
  }
  return rows.sort((a, b) => a.id.localeCompare(b.id));
}

export function getLeanTheorem(
  repoRoot: string,
  id: string,
): LeanTheorem | null {
  if (!id || id.includes("..") || id.includes("/") || id.includes("\\")) {
    return null;
  }
  return listLeanTheorems(repoRoot).find((row) => row.id === id) ?? null;
}

export function leanForStableId(
  repoRoot: string,
  stableId: string,
): LeanTheorem[] {
  const needle = stableId.trim();
  if (!needle) return [];
  return listLeanTheorems(repoRoot).filter((row) => {
    const blob = `${row.title} ${row.logSummary ?? ""}`;
    return blob.includes(needle);
  });
}
