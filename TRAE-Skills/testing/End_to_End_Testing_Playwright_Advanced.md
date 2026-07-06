# Skill: Advanced E2E Testing with Playwright

## Purpose
To implement comprehensive end-to-end testing with Playwright, including visual regression, API testing, and CI/CD integration.

## When to Use
- For testing complex user flows across browsers
- When you need reliable cross-browser testing
- For visual regression testing
- When integrating E2E tests into CI/CD pipelines
- For testing performance and accessibility

## Procedure

### 1. Basic E2E Test
Create a simple Playwright test.

```typescript
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should login successfully with valid credentials', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Fill form
    await page.fill('#email', 'test@example.com');
    await page.fill('#password', 'testpassword123');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Verify login
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Welcome back');
  });
  
  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('#email', 'wrong@example.com');
    await page.fill('#password', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page.locator('.error-message')).toContainText('Invalid credentials');
  });
});
```

### 2. Page Object Model (POM)
Organize tests with Page Object Model.

```typescript
import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('#email');
    this.passwordInput = page.locator('#password');
    this.submitButton = page.locator('button[type="submit"]');
    this.errorMessage = page.locator('.error-message');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}

export class DashboardPage {
  readonly page: Page;
  readonly welcomeMessage: Locator;
  readonly logoutButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.welcomeMessage = page.locator('h1');
    this.logoutButton = page.locator('#logout');
  }

  async logout() {
    await this.logoutButton.click();
  }
}

// Usage in test
test('login with POM', async ({ page }) => {
  const loginPage = new LoginPage(page);
  const dashboardPage = new DashboardPage(page);
  
  await loginPage.goto();
  await loginPage.login('test@example.com', 'testpassword123');
  
  await expect(dashboardPage.welcomeMessage).toContainText('Welcome back');
});
```

### 3. Visual Regression Testing
Test visual changes.

```typescript
import { test, expect } from '@playwright/test';

test.describe('Visual Regression', () => {
  test('homepage should look correct', async ({ page }) => {
    await page.goto('/');
    
    // Full page screenshot
    await expect(page).toHaveScreenshot('homepage.png', {
      fullPage: true,
      threshold: 0.2 // Allow 0.2% pixel difference
    });
  });
  
  test('dashboard should match design', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Screenshot of specific element
    const chart = page.locator('#main-chart');
    await expect(chart).toHaveScreenshot('dashboard-chart.png');
  });
});
```

### 4. API Testing
Test APIs with Playwright.

```typescript
import { test, expect } from '@playwright/test';

test.describe('API Tests', () => {
  test('GET /api/users should return users', async ({ request }) => {
    const response = await request.get('/api/users');
    
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(200);
    
    const users = await response.json();
    expect(users.length).toBeGreaterThan(0);
    expect(users[0]).toHaveProperty('id');
    expect(users[0]).toHaveProperty('name');
  });
  
  test('POST /api/users should create user', async ({ request }) => {
    const newUser = {
      name: 'Test User',
      email: 'testuser@example.com'
    };
    
    const response = await request.post('/api/users', {
      data: newUser
    });
    
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(201);
    
    const createdUser = await response.json();
    expect(createdUser.name).toBe(newUser.name);
    expect(createdUser.email).toBe(newUser.email);
  });
});
```

### 5. Accessibility Testing
Test for accessibility violations.

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility Tests', () => {
  test('homepage should have no accessibility violations', async ({ page }) => {
    await page.goto('/');
    
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });
  
  test('login form should be accessible', async ({ page }) => {
    await page.goto('/login');
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .include('#login-form')
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });
});
```

### 6. Performance Testing
Test performance metrics.

```typescript
import { test, expect } from '@playwright/test';

test.describe('Performance Tests', () => {
  test('page should load within acceptable time', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/');
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(3000); // Less than 3 seconds
  });
  
  test('should meet Core Web Vitals', async ({ page }) => {
    await page.goto('/');
    
    const lcp = await page.evaluate(() => {
      return new Promise(resolve => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          resolve(lastEntry.startTime);
        }).observe({ entryTypes: ['largest-contentful-paint'] });
      });
    });
    
    const fid = await page.evaluate(() => {
      return new Promise(resolve => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          resolve(entries[0].processStart - entries[0].startTime);
        }).observe({ entryTypes: ['first-input'] });
      });
    });
    
    expect(Number(lcp)).toBeLessThan(2500);
    expect(Number(fid)).toBeLessThan(100);
  });
});
```

### 7. CI/CD Integration
Configure Playwright for GitHub Actions.

```yaml
name: Playwright Tests
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: '18'
    - name: Install dependencies
      run: npm ci
    - name: Install Playwright browsers
      run: npx playwright install --with-deps
    - name: Start application
      run: npm run start &
    - name: Wait for application
      run: npx wait-on http://localhost:3000
    - name: Run Playwright tests
      run: npx playwright test
    - uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report
        path: playwright-report/
        retention-days: 30
```

## Best Practices
- **Isolate Tests**: Each test should be independent
- **Use POM**: Organize code with Page Object Model
- **Parallel Execution**: Run tests in parallel for speed
- **Retry Flaky Tests**: Use auto-retry for flaky tests
- **Visual Regression**: Use visual tests for UI changes
- **Accessibility**: Always test for accessibility
- **Clean Up**: Use before/after hooks for setup/teardown
- **CI Integration**: Run E2E tests on every commit
