# Skill: Visual Regression Testing (Playwright)

## Purpose
To automatically detect unintended visual changes in a web application's UI by comparing screenshots of the current build against baseline images (snapshots) approved in a previous version.

## When to Use
- When updating CSS, design tokens, or global styles (e.g., Tailwind configuration) that could affect the layout across the entire site
- When ensuring cross-browser rendering consistency
- When refactoring React components to guarantee no visual differences are introduced

## Procedure

### 1. Installation
Install Playwright and its browsers.

```bash
npm init playwright@latest
```

### 2. Configuration
Configure Playwright to handle screenshots correctly. Playwright automatically manages baselines per OS and browser.

**`playwright.config.ts`**
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  // Fail the build on CI if you accidentally left test.only in the source code.
  forbidOnly: !!process.env.CI,
  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  
  use: {
    // Base URL to use in actions like `await page.goto('/')`.
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'] } },
    { name: 'Mobile Safari', use: { ...devices['iPhone 12'] } },
  ],
});
```

### 3. Writing the Test
Create a test file (e.g., `visual.spec.ts`). You can take screenshots of the full page or specific components.

```typescript
import { test, expect } from '@playwright/test';

test.describe('Visual Regression Tests', () => {
  
  test('Homepage layout matches baseline', async ({ page }) => {
    await page.goto('/');
    
    // Wait for network idle or specific elements to ensure the page is fully rendered
    await page.waitForLoadState('networkidle');
    
    // Take a screenshot of the entire page and compare it to the baseline
    // Playwright will create the baseline automatically on the first run
    await expect(page).toHaveScreenshot('homepage-full.png', {
      fullPage: true, // Captures scrolling content
      maxDiffPixels: 100, // Allow minor pixel differences (e.g., anti-aliasing)
    });
  });

  test('Button component matches baseline', async ({ page }) => {
    await page.goto('/components/buttons');
    
    // Select a specific element
    const submitButton = page.locator('button#submit-main');
    
    // Compare only that element's screenshot
    await expect(submitButton).toHaveScreenshot('submit-button.png');
  });

});
```

### 4. Managing Baselines
- **First Run**: Run `npx playwright test`. It will fail because baselines don't exist yet, but it will generate them in the `tests/` directory.
- **Subsequent Runs**: `npx playwright test` will now compare new screenshots against the baselines.
- **Updating Baselines**: When you intentionally change the UI (e.g., changing a button color from blue to green), you must update the baselines.
  ```bash
  npx playwright test --update-snapshots
  ```

## Best Practices
- **Mask Dynamic Content**: Elements that change constantly (dates, clocks, random IDs, third-party ads) will cause false positives. Mask them before taking the screenshot.
  ```typescript
  await expect(page).toHaveScreenshot('dashboard.png', {
    mask: [page.locator('.live-clock'), page.locator('.dynamic-ad-banner')]
  });
  ```
- **Animations and Transitions**: Disable CSS animations before taking screenshots to prevent flakiness. Playwright can inject CSS to do this:
  ```typescript
  await page.addStyleTag({ content: '*, *::before, *::after { animation-duration: 0s !important; transition-duration: 0s !important; }' });
  ```
- **CI/CD Integration**: Always generate baselines on the same OS that your CI uses (e.g., Linux/Ubuntu). Fonts render differently on macOS vs Linux, which will cause snapshot mismatches. Use Docker or Playwright's native GitHub Actions setup to ensure consistency.