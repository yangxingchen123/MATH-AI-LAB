import { describe, expect, it } from "vitest";
import { isGptAction } from "../src/lib/python-bridge";
import { modelsFor, parseAiPrefs } from "../src/lib/ai-models";

describe("GPT connect whitelist", () => {
  it("allows status connect chat only", () => {
    expect(isGptAction("status")).toBe(true);
    expect(isGptAction("connect")).toBe(true);
    expect(isGptAction("chat")).toBe(true);
    expect(isGptAction("shell")).toBe(false);
    expect(isGptAction("RecordAttempt")).toBe(false);
  });

  it("lists GPT models under openai", () => {
    const ids = modelsFor("openai").map((row) => row.id);
    expect(ids).toContain("gpt-4.1");
    expect(ids).toContain("gpt-4o");
    expect(parseAiPrefs({ provider: "openai", model: "gpt-4o" }).model).toBe("gpt-4o");
  });
});
