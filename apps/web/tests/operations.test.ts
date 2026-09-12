import { describe, expect, it } from "vitest";
import { isLocalOrigin } from "../src/lib/python-bridge";
import { isCreateSegment, pathNeedsHttp404, shouldProbeObject } from "../src/lib/object-id";

describe("operation safety", () => {
  it("allows localhost origins and missing origin", () => {
    expect(isLocalOrigin(null)).toBe(true);
    expect(isLocalOrigin("http://127.0.0.1:3000")).toBe(true);
    expect(isLocalOrigin("http://localhost:3002")).toBe(true);
    expect(isLocalOrigin("https://evil.example")).toBe(false);
  });

  it("does not 404 create routes", () => {
    expect(isCreateSegment("new")).toBe(true);
    expect(pathNeedsHttp404("/problems/new")).toBe(false);
    expect(shouldProbeObject("/problems/new")).toBeNull();
    expect(shouldProbeObject("/problems/P0002")?.id).toBe("P0002");
  });
});
