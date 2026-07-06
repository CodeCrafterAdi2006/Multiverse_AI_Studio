# Skill: Performance Testing with Lighthouse

## Purpose
To audit and improve web application performance, accessibility, SEO, and best practices using Google Lighthouse.

## When to Use
- When optimizing web application performance
- For CI/CD integration to catch performance regressions
- When auditing accessibility compliance
- For SEO optimization
- Before launching a new web application

## Procedure

### 1. Run Lighthouse via CLI
Install and run Lighthouse from the command line.

```bash
# Install Lighthouse
npm install -g lighthouse

# Run a full audit
lighthouse https://example.com --view

# Run specific categories
lighthouse https://example.com --view --only-categories=performance,accessibility

# Output to JSON
lighthouse https://example.com --output=json --output-path=./report.json
```

### 2. Lighthouse in CI/CD (GitHub Actions)
Integrate Lighthouse into your CI pipeline.

```yaml
name: Lighthouse
on: [push]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v9
        with:
          configPath: './lighthouserc.json'
          uploadArtifacts: true
          temporaryPublicStorage: true
```

### 3. Lighthouse Configuration
Create a lighthouserc.json configuration file.

```json
{
  "ci": {
    "collect": {
      "url": [
        "http://localhost:3000",
        "http://localhost:3000/about",
        "http://localhost:3000/products"
      ],
      "startServerCommand": "npm start",
      "startServerReadyPattern": "ready on",
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.95 }],
        "categories:seo": ["error", { "minScore": 0.9 }],
        "first-contentful-paint": ["error", { "maxNumericValue": 1800 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }],
        "interactive": ["error", { "maxNumericValue": 3500 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

### 4. Programmatic Usage
Use Lighthouse programmatically in Node.js.

```javascript
const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');

async function runLighthouse(url) {
  const chrome = await chromeLauncher.launch({ chromeFlags: ['--headless'] });
  const options = { logLevel: 'info', output: 'json', port: chrome.port };
  const runnerResult = await lighthouse(url, options);
  
  console.log('Performance score:', runnerResult.lhr.categories.performance.score * 100);
  console.log('Accessibility score:', runnerResult.lhr.categories.accessibility.score * 100);
  
  await chrome.kill();
  return runnerResult;
}

runLighthouse('https://example.com');
```

## Best Practices
- **Multiple Runs**: Run Lighthouse multiple times and average the results
- **Throttling**: Use network and CPU throttling to simulate real-world conditions
- **Clean Environment**: Run audits on a clean browser profile without extensions
- **Baseline**: Establish a performance baseline and monitor against it
- **Prioritize**: Focus on Core Web Vitals (LCP, FID/INP, CLS) first
- **Automate**: Integrate Lighthouse into your CI/CD pipeline to catch regressions early
