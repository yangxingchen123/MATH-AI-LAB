import { expect, test } from "@playwright/test";

const visual = process.env.PLAYWRIGHT_VISUAL === "1";

test.describe("visual baselines", () => {
  test.skip(!visual, "set PLAYWRIGHT_VISUAL=1 to refresh local baselines");

  test.use({
    reducedMotion: "reduce",
  });

  test("home", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto("/");
    await expect(page).toHaveScreenshot("home.png", { maxDiffPixelRatio: 0.03 });
  });

  test("problem P0002", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto("/problems/P0002");
    await expect(page).toHaveScreenshot("problem-p0002.png", {
      maxDiffPixelRatio: 0.03,
    });
  });

  test("knowledge K0001", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto("/knowledge/K0001");
    await expect(page).toHaveScreenshot("knowledge-k0001.png", {
      maxDiffPixelRatio: 0.03,
    });
  });

  test("research dossier", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto("/research/" + encodeURIComponent("美赛2026-A"));
    await expect(page).toHaveScreenshot("research-dossier.png", {
      maxDiffPixelRatio: 0.03,
    });
  });

  test("mobile problem", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/problems/P0002");
    await expect(page).toHaveScreenshot("problem-mobile.png", {
      maxDiffPixelRatio: 0.03,
    });
  });

  test("dark problem", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.addInitScript(() => {
      localStorage.setItem("math-ai-lab-theme", "dark");
    });
    await page.goto("/problems/P0002");
    await expect(page).toHaveScreenshot("problem-dark.png", {
      maxDiffPixelRatio: 0.03,
    });
  });
});
