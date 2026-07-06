# Skill: Component Testing (React Testing Library)

## Purpose
To test UI components as a user would experience them, focusing on the DOM structure and interactions (clicks, input typing, modal visibility) rather than the internal state or implementation details of the component.

## When to Use
- When building reusable UI components (e.g., buttons, forms, navbars)
- To ensure that specific text or elements appear after an action
- When refactoring React components from Class components to Hooks to ensure behavior remains identical
- When testing event handlers (e.g., form submissions, button clicks)

## Procedure

### 1. Installation
Install the necessary testing library for React.

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

### 2. Basic Component Test
Create a test file (e.g., `LoginForm.test.tsx`). Use `render` and `screen` to interact with the component.

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { LoginForm } from './LoginForm';

test('renders login form and submits', () => {
  // 1. Render the component
  render(<LoginForm onSubmit={jest.fn()} />);

  // 2. Query for elements by text or role (as a user would)
  const emailInput = screen.getByLabelText(/email/i);
  const passwordInput = screen.getByLabelText(/password/i);
  const submitButton = screen.getByRole('button', { name: /login/i });

  // 3. Fire events to simulate user behavior
  fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
  fireEvent.change(passwordInput, { target: { value: 'password123' } });
  fireEvent.click(submitButton);

  // 4. Assert that something happened (e.g., success message)
  // Use jest-dom matchers like .toBeInTheDocument()
  expect(screen.getByText(/success/i)).toBeInTheDocument();
});
```

### 3. Using `user-event` for Realistic Interactions
The `user-event` library is preferred over `fireEvent` because it simulates a real user's keyboard and mouse behavior more accurately.

```tsx
import userEvent from '@testing-library/user-event';

test('typing in input', async () => {
  const user = userEvent.setup();
  render(<LoginForm />);
  
  const emailInput = screen.getByLabelText(/email/i);
  await user.type(emailInput, 'jane@example.com');
  
  expect(emailInput).toHaveValue('jane@example.com');
});
```

### 4. Handling Asynchronous Elements
If an element appears after a delay (e.g., an API call), use `findBy` queries or `waitFor`.

```tsx
test('shows error after failed login', async () => {
  render(<LoginForm />);
  // ... fill in details and click submit ...

  // findBy queries wait for the element to appear (returns a Promise)
  const errorMessage = await screen.findByText(/invalid credentials/i);
  expect(errorMessage).toBeInTheDocument();
});
```

## Best Practices
- **Query by Accessibility Role**: Always prefer `getByRole`, `getByLabelText`, or `getByPlaceholderText` over `testId` or `className`. This ensures your components are accessible to screen readers.
- **Don't Test implementation details**: Don't test the component's internal state (e.g., `expect(component.state.count).toBe(1)`). Test what the user sees (e.g., `expect(screen.getByText('Count: 1')).toBeInTheDocument()`).
- **Use `jest-dom` Matchers**: Import `@testing-library/jest-dom` in your `setupTests.ts` to get helpful matchers like `.toBeVisible()`, `.toHaveValue()`, and `.toBeDisabled()`.
- **Mock External Hooks**: If your component uses `useTranslation` or `useNavigate`, mock them in your tests to keep them isolated.
  ```javascript
  jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => jest.fn(),
  }));
  ```