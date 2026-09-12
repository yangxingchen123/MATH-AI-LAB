import { describe, expect, it } from "vitest";
import type { Candidate } from "@math-ai-lab/domain-math";
import {
  conjectureIsTheorem,
  fromCandidate,
  transitionConjecture,
} from "../src/index.ts";

const human = { type: "Human" as const, id: "冲" };
const ai = { type: "AI" as const, id: "mock" };
const stamp = "2026-09-09T16:00+08:00";

function aiCandidate(): Candidate {
  return {
    id: "candidate:ai_mock:suggest:gap",
    title: "AI candidate: gap",
    proposedType: "conjecture",
    status: "idea",
    origin: "ai_mock",
  };
}

describe("ConjectureLifecycle", () => {
  it("maps Lab FALSIFICATION notes to challenged, never to a theorem", () => {
    const life = fromCandidate({
      id: "candidate:lab:PROB-SF-001",
      title: "sum-free",
      proposedType: "conjecture",
      status: "exploring",
      origin: "lab",
      notes: "Research Lab Candidate. Not Source. lab_stage=FALSIFICATION",
    });
    expect(life.state).toBe("challenged");
    expect(conjectureIsTheorem(life)).toBe(false);
  });

  it("maps an AI Candidate to generated, never to a theorem", () => {
    const life = fromCandidate(aiCandidate());
    expect(life.state).toBe("generated");
    expect(conjectureIsTheorem(life)).toBe(false);
  });

  it("requires event, actor, and evidence on every transition", () => {
    const life = fromCandidate(aiCandidate());
    const missing = transitionConjecture(life, "exploring", {
      event: "",
      actor: ai,
      evidence: "mock output",
      timestamp: stamp,
    });
    expect(missing.ok).toBe(false);
    const noEvidence = transitionConjecture(life, "exploring", {
      event: "start exploring",
      actor: ai,
      evidence: "",
      timestamp: stamp,
    });
    expect(noEvidence.ok).toBe(false);
  });

  it("never allows AI generated → resolved or AI → supported", () => {
    const start = fromCandidate(aiCandidate());
    const exploring = transitionConjecture(start, "exploring", {
      event: "begin search",
      actor: ai,
      evidence: "ai_mock output, not mathematical evidence",
      timestamp: stamp,
    });
    expect(exploring.ok).toBe(true);
    if (!exploring.ok) return;
    const tested = transitionConjecture(exploring.lifecycle, "tested", {
      event: "ran small n",
      actor: ai,
      evidence: "n<=10 table",
      timestamp: stamp,
    });
    expect(tested.ok).toBe(true);
    if (!tested.ok) return;
    const aiSupported = transitionConjecture(tested.lifecycle, "supported", {
      event: "looks true",
      actor: ai,
      evidence: "heuristic",
      timestamp: stamp,
    });
    expect(aiSupported.ok).toBe(false);
    const skip = transitionConjecture(start, "resolved", {
      event: "declare theorem",
      actor: human,
      evidence: "none",
      timestamp: stamp,
    });
    expect(skip.ok).toBe(false);
  });

  it("allows a Human to support then resolve without writing a theorem", () => {
    let life = fromCandidate({
      id: "candidate:lab:C001",
      title: "lab",
      proposedType: "conjecture",
      status: "exploring",
      origin: "lab",
    });
    const tested = transitionConjecture(life, "tested", {
      event: "checked small cases",
      actor: human,
      evidence: "finite table",
      timestamp: stamp,
    });
    expect(tested.ok).toBe(true);
    if (!tested.ok) return;
    const supported = transitionConjecture(tested.lifecycle, "supported", {
      event: "human review of evidence",
      actor: human,
      evidence: "hand proof sketch",
      timestamp: stamp,
    });
    expect(supported.ok).toBe(true);
    if (!supported.ok) return;
    const resolved = transitionConjecture(supported.lifecycle, "resolved", {
      event: "research question settled",
      actor: human,
      evidence: "human proof in notebook",
      timestamp: stamp,
    });
    expect(resolved.ok).toBe(true);
    if (!resolved.ok) return;
    expect(conjectureIsTheorem(resolved.lifecycle)).toBe(false);
  });
});
