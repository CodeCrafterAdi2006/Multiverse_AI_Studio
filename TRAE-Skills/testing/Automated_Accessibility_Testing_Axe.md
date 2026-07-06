# Skill: Automated Accessibility Testing (Axe-core)

## Purpose
To automatically detect web accessibility (a11y) violations—such as missing ARIA attributes, poor color contrast, or missing alt text—during End-to-End (E2E) testing using Deque's [axe-core](https://github.com/dequelabs/axe-core) engine integrated with testing frameworks like Playwright or Cypress.

## When to Use
- When ensuring web applications comply with WCAG (Web Content Accessibility Guidelines) standards
- To catch regressions in accessibility during the CI/CD pipeline before they reach production
- When building reusable UI component libraries (e.g., Storybook)

## Procedure

### 1. Installation (Playwright Example)
Install the official `@axe-core/playwright` package alongside your Playwright setup.

```bash
npm install --save-dev @axe-core/playwright
```

*(Note: For Cypress, use `cypress-axe`; for Jest/React Testing Library, use `jest-axe`.)*

### 2. Writing the Accessibility Test
Create a test file (e.g., `a11y.spec.ts`). You should navigate to a page, inject the axe-core script, run the analysis, and assert that there are zero violations.

```typescript
import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y, getViolations } from 'axe-playwright'; // or @axe-core/playwright

test.describe('Accessibility Tests', () => {

  test('Homepage should not have any automatically detectable accessibility issues', async ({ page }) => {
    // 1. Navigate to the page
    await page.goto('http://localhost:3000');
    
    // Wait for the page to be fully loaded
    await page.waitForLoadState('networkidle');

    // 2. Inject axe-core into the page
    await injectAxe(page);

    // 3. Run the analysis and assert 0 violations
    // checkA11y automatically fails the test if violations are found and prints them to the console
    await checkA11y(page, null, {
      detailedReport: true, // Output detailed violation data
      detailedReportOptions: { html: true }
    });
  });

  test('Specific Component (Modal) should be accessible', async ({ page }) => {
    await page.goto('http://localhost:3000/components');
    
    // Open a modal
    await page.click('button#open-login-modal');
    await page.waitForSelector('#login-modal', { state: 'visible' });

    await injectAxe(page);

    // Run axe only on a specific element instead of the whole page
    await checkA11y(page, '#login-modal', {
      axeOptions: {
        // Run specific WCAG rulesets
        runOnly: {
          type: 'tag',
          values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice']
        }
      }
    });
  });

});
```

### 3. Handling Known Issues (Exclusions)
Sometimes you cannot fix an accessibility issue immediately (e.g., it's in a third-party widget). You can exclude specific CSS selectors or rules to prevent the test from failing while you work on a fix.

```typescript
await checkA11y(page, null, {
  axeOptions: {
    rules: {
      // Temporarily disable color-contrast checks globally
      'color-contrast': { enabled: false }
    }
  }
}, [
  // Exclude a specific third-party iframe from the analysis
  '.third-party-chat-widget'
]);
```

## Best Practices
- **Automated Testing Limitations**: Tools like axe-core can only catch about 30% to 50% of accessibility issues automatically (e.g., missing labels, invalid ARIA). They *cannot* verify if an alt text is actually descriptive, or if the logical tab order makes sense to a screen reader user. Manual testing with screen readers (VoiceOver, NVDA, JAWS) and keyboard navigation is still mandatory.
- **Test States, Not Just Pages**: Accessibility issues often hide inside dynamic states (e.g., expanded dropdowns, open modals, error messages). Ensure your E2E tests interact with the page to reveal these states before running the `checkA11y` assertion.
- **Component Level Testing**: Catch a11y issues early by integrating `jest-axe` or `@storybook/addon-a11y` directly into your component unit tests, rather than waiting for full-page E2E tests.