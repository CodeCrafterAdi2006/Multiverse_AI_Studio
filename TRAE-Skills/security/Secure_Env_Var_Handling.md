# Skill: Secure Env Var Handling

## Purpose
To safely manage, store, and access environment variables (secrets, configurations, API keys) throughout the application lifecycle. Proper handling prevents accidental leaks, simplifies local development, and ensures production security.

## When to Use
- When initializing a new project or adding a new secret
- When deploying to different environments (Local, Staging, Production)
- To avoid hardcoding values like database URLs, API keys, or feature flags
- When establishing a secure CI/CD pipeline

## Procedure

### 1. The Golden Rule: Never Commit Secrets
Secrets (API keys, passwords, private keys) must never be committed to version control. Add your environment files to `.gitignore`.

**`.gitignore`**
```text
.env
.env.local
.env.*.local
*.pem
*.key
```

### 2. Implementation: Local Development (Node.js/dotenv)
Use the `dotenv` or `dotenv-safe` library to load variables from a file into `process.env`.

**Installation**:
```bash
npm install dotenv
```

**Usage**:
```javascript
require('dotenv').config();

const stripeKey = process.env.STRIPE_API_KEY;
if (!stripeKey) {
  throw new Error('STRIPE_API_KEY is not defined in environment variables');
}
```

### 3. The "Self-Documenting" .env.example
Always provide an example file with dummy values to show other developers which variables they need to set.

**`.env.example`**
```env
# Stripe API Configuration
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=

# Database Connection
DATABASE_URL=postgres://user:password@localhost:5432/myapp
```

### 4. Implementation: Production (Managed Secrets)
In production, don't use `.env` files. Use the built-in secret management of your platform.

- **Heroku**: `heroku config:set STRIPE_API_KEY=...`
- **Vercel/Netlify**: Add via the web dashboard (Settings -> Environment Variables).
- **GitHub Actions**: Add via Settings -> Secrets and variables -> Actions. Use in your YAML:
  ```yaml
  env:
    STRIPE_API_KEY: ${{ secrets.STRIPE_API_KEY }}
  ```
- **AWS**: Use **AWS Secrets Manager** or **AWS Parameter Store**.

### 5. Accessing Env Vars Safely (TypeScript)
Use a validation library like **Zod** or **Envalid** to ensure all required variables are present and have the correct format before the app starts.

```typescript
import { z } from 'zod';

const envSchema = z.object({
  PORT: z.string().default('3000'),
  NODE_ENV: z.enum(['development', 'production', 'test']),
  DATABASE_URL: z.string().url(),
  STRIPE_API_KEY: z.string().min(1)
});

// This will throw a clear error if any variable is missing or invalid
export const env = envSchema.parse(process.env);
```

## Best Practices
- **Use Clear Names**: Prefix variables with their service name (e.g., `AWS_S3_BUCKET`, `STRIPE_WEBHOOK_SECRET`) to avoid collisions.
- **Differentiate Environments**: Use different secrets for `development` and `production`. Never use a production database key in your local `.env`.
- **Restrict Access**: Only give production secret access to the individuals or CI/CD pipelines that absolutely need it.
- **Avoid Logging Secrets**: Never log `process.env` or print secrets to the console for debugging. Use a "secret-safe" logger if necessary.
- **Rotate Regularly**: Change your production secrets every few months to minimize the impact of a potential leak.
- **Prefer Cloud Secret Managers**: For enterprise apps, use dedicated services (like HashiCorp Vault) that provide audit logs and automatic rotation.