# Skill: Test Coverage & Quality (Istanbul)

## Purpose
To measure how much of your source code is actually executed when your tests run. Test coverage reports identify "dark zones"—untested branches, functions, or lines—helping you prioritize where to add new tests and reduce the risk of hidden bugs.

## When to Use
- When evaluating the overall health and safety of a project
- To set "quality gates" in CI/CD pipelines (e.g., fail the build if coverage drops below 80%)
- During refactoring to ensure that all branches of a complex function are still tested
- When deciding where to allocate testing resources in a large legacy codebase

## Procedure

### 1. Running Coverage Reports
Most modern testing frameworks (Jest, Vitest, Cypress) have built-in coverage support using **Istanbul** (nyc).

**For Jest**:
```bash
npm test -- --coverage
```

### 2. Understanding the Metrics
Coverage reports typically provide four main metrics:

1. **% Stmts (Statements)**: The percentage of individual executable statements that were run.
2. **% Branch**: The percentage of logic branches (e.g., `if/else`, `switch` cases) that were fully explored. (This is the most important metric for complex logic).
3. **% Funcs (Functions)**: The percentage of defined functions or methods that were called.
4. **% Lines**: The percentage of lines of code that were executed.

### 3. Configuring Coverage (Jest Example)
Use `jest.config.js` to define coverage thresholds and ignore specific files (e.g., configuration, models, or boilerplate).

```javascript
module.exports = {
  collectCoverage: true, // Enable coverage by default
  coverageDirectory: 'coverage', // Output folder
  collectCoverageFrom: [
    'src/**/*.{ts,tsx,js}', // Target all source files
    '!src/**/*.test.ts',      // Don't cover test files
    '!src/index.ts',          // Ignore entry point
    '!src/types/**/*.ts',     // Ignore TypeScript types
    '!src/models/**/*.ts',    // Ignore plain data models
  ],
  // Enforce quality gates
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 85,
      lines: 85,
      statements: 85,
    },
  },
};
```

### 4. Viewing the Report
Jest generates a `coverage/` folder. Open `coverage/lcov-report/index.html` in your browser to see a detailed, color-coded breakdown of every file in your project.
- **Green**: Fully covered.
- **Yellow**: Partially covered (e.g., an `if` was tested, but its `else` branch was not).
- **Red**: Not covered at all.

### 5. Ignoring Specific Lines
Sometimes a line is impossible or unnecessary to test (e.g., a defensive `else` that "should never be reached"). Use Istanbul ignore comments.

```javascript
/* istanbul ignore next */
if (process.env.NODE_ENV === 'production') {
  // ... this code won't be counted towards coverage
}
```

## Best Practices
- **Coverage != Quality**: 100% coverage does not mean your code is bug-free. It only means the code was *executed*. It doesn't mean your tests are *good* or that they cover all edge cases. Use Mutation Testing to verify test quality.
- **Don't Aim for 100%**: A project with 80-90% coverage is usually healthier than one with 100% that uses meaningless tests just to "hit the number".
- **Branch Coverage is Key**: Focus on making sure all `if/else` paths are tested, as these are where bugs most frequently hide.
- **Integrate with CI/CD**: Use tools like Codecov, Coveralls, or SonarQube to track coverage trends over time and visualize them in your PRs.
- **Ignore Boilerplate**: Don't waste time testing auto-generated code, type definitions, or third-party libraries. Focus your coverage on the "business logic" (the code *you* wrote).