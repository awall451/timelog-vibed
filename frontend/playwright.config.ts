import { defineConfig, devices } from '@playwright/test';

/**
 * Cross-browser coverage:
 *
 * - Chromium / Firefox at iPhone-13 + Pixel-7 viewports run locally on
 *   any host (Linux/macOS/Windows) — covers Blink + Gecko engines plus
 *   touch/mobile viewport regressions on the smoke-renders spec.
 * - WebKit (Safari engine) is omitted from the local config because
 *   Playwright's WebKit Linux binary requires libicu.so.74, which Arch
 *   and other rolling distros do not ship. To run the smoke spec on
 *   WebKit, use the Playwright Docker image — see CLAUDE.md "Cross-
 *   browser testing" section.
 *
 * Existing mobile-overflow tests stay on the original four mobile/
 * tablet projects (razr, iphone-se, pixel-7, tablet) using Chromium —
 * they only assert layout, so engine variety is not needed there.
 *
 * The demo-recording spec runs only under desktop-record.
 */
export default defineConfig({
  testDir: './tests/e2e',
  globalSetup: './tests/e2e/global-setup.ts',
  fullyParallel: false,
  workers: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://localhost:5174',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'VITE_DEMO_MODE=true npm run dev -- --port 5174 --strictPort',
    url: 'http://localhost:5174',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    stdout: 'pipe',
    stderr: 'pipe',
  },
  projects: [
    // ── Mobile-overflow sweep (Chromium-only, layout-focused) ──────
    {
      name: 'razr-portrait',
      testIgnore: /demo-recording\.spec\.ts|smoke-renders\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], viewport: { width: 412, height: 919 }, hasTouch: true, isMobile: true },
    },
    {
      name: 'iphone-se',
      testIgnore: /demo-recording\.spec\.ts|smoke-renders\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], viewport: { width: 375, height: 667 }, hasTouch: true, isMobile: true },
    },
    {
      name: 'pixel-7',
      testIgnore: /demo-recording\.spec\.ts|smoke-renders\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], viewport: { width: 412, height: 915 }, hasTouch: true, isMobile: true },
    },
    {
      name: 'tablet',
      testIgnore: /demo-recording\.spec\.ts|smoke-renders\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], viewport: { width: 768, height: 1024 } },
    },

    // ── Demo recording (desktop-only, video on) ─────────────────────
    {
      name: 'desktop-record',
      testMatch: /demo-recording\.spec\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
        video: { mode: 'on', size: { width: 1280, height: 720 } },
        launchOptions: { slowMo: 250 },
      },
    },

    // ── Cross-browser smoke (Chromium + Firefox at phone viewports) ─
    {
      name: 'chromium-iphone-13',
      testMatch: /smoke-renders\.spec\.ts/,
      use: { ...devices['iPhone 13'], browserName: 'chromium' },
    },
    {
      name: 'firefox-iphone-13',
      testMatch: /smoke-renders\.spec\.ts/,
      use: {
        browserName: 'firefox',
        viewport: { width: 390, height: 844 },
        userAgent:
          'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
      },
    },
    {
      name: 'chromium-pixel-7',
      testMatch: /smoke-renders\.spec\.ts/,
      use: { ...devices['Pixel 7'] },
    },
    {
      name: 'firefox-pixel-7',
      testMatch: /smoke-renders\.spec\.ts/,
      use: {
        browserName: 'firefox',
        viewport: { width: 412, height: 915 },
        userAgent:
          'Mozilla/5.0 (Android 14; Mobile; rv:128.0) Gecko/128.0 Firefox/128.0',
      },
    },
  ],
});
