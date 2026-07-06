# Skill: Test-Driven Development (TDD)

## Purpose
To write higher-quality, more reliable, and better-designed code by writing tests *before* the implementation. This forces developers to think about the requirements, edge cases, and API design upfront.

## When to Use
- When implementing a new feature or function with clear requirements
- When fixing a bug (write a failing test that reproduces the bug first)
- When refactoring complex legacy code to ensure behavior is preserved
- To reduce "over-engineering" by writing only the code necessary to pass the tests

## Procedure

### 1. The Red-Green-Refactor Cycle
TDD is a simple 3-step loop:

1. **🔴 RED**: Write a small test for a specific behavior. Run it and watch it fail (usually because the function doesn't exist yet).
2. **🟢 GREEN**: Write the *minimum* amount of code necessary to make that test pass. Don't worry about perfection yet.
3. **🔵 REFACTOR**: Improve the code (rename variables, extract functions, optimize performance) while keeping the tests green.

### 2. TDD Example (JavaScript/Jest)

**Step 1: Write a failing test (RED)**
```javascript
// calculator.test.js
const { add } = require('./calculator');

test('adds two numbers correctly', () => {
  expect(add(2, 3)).toBe(5);
});
```
*Result: `TypeError: add is not a function`*

**Step 2: Make it pass (GREEN)**
```javascript
// calculator.js
function add(a, b) {
  return a + b;
}
module.exports = { add };
```
*Result: `PASS`*

**Step 3: Refactor (REFACTOR)**
Add edge cases or improve the function if needed.
```javascript
// calculator.test.js
test('handles strings by converting to numbers', () => {
  expect(add('2', 3)).toBe(5);
});

// calculator.js
function add(a, b) {
  return Number(a) + Number(b);
}
```

### 3. TDD Best Practices
- **Small Steps**: Don't try to test a whole feature at once. Break it into tiny behaviors (e.g., "handle empty input", "handle positive numbers").
- **Only write enough code to pass**: Avoid "gold-plating" or adding features you *think* you'll need later. Let the tests drive the development.
- **Commit frequently**: Every time you reach "Green", you have a working state. Commit it.
- **Trust the tests**: If you refactor and the tests stay green, you can be confident you haven't introduced regressions.

## Best Practices
- **Don't TDD UI/Layout**: TDD is perfect for business logic, algorithms, and data processing. It's often too slow and frustrating for visual design or CSS.
- **Keep Tests Fast**: TDD works best when tests run in milliseconds. If your tests are slow, you'll stop running them frequently.
- **Test Behaviors, Not Implementation**: Don't test *how* the code works (e.g., "calls function X"), test *what* it does (e.g., "returns Y when input is Z"). This allows you to refactor the internal implementation without breaking the tests.