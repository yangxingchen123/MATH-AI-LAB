import { describe, expect, it } from "vitest";
import {
  createCounterexample,
  emptyFailureMemory,
  lookupFailures,
  rememberFailure,
} from "../src/index.ts";

describe("FailureMemorySystem", () => {
  it("stores a reusable dead-end and can look it up later", () => {
    const first = rememberFailure(emptyFailureMemory(), {
      id: "fail:compactness-without-hausdorff",
      failedAttempt: "session:1/action:3",
      reason: "compactness used without Hausdorff",
      assumptionFailure: "missing Hausdorff",
      methodFailure: "compactness argument",
      lesson: "Do not invoke compactness uniqueness without separation.",
      relatedFutureResearch: ["dir:separation-axioms"],
    });
    expect(first.ok).toBe(true);
    if (!first.ok) return;
    const hits = lookupFailures(first.memory, { methodFailure: "compactness" });
    expect(hits).toHaveLength(1);
    expect(hits[0]?.lesson).toContain("separation");
  });

  it("rejects incomplete failures and duplicate ids", () => {
    const bad = rememberFailure(emptyFailureMemory(), {
      id: "x",
      failedAttempt: "",
      reason: "r",
      lesson: "l",
      relatedFutureResearch: [],
    });
    expect(bad.ok).toBe(false);
    const once = rememberFailure(emptyFailureMemory(), {
      id: "fail:1",
      failedAttempt: "a",
      reason: "r",
      lesson: "l",
      relatedFutureResearch: [],
    });
    expect(once.ok).toBe(true);
    if (!once.ok) return;
    const twice = rememberFailure(once.memory, {
      id: "fail:1",
      failedAttempt: "a",
      reason: "r",
      lesson: "l",
      relatedFutureResearch: [],
    });
    expect(twice.ok).toBe(false);
  });
});

describe("CounterexampleRecord", () => {
  it("records why a claim failed and what to try next", () => {
    const made = createCounterexample({
      id: "cex:1",
      claim: "All functions satisfying X are continuous",
      counterexample: "Function Y",
      construction: "Indicator of the rationals on [0,1]",
      whyFailure: "X does not imply boundedness",
      lesson: "Missing boundedness assumption",
      futureDirection: "dir:add-boundedness",
    });
    expect(made.ok).toBe(true);
  });
});
