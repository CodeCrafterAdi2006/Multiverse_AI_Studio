# Skill: Code Commenting Best Practices

## Purpose
To write meaningful, concise, and helpful comments that explain the "why" behind complex code, without cluttering the codebase with obvious or redundant information. Good comments act as documentation for future developers (including your future self).

## When to Use
- When implementing a non-obvious algorithm or workaround
- To document complex business rules that aren't clear from the code alone
- When dealing with technical debt or temporary hacks (e.g., `TODO`, `FIXME`)
- To explain why a specific library or external API is used in a certain way

## Procedure

### 1. Types of Comments
- **Documentation Comments (Docstrings)**: Explain *what* a function or class does, its parameters, and return values.
- **Implementation Comments**: Explain *how* or *why* a specific block of code works.
- **TODO/FIXME Comments**: Track pending work or known issues.

### 2. The "Why", Not the "What"
Code explains the "What" and "How". Comments should explain the "Why".

**❌ BAD (Redundant)**:
```javascript
// Increment i by 1
i++;
```

**✅ GOOD (Explains intent)**:
```javascript
// We skip the first element because it's a header in the CSV
for (let i = 1; i < data.length; i++) {
  // ...
}
```

### 3. Using JSDoc (for JavaScript/TypeScript)
Standardize function documentation so editors can provide better IntelliSense.

```typescript
/**
 * Calculates the final price after tax and discounts.
 * 
 * @param price - The base price of the item.
 * @param taxRate - The tax rate as a decimal (e.g., 0.22 for 22%).
 * @param discount - A fixed discount amount.
 * @returns The final price rounded to 2 decimal places.
 * 
 * @example
 * calculatePrice(100, 0.22, 10) // returns 112
 */
function calculatePrice(price: number, taxRate: number, discount: number): number {
  // ...
}
```

### 4. Handling Workarounds
Always document when you are doing something unusual to fix a bug or handle an edge case.

```javascript
// NOTE: We use a 50ms timeout here because the third-party modal 
// needs time to mount before we can focus the input field.
// See issue #124 for more details.
setTimeout(() => {
  inputRef.current.focus();
}, 50);
```

### 5. Managing TODOs
Don't just leave `// TODO: fix this`. Be specific and include your name or a ticket number.

```javascript
// TODO(JohnDoe): Refactor this to use the new GraphQL API once it's deployed. 
// See ticket JIRA-456.
```

## Best Practices
- **Good code is self-documenting**: Before writing a comment, ask: "Can I make this code clearer by renaming a variable or extracting a function?"
- **Keep comments up to date**: An incorrect comment is worse than no comment at all. Update comments during refactoring.
- **Avoid "Commented-out code"**: Don't leave old code in comments. That's what Git is for. Delete it.
- **Don't use comments to apologize**: If code is bad, refactor it instead of writing a comment explaining how bad it is.
- **Be professional**: Avoid jokes, frustration, or personal notes in comments. They are part of the permanent codebase.