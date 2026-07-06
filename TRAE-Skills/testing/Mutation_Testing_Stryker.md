# Skill: Mutation Testing (Stryker)

## Purpose
To measure the true effectiveness of your unit tests. Code coverage only tells you which lines were executed during a test; mutation testing tells you if your tests actually catch bugs when the code changes. [Stryker Mutator](https://stryker-mutator.io/) automatically introduces small changes (mutants) into your code (e.g., changing `+` to `-`, `true` to `false`) and runs your tests. If the tests still pass, the mutant "survived" (bad). If the tests fail, the mutant was "killed" (good).

## When to Use
- On mission-critical logic (e.g., financial calculations, security checks, state machines) where high confidence is required
- When you have high code coverage (>90%) but still experience regressions in production
- To identify meaningless or "assertion-free" tests that execute code but verify nothing

## Procedure

### 1. Installation
Install Stryker and the runner for your testing framework (e.g., Jest).

```bash
npm install --save-dev @stryker-mutator/core @stryker-mutator/jest-runner
```

Initialize Stryker configuration:
```bash
npx stryker init
```
This interactive prompt will create a `stryker.config.json` (or `.js`) file tailored to your project.

### 2. Configuration (`stryker.config.json`)
Configure Stryker to target specific files. Running mutation tests on an entire codebase can be extremely slow because it runs the entire test suite for *every* mutation.

```json
{
  "$schema": "./node_modules/@stryker-mutator/core/schema/stryker-schema.json",
  "packageManager": "npm",
  "reporters": [
    "html",
    "clear-text",
    "progress"
  ],
  "testRunner": "jest",
  "coverageAnalysis": "perTest",
  "mutate": [
    "src/services/**/*.ts",      // Only mutate core logic
    "!src/**/*.test.ts",         // Don't mutate tests
    "!src/index.ts",             // Ignore entry points
    "!src/models/**/*.ts"        // Ignore plain data structures
  ],
  "thresholds": {
    "high": 80,
    "low": 60,
    "break": 50 // Fail the build if mutation score drops below 50%
  }
}
```

### 3. Example of a Survived Mutant
Suppose you have this code:

```typescript
function isEligibleForDiscount(age: number, isMember: boolean): boolean {
  if (age >= 65 || isMember) {
    return true;
  }
  return false;
}
```

And this test:
```typescript
test('eligible if 65', () => {
  expect(isEligibleForDiscount(65, false)).toBe(true);
});
test('eligible if member', () => {
  expect(isEligibleForDiscount(30, true)).toBe(true);
});
```

Stryker might change `>=` to `>`.
```typescript
// Mutant
function isEligibleForDiscount(age: number, isMember: boolean): boolean {
  if (age > 65 || isMember) { // Changed >= to >
    return true;
  }
  return false;
}
```

If you run Stryker, your tests will *fail* (because `isEligibleForDiscount(65, false)` will now return `false`). The mutant is **KILLED** (Good!).

However, if Stryker mutates `||` to `&&`:
```typescript
// Mutant
function isEligibleForDiscount(age: number, isMember: boolean): boolean {
  if (age >= 65 && isMember) { // Changed || to &&
    return true;
  }
  return false;
}
```
If your test suite *doesn't* have a test for `(65, false)` or `(30, true)` specifically asserting the `||` logic correctly, the mutant might **SURVIVE**. This indicates a hole in your test suite.

### 4. Running Stryker
Execute the mutation tests:
```bash
npx stryker run
```

Review the generated HTML report (usually in the `reports/mutation/html/` folder) to see exactly which lines of code were mutated and survived.

## Best Practices
- **Focus on Core Logic**: Do not run mutation testing on UI components, simple CRUD controllers, or configuration files. Focus purely on complex business logic, algorithms, and reducers.
- **Understand the Cost**: Mutation testing is computationally expensive. Run it on CI/CD only for specific critical packages (e.g., in a monorepo) or run it nightly rather than on every PR commit.
- **Don't Aim for 100%**: A mutation score of 100% is rarely practical. Some mutations are "equivalent" (they change the code but not the observable behavior) and are technically impossible to kill. Aim for a high score (80%+) on critical paths.