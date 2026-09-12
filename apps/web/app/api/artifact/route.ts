import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { resolveSafeRel } from "@math-ai-lab/content";
import { NextResponse } from "next/server";
import { getRepository } from "../../../src/lib/repo";

export function GET(request: Request) {
  const url = new URL(request.url);
  const rel = url.searchParams.get("path") ?? "";
  const repo = getRepository();
  const safe = resolveSafeRel(repo.repoRoot, rel, [
    "03_参考资料",
    "08_成果输出",
    "06_LEAN形式化",
    "04_LATEX",
  ]);
  if (!safe) {
    return new NextResponse("Not Found", { status: 404 });
  }
  const abs = join(repo.repoRoot, ...safe.split("/"));
  if (!existsSync(abs)) {
    return new NextResponse("Not Found", { status: 404 });
  }
  const data = new Uint8Array(readFileSync(abs));
  const lower = safe.toLowerCase();
  const type = lower.endsWith(".pdf")
    ? "application/pdf"
    : lower.endsWith(".md")
      ? "text/plain; charset=utf-8"
      : "application/octet-stream";
  return new NextResponse(data, {
    headers: {
      "Content-Type": type,
      "Content-Disposition": `inline; filename="${safe.split("/").pop()}"`,
      "Cache-Control": "private, max-age=60",
    },
  });
}
