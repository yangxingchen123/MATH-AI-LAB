import { defineConfig, devices } from "@playwright/test";

const port = Number(process.env.WEB_PORT || 3002);
const baseURL = `http://127.0.0.1:${port}`;

export default defineConfig({
  testDir: "e2e",
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL,
    viewport: { width: 1440, height: 900 },
    locale: "zh-CN",
    trace: "retain-on-failure",
  },
  webServer: {
    command: process.env.CI
      ? `npx next start -p ${port}`
      : `npx next dev -p ${port}`,
    cwd: "apps/web",
    url: baseURL,
    reuseExistingServer: process.env.PW_REUSE === "1",
    timeout: 180_000,
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        channel: process.env.PW_CHANNEL || (process.env.CI ? undefined : "msedge"),
      },
    },
  ],
});
