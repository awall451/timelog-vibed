import { test, expect } from '@playwright/test';

test.describe.configure({ mode: 'serial' });

test('demo walkthrough', async ({ page }, info) => {
  test.skip(info.project.name !== 'desktop-record', 'recording only on desktop-record');

  // 1. Dashboard — beauty shot
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1500);

  // poster frame for landing page
  await page.screenshot({ path: 'static/demo-poster.png' });

  // hover the bar list to draw the eye
  const barList = page.locator('.bar-list');
  if (await barList.count()) {
    await barList.first().scrollIntoViewIfNeeded();
    await page.waitForTimeout(800);
  }

  // 2. Log a new entry
  await page.goto('/log');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(600);

  await page.locator('#project').click();
  await page.locator('#project').fill('Timelog Demo');
  await page.waitForTimeout(400);

  await page.locator('#category').click();
  await page.locator('#category').fill('Development');
  await page.waitForTimeout(400);

  await page.locator('#description').click();
  await page.locator('#description').fill('Wired up a new chart on the analytics page');
  await page.waitForTimeout(400);

  await page.locator('#hours').click();
  await page.locator('#hours').fill('1.75');
  await page.waitForTimeout(600);

  await page.locator('button[type="submit"]').click();
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1500);

  // 3. Entries — heatmap + table
  await page.goto('/entries');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1500);

  // scroll table into view to show entries
  const table = page.locator('table').first();
  if (await table.count()) {
    await table.scrollIntoViewIfNeeded();
    await page.waitForTimeout(1000);
  }

  // 4. Charts page
  await page.goto('/charts');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2500);

  // scroll through charts
  await page.evaluate(() => window.scrollBy({ top: 400, behavior: 'smooth' }));
  await page.waitForTimeout(1500);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await page.waitForTimeout(800);

  // 5. Theme switching — appearance settings
  await page.goto('/settings/appearance');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(800);

  const themeOrder = ['tokyonight', 'cyberpunk', 'dracula', 'rosepine'];
  for (const theme of themeOrder) {
    const card = page.locator(`button[data-theme-preview="${theme}"]`);
    if (await card.count()) {
      await card.click();
      await page.waitForTimeout(900);
    }
  }

  // 6. Final beauty shot back on dashboard
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);

  // soft assertion to keep the test healthy
  await expect(page.locator('h1')).toBeVisible();
});
