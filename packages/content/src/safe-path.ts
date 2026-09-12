import { isAbsolute, normalize, relative, sep } from "node:path";

const DENY_SEGMENTS = new Set([
  "node_modules",
  ".git",
  ".next",
  ".venv",
  ".lake",
  "__pycache__",
]);

export const EXPLORER_ROOTS = [
  "01_知识库",
  "02_题目库",
  "03_参考资料",
  "04_LATEX",
  "05_代码",
  "06_LEAN形式化",
  "07_项目",
  "08_成果输出",
  "09_长期记忆",
  "10_提示词",
  "11_学习证据",
  "12_方法库",
  "docs",
  "tools",
] as const;

export function toPosixRel(value: string): string {
  return value.split(sep).join("/").replace(/\\/g, "/");
}

export function isDeniedSegment(name: string): boolean {
  return DENY_SEGMENTS.has(name) || name === ".." || name.includes("\0");
}

export function resolveSafeRel(
  repoRoot: string,
  relPath: string,
  allowedRoots: readonly string[] = EXPLORER_ROOTS,
): string | null {
  const posix = toPosixRel(relPath).replace(/^\/+/, "");
  if (!posix || posix.includes("\0") || posix.includes("..")) {
    return null;
  }
  const root = allowedRoots.find(
    (item) => posix === item || posix.startsWith(`${item}/`),
  );
  if (!root) {
    return null;
  }
  const abs = normalize(`${repoRoot}${sep}${posix.split("/").join(sep)}`);
  const rel = toPosixRel(relative(repoRoot, abs));
  if (isAbsolute(rel) || rel.startsWith("..") || rel.includes("..")) {
    return null;
  }
  const parts = rel.split("/");
  if (parts.some((part) => isDeniedSegment(part))) {
    return null;
  }
  return rel;
}
