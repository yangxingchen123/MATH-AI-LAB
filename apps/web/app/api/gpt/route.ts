import { NextResponse } from "next/server";
import { isLocalOrigin, runGptCommand } from "../../../src/lib/python-bridge";

export const runtime = "nodejs";

const BLOCKED = new Set(["root", "path", "file", "command", "cwd", "shell", "opener"]);

export async function POST(request: Request) {
  if (!isLocalOrigin(request.headers.get("origin"))) {
    return NextResponse.json({ ok: false, error: "origin not allowed" }, { status: 403 });
  }
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ ok: false, error: "invalid JSON" }, { status: 400 });
  }
  if (!body || typeof body !== "object") {
    return NextResponse.json({ ok: false, error: "invalid body" }, { status: 400 });
  }
  const data = body as Record<string, unknown>;
  for (const key of BLOCKED) {
    if (key in data) {
      return NextResponse.json({ ok: false, error: "request must not set root or command" }, { status: 400 });
    }
  }
  const result = runGptCommand(data);
  const ok = result.ok === true || result.action === "status";
  return NextResponse.json(result, { status: ok ? 200 : 422 });
}
