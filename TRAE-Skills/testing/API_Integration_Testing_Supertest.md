# Skill: API Integration Testing (Supertest + Jest)

## Purpose
To test the entire lifecycle of an HTTP request through your backend application (routing, middleware, controllers, and database interactions) to ensure that the different components work together correctly.

## When to Use
- When verifying that API endpoints return the correct status codes and JSON responses
- When testing authentication flows (e.g., logging in, getting a token, accessing a protected route)
- When validating database changes (e.g., creating a user via `POST /users` and verifying they exist in the DB)

## Procedure

### 1. Installation
Install `supertest` and a testing framework like `jest` as development dependencies.

```bash
npm install --save-dev jest supertest @types/jest @types/supertest
```

### 2. Prepare the Express App
Ensure your Express app is exported without calling `app.listen()`. This allows Supertest to bind it to an ephemeral port for testing without port conflicts.

**`app.ts`**
```typescript
import express from 'express';
import { userRoutes } from './routes/users';

const app = express();
app.use(express.json());
app.use('/users', userRoutes);

export default app; // Export the app, don't start the server here
```

**`server.ts`**
```typescript
import app from './app';

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
```

### 3. Writing the Test
Create a test file (e.g., `users.test.ts`). Use `supertest(app)` to make HTTP requests against your application.

```typescript
import request from 'supertest';
import app from '../src/app'; // Import the Express app
import db from '../src/db'; // Your database connection/ORM instance

// 1. Setup and Teardown
beforeAll(async () => {
  // Connect to a test database or run migrations
  await db.connect();
});

afterAll(async () => {
  // Clean up database and close connections
  await db.clear();
  await db.disconnect();
});

describe('User API Endpoints', () => {
  
  // 2. Test a GET request
  it('should return a list of users', async () => {
    const response = await request(app)
      .get('/users')
      .set('Authorization', 'Bearer valid_token_here'); // Set headers if needed

    // Assertions
    expect(response.status).toBe(200);
    expect(Array.isArray(response.body)).toBeTruthy();
  });

  // 3. Test a POST request
  it('should create a new user', async () => {
    const newUser = {
      name: 'Jane Doe',
      email: 'jane@example.com',
      password: 'securepassword'
    };

    const response = await request(app)
      .post('/users')
      .send(newUser); // Send JSON payload

    // Assertions
    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');
    expect(response.body.email).toBe(newUser.email);
    
    // Verify it actually reached the database
    const userInDb = await db.User.findByEmail('jane@example.com');
    expect(userInDb).not.toBeNull();
  });

  // 4. Test error handling
  it('should return 400 if email is missing', async () => {
    const response = await request(app)
      .post('/users')
      .send({ name: 'Invalid User' });

    expect(response.status).toBe(400);
    expect(response.body).toHaveProperty('error', 'Email is required');
  });
});
```

## Best Practices
- **Use a Separate Test Database**: Never run integration tests against a development or production database. Create a separate DB (e.g., `myapp_test`) and reset it before each test suite runs.
- **Isolate Tests**: Tests should not depend on each other. If test B relies on test A creating a user, they will fail if run out of order. Each test should create its own setup data.
- **Mock External Services**: If your API calls Stripe, SendGrid, or AWS S3, use Jest's mocking capabilities (`jest.mock()`) or libraries like `nock` to intercept these requests during integration testing. You don't want to send real emails or charge real credit cards during tests.