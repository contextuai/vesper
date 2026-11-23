/**
 * Vesper Desktop — Retired Connections Redirect & Security/Developer Panels E2E Tests
 *
 * Replaces legacy /connections distribution tests following Issue #75 retirement
 * and verifies Security (DLP, ABOM, Enterprise Policy) and Developer settings tabs.
 */
import { test, expect } from "@playwright/test";

const BACKEND_URL = "http://127.0.0.1:18741";

test.describe("Retired Connections & Vesper v1.2 Settings", () => {
  // DC-CONN-01: Legacy /connections route redirects to /settings
  test("DC-CONN-01: legacy /connections redirects cleanly to /settings", async ({ page }) => {
    await page.goto("/connections");
    await page.waitForURL((url) => url.pathname === "/settings", { timeout: 5000 });
    await expect(page.locator("h1, h2").filter({ hasText: "Settings" }).first()).toBeVisible();
  });

  // DC-CONN-02: Retired social and distribution API endpoints return 404
  test("DC-CONN-02: retired social and distribution API routes return 404", async () => {
    for (const path of [
      "/api/v1/connections",
      "/api/v1/distribution/channels",
      "/api/v1/reddit/account",
      "/api/v1/twitter/account",
    ]) {
      const resp = await fetch(`${BACKEND_URL}${path}`);
      expect(resp.status).toBe(404);
    }
  });

  // DC-CONN-03: Settings -> Security & Audit exposes Local DLP, ABOM export, and Enterprise Policy
  test("DC-CONN-03: security & audit tab renders Local DLP, ABOM, and Enterprise Policy", async ({
    page,
  }) => {
    await page.goto("/settings?tab=security");
    await page.waitForLoadState("networkidle");

    await expect(page.locator('[aria-label="Enable Local DLP"]')).toBeVisible({
      timeout: 5000,
    });
    await expect(page.getByText("ABOM Model Integrity Inventory")).toBeVisible({
      timeout: 10000,
    });
    await expect(page.getByRole("button", { name: /Export JSON/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /Export CSV/i })).toBeVisible();
    await expect(
      page.getByText("Custom Model Catalog URL or Local File Path")
    ).toBeVisible();
  });

  // DC-CONN-04: Settings -> Developer exposes Local /v1 Server and Advanced Mode toggles
  test("DC-CONN-04: developer tab renders Local /v1 Server and Advanced Mode toggles", async ({
    page,
  }) => {
    await page.goto("/settings?tab=developer");
    await page.waitForLoadState("networkidle");

    await expect(
      page.locator('[aria-label="Toggle Local OpenAI /v1 Server"]')
    ).toBeVisible({ timeout: 5000 });
    await expect(
      page.locator('[aria-label="Toggle Advanced Mode"]')
    ).toBeVisible({ timeout: 5000 });
  });
});
