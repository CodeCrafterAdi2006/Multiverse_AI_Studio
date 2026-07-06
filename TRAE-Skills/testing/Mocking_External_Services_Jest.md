# Skill: Mocking External Services (Jest)

## Purpose
To isolate the unit under test by replacing real external dependencies (e.g., APIs, databases, third-party libraries) with mock objects. This ensures that tests are fast, predictable, and don't require real network or database connections.

## When to Use
- When testing a function that calls a real API (e.g., `axios`, `fetch`)
- When testing code that uses a database ORM (e.g., `Prisma`, `TypeORM`)
- When dealing with third-party SDKs (e.g., Stripe, AWS SDK, SendGrid)
- To simulate error cases (e.g., "What happens if the API returns a 500 error?")

## Procedure

### 1. Mocking a Module (e.g., Axios)
The most common use case is mocking an HTTP client.

**`api.ts`**
```typescript
import axios from 'axios';
export const fetchUser = async (id: number) => {
  const response = await axios.get(`https://api.example.com/users/${id}`);
  return response.data;
};
```

**`api.test.ts`**
```typescript
import axios from 'axios';
import { fetchUser } from './api';

// 1. Tell Jest to mock the entire axios module
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

test('fetchUser returns data correctly', async () => {
  const mockUser = { id: 1, name: 'John Doe' };
  
  // 2. Define the behavior of the mock
  mockedAxios.get.mockResolvedValue({ data: mockUser });

  const user = await fetchUser(1);
  
  // 3. Assertions
  expect(user).toEqual(mockUser);
  expect(mockedAxios.get).toHaveBeenCalledWith('https://api.example.com/users/1');
});
```

### 2. Simulating Errors
Mocks are perfect for testing error handling.

```javascript
test('fetchUser handles API errors', async () => {
  mockedAxios.get.mockRejectedValue(new Error('Network Error'));

  // Assert that the function throws as expected
  await expect(fetchUser(1)).rejects.toThrow('Network Error');
});
```

### 3. Mocking a Single Function (`jest.spyOn`)
Use `spyOn` if you only want to mock a specific function but keep the rest of the module's behavior intact.

```javascript
import * as utils from './utils';

test('calls helper function', () => {
  const spy = jest.spyOn(utils, 'helperFunction').mockReturnValue(true);
  
  // Call the code that uses utils.helperFunction
  doSomething();

  expect(spy).toHaveBeenCalled();
  
  // Restore original implementation after the test
  spy.mockRestore();
});
```

### 4. Clearing Mocks Between Tests
Always clear your mocks to avoid "pollution" (where the call count from one test affects another).

```javascript
beforeEach(() => {
  jest.clearAllMocks();
});
```

## Best Practices
- **Mock at the Boundary**: Mock the external library (e.g., `axios`, `prisma`) rather than your own internal wrappers if possible. This tests your code more thoroughly.
- **Don't Over-Mock**: If a function is simple and has no external dependencies, don't mock it. Mocks should only be used to cross "boundaries" (network, disk, external libraries).
- **Use Manual Mocks (`__mocks__`)**: For complex libraries that are used in many tests (e.g., `react-native-fs`), create a manual mock in a `__mocks__` folder next to the `node_modules`.
- **Verify Call Arguments**: Don't just check `toHaveBeenCalled()`. Use `toHaveBeenCalledWith(arg1, arg2)` to ensure your code is sending the correct data to the external service.
- **Use `nock` for API Mocking**: For complex HTTP mocking (e.g., intercepting multiple different URLs with different headers), consider using the `nock` library alongside Jest. It provides a more powerful, interceptor-based approach.