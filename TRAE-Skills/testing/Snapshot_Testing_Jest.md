# Skill: Snapshot Testing (Jest)

## Purpose
To ensure that your UI components or data structures don't change unexpectedly. Snapshot testing records the rendered output of a component and compares it against a saved "baseline" version in future test runs.

## When to Use
- When testing React, Vue, or Angular components to catch unintended HTML/CSS changes
- When validating complex JSON API responses that have a stable structure
- To document the expected output of a function without writing dozens of manual assertions

## Procedure

### 1. Basic Component Snapshot
Use `toMatchSnapshot()` in your Jest tests.

```tsx
import { render } from '@testing-library/react';
import { MyComponent } from './MyComponent';

test('renders correctly', () => {
  const { asFragment } = render(<MyComponent name="John" />);
  
  // The first time this runs, Jest creates a __snapshots__ folder
  // Subsequent runs will compare the output against that file
  expect(asFragment()).toMatchSnapshot();
});
```

### 2. Snapshotting Data Structures
Snapshots aren't just for UI. They are great for complex objects.

```javascript
test('api response has correct shape', () => {
  const complexObject = generateReport(data);
  expect(complexObject).toMatchSnapshot();
});
```

### 3. Inline Snapshots
If the output is small, use `toMatchInlineSnapshot()` to keep the baseline directly in your test file.

```javascript
test('formats currency', () => {
  const result = formatCurrency(10.5);
  // Jest will automatically fill in the string below
  expect(result).toMatchInlineSnapshot(`"$10.50"`);
});
```

### 4. Updating Snapshots
When you intentionally change a component's design, update the snapshots via CLI.

```bash
npm test -- -u
# or
jest --updateSnapshot
```

## Best Practices
- **Small Snapshots**: Avoid snapshotting massive components or pages. They become "walls of text" that developers just update without reviewing.
- **Review the Diff**: When a snapshot fails, carefully read the diff in the terminal. Don't just run `-u` to make it go away.
- **Use Descriptive Test Names**: The snapshot file uses the test name to identify the baseline.
- **Don't use for dynamic data**: Avoid snapshotting objects that contain random IDs, dates, or timestamps. Use `expect.any(Number)` or `expect.stringMatching()` to handle dynamic parts.
  ```javascript
  expect(user).toMatchSnapshot({
    createdAt: expect.any(Date),
    id: expect.any(String)
  });
  ```