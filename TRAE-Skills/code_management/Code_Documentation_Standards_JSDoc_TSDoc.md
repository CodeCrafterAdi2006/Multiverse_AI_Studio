# Skill: Code Documentation Standards (JSDoc/TSDoc)

## Purpose
To write clear, consistent, and useful documentation for your code that helps teammates (and future you!).

## When to Use
- When working on team projects
- For public/open-source libraries
- When you want to reduce onboarding time
- For code that will be maintained long-term

## Procedure

### 1. JSDoc/TSDoc Basics
Document functions, classes, and types.

```typescript
/**
 * Calculates the total price of items in a cart, applying discounts and taxes.
 * @param items - Array of cart items with id, price, and quantity
 * @param discount - Discount percentage (0-100)
 * @param taxRate - Tax rate (e.g., 0.08 for 8%)
 * @returns Total price after discount and tax
 * @throws {Error} If discount is >100 or <0
 * @example
 * ```typescript
 * const cart = [{ id: "1", price: 10, quantity: 2 }];
 * const total = calculateTotal(cart, 10, 0.08);
 * console.log(total); // 19.44
 * ```
 */
function calculateTotal(
  items: { id: string; price: number; quantity: number }[],
  discount: number,
  taxRate: number
): number {
  if (discount < 0 || discount > 100) throw new Error("Invalid discount");
  const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const afterDiscount = subtotal * (1 - discount / 100);
  return afterDiscount * (1 + taxRate);
}

/**
 * A user in our system.
 * @typedef {Object} User
 * @property {string} id - Unique user ID
 * @property {string} name - Full name
 * @property {string} email - Email address
 * @property {Date} createdAt - Account creation date
 */

/**
 * User service class for managing users.
 */
class UserService {
  /**
   * Creates a new user.
   * @param userData - User data without ID/createdAt
   * @returns Created user
   */
  async createUser(userData: Omit<User, "id" | "createdAt">): Promise<User> {
    // ...
  }
}
```

### 2. React Component Documentation
Document React components.

```tsx
/**
 * A reusable button component with different variants.
 * @component
 * @example
 * ```tsx
 * <Button
 *   variant="primary"
 *   onClick={() => console.log("Clicked!")}
 * >
 *   Click Me
 * </Button>
 * ```
 * @param {Object} props - Component props
 * @param {("primary" | "secondary" | "danger"} props.variant - Button style variant
 * @param {boolean} [props.disabled=false] - Whether button is disabled
 * @param {React.ReactNode} props.children - Button content
 * @param {() => void} [props.onClick] - Click handler
 */
function Button({
  variant,
  disabled = false,
  children,
  onClick,
}: {
  variant: "primary" | "secondary" | "danger";
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}) {
  return (
    <button
      className={`btn btn-${variant}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

### 3. README for Repositories
Standardize your repo README.

```markdown
# Project Name
Short, descriptive subtitle.

## Features
- ✨ Feature 1
- 🚀 Feature 2

## Installation
```bash
npm install
```

## Usage
```typescript
import { thing } from "package";
const result = thing();
```

## Contributing
See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License
MIT
```

## Best Practices
- **Why, Not What**: Explain *why* code exists, not just what it does
- **Update Docs**: Keep docs in sync with code changes
- **Examples**: Always add usage examples
- **TS over JSDoc**: Prefer TypeScript types + TSDoc for TS projects
- **Avoid Redundancy**: Don't document obvious things
- **Docstrings**: Use docstrings for public APIs
- **README**: Always have a good README
