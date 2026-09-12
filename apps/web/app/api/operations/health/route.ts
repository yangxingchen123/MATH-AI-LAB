import { NextResponse } from "next/server";
import { operationHealth } from "../../../../src/lib/python-bridge";

export const runtime = "nodejs";

export function GET() {
  const health = operationHealth();
  return NextResponse.json({
    writes: health.available,
    level: health.available ? "healthy" : "unavailable",
    detail: health.detail,
    operations: health.operations,
  });
}
