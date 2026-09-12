import { NextResponse } from "next/server";
import { isDomainOperation } from "@math-ai-lab/domain";
import { isLocalOrigin, runDomainOperation } from "../../../src/lib/python-bridge";

export const runtime = "nodejs";

export async function POST(request: Request) {
  if (!isLocalOrigin(request.headers.get("origin"))) {
    return NextResponse.json({ error: "origin not allowed" }, { status: 403 });
  }
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "invalid JSON" }, { status: 400 });
  }
  if (!body || typeof body !== "object") {
    return NextResponse.json({ error: "invalid body" }, { status: 400 });
  }
  const data = body as Record<string, unknown>;
  if (typeof data.operation !== "string" || !isDomainOperation(data.operation)) {
    return NextResponse.json({ error: "operation is not on the whitelist" }, { status: 400 });
  }
  if (data.root != null || data.cwd != null || data.command != null) {
    return NextResponse.json({ error: "request must not set root or command" }, { status: 400 });
  }
  const payload = data.payload;
  if (payload != null && typeof payload !== "object") {
    return NextResponse.json({ error: "payload must be an object" }, { status: 400 });
  }
  const record = (payload ?? {}) as Record<string, unknown>;
  for (const key of ["root", "path", "file", "command", "cwd", "shell"]) {
    if (key in record) {
      return NextResponse.json({ error: "payload must not include filesystem fields" }, { status: 400 });
    }
  }
  const result = runDomainOperation({
    operation: data.operation,
    preview: Boolean(data.preview),
    requestId: typeof data.requestId === "string" ? data.requestId : crypto.randomUUID(),
    payload: record,
  });
  return NextResponse.json(result, { status: result.success ? 200 : 422 });
}
