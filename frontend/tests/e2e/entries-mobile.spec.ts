import { expect, test } from '@playwright/test';

test.describe('mobile layout — /entries', () => {
  test('hours column stays inside viewport, no horizontal page overflow, nav fits', async ({ page }, testInfo) => {
    await page.goto('/entries');

    // Demo mode hydrates sql.js client-side. Wait for either entries or empty-state.
    await page.waitForLoadState('networkidle');
    await page.waitForFunction(
      () => document.querySelector('td.hours') !== null || document.querySelector('.empty') !== null,
      undefined,
      { timeout: 15_000 }
    );

    const vw = testInfo.project.use.viewport!.width;

    // Assertion 1: no horizontal page overflow.
    const docOverflow = await page.evaluate(() => {
      const root = document.documentElement;
      return root.scrollWidth - root.clientWidth;
    });
    expect.soft(docOverflow, 'document horizontal overflow').toBeLessThanOrEqual(0);

    // Assertion 2: top nav fits within its container (no horizontal scroll on nav).
    const navOverflow = await page.evaluate(() => {
      const nav = document.querySelector('header nav') as HTMLElement | null;
      if (!nav) return 0;
      return nav.scrollWidth - nav.clientWidth;
    });
    expect.soft(navOverflow, 'nav horizontal overflow').toBeLessThanOrEqual(0);

    // Assertion 3: hours cell — if any rows rendered — sits fully within viewport width.
    const hasRows = await page.locator('td.hours').count();
    if (hasRows > 0) {
      const cell = page.locator('td.hours').first();
      const box = await cell.boundingBox();
      expect(box, 'hours cell boundingBox').not.toBeNull();
      const right = box!.x + box!.width;
      expect.soft(right, `hours cell right edge (vw=${vw})`).toBeLessThanOrEqual(vw);
    }
  });

  test('footer not occluded by fixed timer or settings widgets', async ({ page }, testInfo) => {
    test.skip(testInfo.project.name === 'tablet', 'desktop/tablet layout intentionally allows widget overlap');

    await page.goto('/entries');
    await page.waitForLoadState('networkidle');
    await page.waitForFunction(
      () => document.querySelector('.footer') !== null || document.querySelector('.empty') !== null,
      undefined,
      { timeout: 15_000 }
    );

    const footerCount = await page.locator('.footer').count();
    if (footerCount === 0) test.skip(true, 'no entries → no footer to test');

    // Scroll footer into view at the bottom of the viewport.
    await page.locator('.footer').scrollIntoViewIfNeeded();
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(200);

    const footer = await page.locator('.footer').boundingBox();
    const timer = await page.locator('.sprite-btn').boundingBox();
    const settings = await page.locator('.settings-btn').boundingBox();
    expect(footer, 'footer boundingBox').not.toBeNull();

    type Box = { x: number; y: number; width: number; height: number };
    const intersects = (a: Box, b: Box) =>
      !(a.x + a.width <= b.x || b.x + b.width <= a.x || a.y + a.height <= b.y || b.y + b.height <= a.y);

    if (timer)    expect.soft(intersects(footer!, timer),    'footer overlaps timer widget').toBeFalsy();
    if (settings) expect.soft(intersects(footer!, settings), 'footer overlaps settings button').toBeFalsy();
  });
});
