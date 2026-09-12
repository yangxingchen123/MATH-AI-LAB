import { existsSync } from "node:fs";
import { join } from "node:path";
import {
  isReservedId,
  resolveContentRef,
  type DiagnosticItem,
  type Knowledge,
  type Method,
  type Problem,
} from "@math-ai-lab/domain";
import { listReferences } from "./references.ts";

export function collectDiagnostics(input: {
  repoRoot: string;
  knowledge: Knowledge[];
  problems: Problem[];
  methods: Method[];
  skips: readonly { sourcePath: string; reason: string }[];
}): DiagnosticItem[] {
  const items: DiagnosticItem[] = [];
  const catalog = new Set([
    ...input.knowledge.map((row) => row.id),
    ...input.problems.map((row) => row.id),
    ...input.methods.map((row) => row.id),
  ]);

  for (const skip of input.skips) {
    if (skip.reason === "parse_error" || skip.reason === "missing_front_matter") {
      items.push({
        type: "parse_error",
        sourcePath: skip.sourcePath,
        explanation:
          skip.reason === "parse_error"
            ? "Front Matter 无法解析，对象未进入正式列表。"
            : "缺少 Front Matter，对象未进入正式列表。",
      });
    }
  }

  const seen = new Map<string, string>();
  for (const item of [...input.knowledge, ...input.problems, ...input.methods]) {
    const previous = seen.get(item.id);
    if (previous) {
      items.push({
        type: "duplicate_id",
        sourcePath: item.sourcePath,
        target: item.id,
        explanation: `ID ${item.id} 与 ${previous} 重复。`,
      });
    } else {
      seen.set(item.id, item.sourcePath);
    }
    if (isReservedId(item.id)) {
      items.push({
        type: "reserved_id",
        sourcePath: item.sourcePath,
        target: item.id,
        explanation: "模板 / 哨兵 ID 不应出现在正式对象中。",
      });
    }
    if (item.unknownFields.length > 0) {
      items.push({
        type: "unknown_field",
        sourcePath: item.sourcePath,
        explanation: `未知 YAML 字段：${item.unknownFields.join(", ")}（未提升为 Schema）。`,
      });
    }
  }

  const checkRefs = (sourcePath: string, refs: string[] | undefined) => {
    for (const ref of refs ?? []) {
      const resolved = resolveContentRef(ref, catalog);
      if (resolved.status === "broken") {
        items.push({
          type: "broken_ref",
          sourcePath,
          target: ref,
          explanation: `引用 ${ref} 无法解析（${resolved.reason}）。`,
        });
      }
    }
  };

  for (const item of input.knowledge) {
    checkRefs(item.sourcePath, item.prerequisites);
    checkRefs(item.sourcePath, item.related);
  }
  for (const item of input.problems) {
    checkRefs(item.sourcePath, item.knowledge);
  }
  for (const item of input.methods) {
    checkRefs(item.sourcePath, item.knowledge);
  }

  for (const ref of listReferences(input.repoRoot)) {
    if (ref.pdfPath && !existsSync(join(input.repoRoot, ...ref.pdfPath.split("/")))) {
      items.push({
        type: "missing_artifact",
        sourcePath: ref.sourcePath,
        target: ref.pdfPath,
        explanation: "identity 记录了 PDF，但文件不存在。",
      });
    }
  }

  return items;
}
