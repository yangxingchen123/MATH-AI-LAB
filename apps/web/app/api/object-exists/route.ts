import { NextResponse } from "next/server";
import { isReservedId, isUnsafeId } from "@math-ai-lab/domain";
import { getRepository } from "../../../src/lib/repo";

export const runtime = "nodejs";

export function GET(request: Request) {
  const url = new URL(request.url);
  const kind = url.searchParams.get("kind") ?? "";
  const id = url.searchParams.get("id") ?? "";
  if (!id || isUnsafeId(id) || isReservedId(id)) {
    return NextResponse.json({ exists: false });
  }
  const repo = getRepository();
  let exists = false;
  if (kind === "knowledge") exists = repo.getKnowledge(id) != null;
  else if (kind === "problems") exists = repo.getProblem(id) != null;
  else if (kind === "methods") exists = repo.getMethod(id) != null;
  else if (kind === "research") exists = repo.getResearch(id) != null;
  return NextResponse.json({ exists });
}
