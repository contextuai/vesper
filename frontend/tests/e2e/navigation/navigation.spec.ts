/**
 * Vesper Desktop — Navigation E2E Tests
 *
 * Tests the streamlined 5-tab Vesper sidebar navigation and opt-in Advanced Mode.
 * Frontend: http://localhost:1420 (Vite SPA)
 */
import { test, expect } from "@playwright/test";
import { NavigationPage } from "../fixtures/page-objects";
import { EXPECTED_NAV_LABELS } from "../fixtures/page-objects/navigation.page";

let nav: NavigationPage;

test.beforeEach(async ({ page }) => {
  nav = new NavigationPage(page);
  await nav.goto();
});

// DC-NAV-01: Sidebar shows the 5 core Vesper navigation items by default
test("DC-NAV-01: sidebar shows all navigation items", async () => {
  await expect(nav.sidebar).toBeVisible();

  const labels = await nav.getNavLabels();
  for (const item of EXPECTED_NAV_LABELS) {
    expect(labels).toContain(item);
  }
  expect(labels.length).toBe(5);

  for (const hidden of [
    "Distributions",
    "Local Server",
    "Agents",
    "Workspace",
    "Automations",
  ]) {
    expect(labels).not.toContain(hidden);
  }
});

// DC-NAV-02: Navigate to each core page and verify heading
test("DC-NAV-02: navigate to each page and verify heading", async ({ page }) => {
  const routes: { label: string; heading: string | RegExp }[] = [
    {
      label: "Chat",
      heading:
        /Vesper Sovereign AI Workstation|Start a conversation|Set up an AI model to start chatting/,
    },
    { label: "Local Docs", heading: /Local Docs & RAG|Knowledge Bases/ },
    { label: "Models", heading: "Model Hub" },
    { label: "Tools & MCP", heading: /Connectors & MCP|Connectors/ },
    { label: "Settings", heading: "Settings" },
  ];

  for (const route of routes) {
    await nav.navigateTo(route.label);
    await page.waitForTimeout(300);

    const headingEl = page.getByText(route.heading).first();
    await expect(headingEl).toBeVisible({ timeout: 5000 });
  }
});

// DC-NAV-03: Active page is highlighted in sidebar
test("DC-NAV-03: active page is highlighted in sidebar", async ({ page }) => {
  await nav.navigateTo("Local Docs");
  await page.waitForTimeout(300);

  const docsLink = page.locator("aside nav a", { hasText: "Local Docs" });
  const classes = await docsLink.getAttribute("class");
  expect(classes).toContain("primary");

  await nav.navigateTo("Settings");
  await page.waitForTimeout(300);

  const settingsLink = page.locator("aside nav a", { hasText: "Settings" });
  const settingsClasses = await settingsLink.getAttribute("class");
  expect(settingsClasses).toContain("primary");

  const docsClassesAfter = await docsLink.getAttribute("class");
  expect(docsClassesAfter).not.toContain("bg-primary");
});

// DC-NAV-04: Sidebar collapse/expand toggle works
test("DC-NAV-04: sidebar collapse/expand toggle works", async ({ page }) => {
  await expect(nav.sidebar).toBeVisible();

  await expect(page.locator("aside", { hasText: "Vesper" })).toBeVisible();

  // Collapse
  await nav.collapseToggle.click();
  await page.waitForTimeout(500);

  const sidebar = nav.sidebar;
  const box = await sidebar.boundingBox();
  expect(box).toBeTruthy();
  expect(box!.width).toBeLessThan(100);

  const labels = await nav.getNavLabels();
  expect(labels.length).toBe(0);

  // Expand
  await nav.collapseToggle.click();
  await page.waitForTimeout(500);

  const expandedBox = await sidebar.boundingBox();
  expect(expandedBox!.width).toBeGreaterThan(100);

  const expandedLabels = await nav.getNavLabels();
  expect(expandedLabels.length).toBe(5);
});

// DC-NAV-05: Page transitions are smooth & Advanced Mode toggles hidden surfaces
test("DC-NAV-05: page transitions are smooth", async ({ page }) => {
  for (const route of EXPECTED_NAV_LABELS) {
    await nav.navigateTo(route);
    await page.waitForTimeout(300);

    await expect(nav.sidebar).toBeVisible();

    const hasError = await page
      .locator("text=/Something went wrong|Unhandled/i")
      .isVisible()
      .catch(() => false);
    expect(hasError).toBeFalsy();
  }

  // Toggle Advanced Mode ON/OFF under Settings -> Developer
  await page.goto("/settings?tab=developer");
  await page.waitForLoadState("networkidle");

  const advToggle = page.locator('[aria-label="Toggle Advanced Mode"]');
  await expect(advToggle).toBeVisible({ timeout: 5000 });
  await advToggle.click();

  const advancedLabels = ["Agents", "Workspace", "Automations", "Memory", "Approvals"];
  for (const label of advancedLabels) {
    await expect(
      page.locator("aside nav a", { hasText: label }).first()
    ).toBeVisible({ timeout: 5000 });
  }

  // Leave Advanced Mode OFF at the end of the test
  await advToggle.click();
  for (const label of advancedLabels) {
    await expect(
      page.locator("aside nav a", { hasText: label })
    ).toHaveCount(0);
  }
});
