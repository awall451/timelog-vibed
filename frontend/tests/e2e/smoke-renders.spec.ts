import { test, expect, type ConsoleMessage, type Page } from '@playwright/test';

/**
 * Smoke renders — fail-loud test that every public route loads and shows
 * its h1 within a few seconds, with no console errors. Existed precisely
 * because a top-level await regression silently rendered the entire app
 * blank on iOS Safari < 15. A blank-on-load failure mode would not have
 * been caught by the existing mobile-overflow sweep, so this spec exists
 * to assert "did anything actually render?" across browsers.
 */

const ROUTES: { path: string; h1: RegExp }[] = [
  { path: '/',                    h1: /Timelog|Dashboard/i },
  { path: '/dashboard',           h1: /Dashboard/i },
  { path: '/entries',             h1: /Entries/i },
  { path: '/charts',              h1: /Charts|Analytics/i },
  { path: '/log',                 h1: /Log Time/i },
  { path: '/settings',            h1: /Settings|General/i },
  { path: '/settings/general',    h1: /General/i },
  { path: '/settings/appearance', h1: /Appearance/i },
  { path: '/settings/timer',      h1: /Timer/i },
  { path: '/settings/storage',    h1: /Data/i },
  { path: '/settings/ai-sync',    h1: /AI Sync/i },
];

function attachErrorListeners(page: Page): { errors: string[] } {
  const errors: string[] = [];
  page.on('console', (msg: ConsoleMessage) => {
    if (msg.type() === 'error') errors.push(`console.error: ${msg.text()}`);
  });
  page.on('pageerror', (err) => {
    errors.push(`pageerror: ${err.message}`);
  });
  return { errors };
}

test.describe('smoke renders — every route shows its h1, no console errors', () => {
  for (const { path, h1 } of ROUTES) {
    test(`route ${path}`, async ({ page }) => {
      const { errors } = attachErrorListeners(page);
      await page.goto(path);
      await page.waitForLoadState('networkidle');

      // Heading must be visible within 5s — proves the bundle parsed,
      // hydrated, and rendered something (not the blank-on-TLA failure).
      await expect(page.locator('h1').first()).toBeVisible({ timeout: 5000 });
      const text = await page.locator('h1').first().textContent();
      expect.soft(text ?? '', `${path}: h1 text`).toMatch(h1);

      // Allow benign favicon 404 noise; everything else fails the test.
      const meaningful = errors.filter(e => !/favicon|404/i.test(e));
      expect.soft(meaningful, `${path}: console errors`).toEqual([]);
    });
  }
});
