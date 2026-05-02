import { expect, test } from '@playwright/test';

const ROUTES = [
  '/',
  '/entries',
  '/charts',
  '/log',
  '/sync',
  '/settings',
  '/settings/general',
  '/settings/appearance',
  '/settings/timer',
  '/settings/storage',
  '/settings/ai-sync',
];

test.describe('mobile sweep — no horizontal overflow', () => {
  for (const route of ROUTES) {
    test(`route ${route}`, async ({ page }, info) => {
      test.skip(info.project.name === 'tablet', 'sweep is mobile-only');

      await page.goto(route);
      await page.waitForLoadState('networkidle');
      // small settle for sql.js hydration / client-side fetches
      await page.waitForTimeout(300);

      const docOverflow = await page.evaluate(() => {
        const r = document.documentElement;
        return r.scrollWidth - r.clientWidth;
      });
      expect.soft(docOverflow, `${route}: documentElement horizontal overflow`).toBeLessThanOrEqual(0);

      const bodyOverflow = await page.evaluate(() => {
        const b = document.body;
        return b.scrollWidth - b.clientWidth;
      });
      expect.soft(bodyOverflow, `${route}: body horizontal overflow`).toBeLessThanOrEqual(0);

      const navOverflow = await page.evaluate(() => {
        const n = document.querySelector('header nav') as HTMLElement | null;
        return n ? n.scrollWidth - n.clientWidth : 0;
      });
      expect.soft(navOverflow, `${route}: nav horizontal overflow`).toBeLessThanOrEqual(0);
    });
  }
});
