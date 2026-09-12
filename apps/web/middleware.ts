import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { pathNeedsHttp404, shouldProbeObject } from "./src/lib/object-id";

export async function middleware(request: NextRequest) {
  if (pathNeedsHttp404(request.nextUrl.pathname)) {
    const url = request.nextUrl.clone();
    url.pathname = "/http-404";
    return NextResponse.rewrite(url, { status: 404 } as never);
  }
  const probe = shouldProbeObject(request.nextUrl.pathname);
  if (probe) {
    const existsUrl = request.nextUrl.clone();
    existsUrl.pathname = "/api/object-exists";
    existsUrl.search = `?kind=${encodeURIComponent(probe.kind)}&id=${encodeURIComponent(probe.id)}`;
    try {
      const response = await fetch(existsUrl, { headers: { "x-internal-probe": "1" } });
      const data = (await response.json()) as { exists?: boolean };
      if (!data.exists) {
        const url = request.nextUrl.clone();
        url.pathname = "/http-404";
        return NextResponse.rewrite(url, { status: 404 } as never);
      }
    } catch {
      const url = request.nextUrl.clone();
      url.pathname = "/http-404";
      return NextResponse.rewrite(url, { status: 404 } as never);
    }
  }
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/knowledge/:path*",
    "/problems/:path*",
    "/methods/:path*",
    "/research/:path*",
  ],
};
