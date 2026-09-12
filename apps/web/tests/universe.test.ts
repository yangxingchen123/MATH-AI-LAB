import { describe, expect, it } from "vitest";
import { createRepository } from "@math-ai-lab/content";
import { universeFromRepository } from "../src/lib/universe";

describe("universe projection safety", () => {
  it("does not invent theorems or proves-relations from KM objects", () => {
    const snap = universeFromRepository(createRepository());
    expect(snap.entities.some((row) => row.type === "theorem")).toBe(false);
    expect(snap.relations.some((row) => row.type === "proves")).toBe(false);
    expect(snap.candidates.every((row) => row.origin === "lab")).toBe(true);
  });
});
