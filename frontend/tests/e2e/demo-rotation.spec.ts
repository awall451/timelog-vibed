import { test, expect } from '@playwright/test';

/**
 * Demo date rotation — the seed is re-yeared at load so every entry lands in
 * the trailing 365-day window ending today (see src/lib/demo/db.ts reyear()).
 * Guards against the demo silently going stale again: newest entry must be
 * recent, nothing may be in the future, and the window must span a year.
 */

function isoLocal(d: Date): string {
  return d.toLocaleDateString('sv-SE');
}

test('entries are rotated into the trailing year ending today', async ({ page }) => {
  await page.goto('/entries');
  await expect(page.getByRole('heading', { level: 1, name: /^Entries$/ })).toBeVisible();
  // Wait for sql.js to hydrate and rows to render.
  await expect
    .poll(async () => (await page.innerText('body')).match(/\d{4}-\d{2}-\d{2}/g)?.length ?? 0, {
      timeout: 15_000
    })
    .toBeGreaterThan(20);

  const dates = [...new Set((await page.innerText('body')).match(/\d{4}-\d{2}-\d{2}/g) ?? [])].sort();
  const oldest = dates[0];
  const newest = dates[dates.length - 1];

  const today = new Date();
  const todayIso = isoLocal(today);
  const weekAgo = isoLocal(new Date(today.getTime() - 6 * 86_400_000));
  const yearAgo = isoLocal(new Date(today.getTime() - 366 * 86_400_000));

  expect(newest <= todayIso, `newest ${newest} must not be in the future (today ${todayIso})`).toBe(true);
  expect(newest >= weekAgo, `newest ${newest} is stale (today ${todayIso})`).toBe(true);
  expect(oldest >= yearAgo, `oldest ${oldest} is older than a year (today ${todayIso})`).toBe(true);
});
