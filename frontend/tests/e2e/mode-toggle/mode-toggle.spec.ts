/**
 * Vesper Desktop — App Mode Toggle E2E Tests
 *
 * Tests that the Solo/Coder mode bar is hidden in default Vesper Lite edition,
 * and functions when Full Solo edition is explicitly unlocked.
 *
 * Backend: http://127.0.0.1:18741
 * Frontend: http://localhost:1420
 */
import { test, expect } from "@playwright/test";

const BACKEND_URL = "http://127.0.0.1:18741";

// MODE-00: Top Solo/Coder pill is hidden by default in Vesper Lite
test("MODE-00: app mode pill is hidden by default in Vesper Lite", async ({ page }) => {
  await fetch(`${BACKEND_URL}/api/v1/desktop/switch-lite`, { method: "POST" }).catch(() => {});
  await page.goto("/");
  await page.evaluate(() => {
    localStorage.setItem("contextuai.edition.unlocked", "lite");
  });
  await page.reload();
  await page.waitForLoadState("networkidle");

  const modeToggle = page.locator('[role="tablist"][aria-label="Application mode"]');
  await expect(modeToggle).toHaveCount(0);
});

test.describe("Full Solo unlocked", () => {
  test.beforeAll(async () => {
    const res = await fetch(`${BACKEND_URL}/api/v1/desktop/unlock-solo`, { method: "POST" });
    if (!res.ok) {
      throw new Error(`unlock-solo failed with status ${res.status}`);
    }
  });

  test.afterAll(async () => {
    await fetch(`${BACKEND_URL}/api/v1/desktop/switch-lite`, { method: "POST" }).catch(() => {});
  });

  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.evaluate(() => {
      localStorage.setItem("contextuai.edition.unlocked", "solo");
      localStorage.setItem("solo.app.mode", "solo");
    });
    await page.reload();
    await page.waitForLoadState("networkidle");
  });

  // MODE-01: Top-center pill shows current app mode when Full Solo is unlocked
  test("MODE-01: app mode pill is visible at top center", async ({ page }) => {
    const modeToggle = page.locator('[role="tablist"][aria-label="Application mode"]');
    await expect(modeToggle).toBeVisible({ timeout: 5000 });
  });

  // MODE-02: Clicking mode pill toggles between Solo and Coder
  test("MODE-02: clicking mode pill toggles modes", async ({ page }) => {
    const coderBtn = page.getByRole("tab", { name: "Coder" });

    const initialMode = await page.evaluate(() => localStorage.getItem("solo.app.mode"));
    expect(initialMode).toBe("solo");

    await coderBtn.click();
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(500);

    const newMode = await page.evaluate(() => localStorage.getItem("solo.app.mode"));
    expect(newMode).toBe("coder");
  });

  // MODE-03: Mode persists after page reload
  test("MODE-03: app mode persists after reload", async ({ page }) => {
    const coderBtn = page.getByRole("tab", { name: "Coder" });
    const currentMode = await page.evaluate(() => localStorage.getItem("solo.app.mode"));
    if (currentMode === "solo") {
      await coderBtn.click();
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(500);
    }

    await page.reload();
    await page.waitForLoadState("networkidle");

    const mode = await page.evaluate(() => localStorage.getItem("solo.app.mode"));
    expect(mode).toBe("coder");
  });

  // MODE-04: Coder mode shows coder-specific sidebar
  test("MODE-04: coder mode displays coder sidebar", async ({ page }) => {
    const coderBtn = page.getByRole("tab", { name: "Coder" });
    await coderBtn.click();
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(500);

    const sidebar = page.locator("aside");
    await expect(sidebar).toBeVisible();

    const navLinks = sidebar.locator("a");
    const linkCount = await navLinks.count();
    expect(linkCount).toBeGreaterThan(0);
  });
});
