import { expect, test, type Page } from "@playwright/test";

const ROUTES = [
  "/",
  "/knowledge",
  "/knowledge/K0001",
  "/problems",
  "/problems/P0001",
  "/problems/P0002",
  "/methods",
  "/methods/M0001",
  "/research",
  "/research/" + encodeURIComponent("美赛2026-A"),
  "/references",
  "/outputs",
  "/memory",
  "/inbox",
  "/prompts",
  "/repository",
  "/lean",
  "/lab",
  "/universe",
  "/advanced/diagnostics",
  "/search",
  "/settings",
];

const VIEWPORTS = [
  { width: 1920, height: 1080 },
  { width: 1440, height: 900 },
  { width: 1366, height: 768 },
  { width: 768, height: 1024 },
  { width: 390, height: 844 },
];

async function noHorizontalBleed(page: Page) {
  const overflow = await page.evaluate(() => {
    return document.documentElement.scrollWidth - window.innerWidth;
  });
  expect(overflow).toBeLessThanOrEqual(8);
}

test.describe("Human Interface v1 routes", () => {
  for (const route of ROUTES) {
    test(`renders ${route}`, async ({ page }) => {
      const response = await page.goto(route, { waitUntil: "domcontentloaded" });
      expect(response?.ok()).toBeTruthy();
      await expect(page.locator("h1").first()).toBeVisible();
      await noHorizontalBleed(page);
    });
  }

  test("reserved IDs are HTTP 404", async ({ request }) => {
    for (const path of ["/knowledge/K0000", "/problems/P0000", "/methods/M0000"]) {
      const response = await request.get(path);
      expect(response.status(), path).toBe(404);
    }
  });

  test("missing objects are HTTP 404", async ({ request }) => {
    const response = await request.get("/knowledge/K9999");
    expect(response.status()).toBe(404);
  });

  test("P0002 exposes parts and mapping-complete knowledge", async ({ page }) => {
    await page.goto("/problems/P0002");
    await expect(page.getByRole("heading", { name: /P0002 —/ })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Part (a)" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Part (b)" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Part (c)" })).toBeVisible();
    await expect(page.getByText("mapping 已完成，当前没有直接对象")).toBeVisible();
  });

  test("search finds K0001", async ({ page }) => {
    await page.goto("/");
    await page.keyboard.press("Control+K");
    await page.getByPlaceholder("搜索知识、题目、方法、研究").fill("K0001");
    await expect(page.getByRole("option").first()).toBeVisible();
    await page.keyboard.press("Enter");
    await expect(page).toHaveURL(/\/knowledge\/K0001/);
  });

  test("dark mode toggle does not crash problem page", async ({ page }) => {
    await page.goto("/problems/P0002");
    const toggle = page.getByRole("button", { name: /主题|浅色|深色|系统/ });
    if (await toggle.count()) {
      await toggle.first().click();
    }
    await expect(page.getByRole("heading", { name: /P0002/ }).first()).toBeVisible();
  });

  test("mobile navigation opens", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/problems/P0002");
    await page.getByRole("button", { name: "菜单" }).click();
    await expect(page.getByRole("dialog", { name: "导航" })).toBeVisible();
    await expect(page.getByRole("navigation", { name: "主导航" }).getByText("知识")).toBeVisible();
  });

  test("Lean distinguishes verified from source-only", async ({ page }) => {
    await page.goto("/lean");
    await expect(page.getByText("已验证").first()).toBeVisible();
    await expect(page.getByText("源文件存在不等于已验证")).toBeVisible();
  });

  test("outputs page renders", async ({ page }) => {
    await page.goto("/outputs");
    await expect(page.getByRole("heading", { name: "成果" })).toBeVisible();
  });

  test("formula error page still renders surrounding text", async ({ page }) => {
    await page.goto("/knowledge/K0001");
    await expect(page.locator(".markdown-body")).toBeVisible();
  });

  test("Problem Workbench exposes attempt and workflow preview", async ({ page }) => {
    await page.goto("/problems/P0002");
    await expect(page.getByRole("heading", { name: "My Attempts" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "New Attempt" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Move workflow" })).toBeVisible();
    await page.locator("#attempts textarea").fill("E2E preview only, do not persist.");
    await page.getByRole("button", { name: "预览 Attempt" }).click();
    await expect(page.getByRole("dialog", { name: "预览 RecordAttempt" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "预览 RecordAttempt" })).toBeVisible();
    await page.getByRole("button", { name: "取消" }).click();
    await expect(page.getByRole("dialog", { name: "预览 RecordAttempt" })).toHaveCount(0);
  });

  test("create problem form is preview-gated", async ({ page }) => {
    await page.goto("/problems/new");
    await expect(page.getByRole("heading", { name: "创建题目" })).toBeVisible();
    await page.getByLabel("title").fill("E2E 不写入");
    await page.getByLabel("正文").fill("只预览。");
    await page.getByRole("button", { name: "预览" }).click();
    await expect(page.getByRole("dialog", { name: "预览 CreateProblem" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "预览 CreateProblem" })).toBeVisible();
    await page.getByRole("button", { name: "取消" }).click();
  });

  test("exploration briefing stays read-only", async ({ page }) => {
    await page.goto("/explore");
    await expect(page.getByRole("heading", { name: "数学探索" })).toBeVisible();
    await expect(page.getByText("不能把 Candidate 写成 Theorem")).toBeVisible();
    await expect(page.getByText("Wrote Canonical")).toBeVisible();
    await expect(page.getByText("false")).toBeVisible();
    await expect(page.getByRole("heading", { name: "检索过程记录" })).toBeVisible();
  });

  test("universe explorer opens an entity", async ({ page }) => {
    await page.goto("/universe");
    await expect(page.getByRole("heading", { name: "数学宇宙" })).toBeVisible();
    await expect(page.getByText("只读投影")).toBeVisible();
    await expect(page.getByLabel("主导航").getByText("猜想")).toBeVisible();
    const first = page.locator("article table").getByRole("link").first();
    await expect(first).toBeVisible();
    await first.click();
    await expect(page).toHaveURL(/\/universe\//);
    await expect(page.getByRole("heading", { name: "Relations" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Evidence" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "History" })).toBeVisible();
  });

  test("inbox promotion UI exists", async ({ page }) => {
    await page.goto("/inbox");
    await expect(page.getByRole("heading", { name: "收件箱" })).toBeVisible();
  });

  for (const viewport of VIEWPORTS) {
    test(`home fits ${viewport.width}x${viewport.height}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await page.goto("/");
      await noHorizontalBleed(page);
    });
  }
});
