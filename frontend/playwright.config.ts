import { defineConfig, devices } from '@playwright/test';

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
    {
      name: 'razr-portrait',
      testIgnore: /demo-recording\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], viewport: { width: 412, height: 919 }, hasTouch: true, isMobile: true },
    },
    {
      name: 'iphone-se',
      testIgnore: /demo-recording\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], viewport: { width: 375, height: 667 }, hasTouch: true, isMobile: true },
    },
    {
      name: 'pixel-7',
      testIgnore: /demo-recording\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], viewport: { width: 412, height: 915 }, hasTouch: true, isMobile: true },
    },
    {
      name: 'tablet',
      testIgnore: /demo-recording\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], viewport: { width: 768, height: 1024 } },
    },
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
  ],
});
