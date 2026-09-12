import { describe, expect, it } from "vitest";
import { isMissingObjectId, pathNeedsHttp404 } from "../src/lib/object-id";

describe("HTTP 404 identity", () => {
  it("rejects reserved and unsafe IDs", () => {
    expect(isMissingObjectId("K0000")).toBe(true);
    expect(isMissingObjectId("P0000")).toBe(true);
    expect(isMissingObjectId("M0000")).toBe(true);
    expect(isMissingObjectId("../P0001")).toBe(true);
    expect(isMissingObjectId("P0001")).toBe(false);
  });

  it("maps reserved object routes to HTTP 404", () => {
    expect(pathNeedsHttp404("/knowledge/K0000")).toBe(true);
    expect(pathNeedsHttp404("/problems/P0000")).toBe(true);
    expect(pathNeedsHttp404("/methods/M0000")).toBe(true);
    expect(pathNeedsHttp404("/knowledge/K0001")).toBe(false);
    expect(pathNeedsHttp404("/knowledge/K9999")).toBe(false);
    expect(pathNeedsHttp404("/problems/new")).toBe(false);
    expect(pathNeedsHttp404("/research/_模板")).toBe(true);
    expect(pathNeedsHttp404("/knowledge/../P0001")).toBe(true);
  });
});
