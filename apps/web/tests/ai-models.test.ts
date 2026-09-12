import { describe, expect, it } from "vitest";
import { parseAiPrefs, selectionLabel } from "../src/lib/ai-models";

describe("AI model prefs", () => {
  it("keeps a valid catalog selection", () => {
    const prefs = parseAiPrefs({ provider: "xai", model: "grok-4.6" });
    expect(prefs.provider).toBe("xai");
    expect(prefs.model).toBe("grok-4.6");
    expect(selectionLabel(prefs)).toContain("Grok 4.6");
  });

  it("falls back when the provider is unknown", () => {
    const prefs = parseAiPrefs({ provider: "nope", model: "x" });
    expect(prefs.provider).toBe("cursor");
    expect(prefs.model).toBe("auto");
  });

  it("keeps a custom model name", () => {
    const prefs = parseAiPrefs({ provider: "custom", custom_model: "my-local-70b" });
    expect(prefs.custom_model).toBe("my-local-70b");
    expect(selectionLabel(prefs)).toContain("my-local-70b");
  });
});
