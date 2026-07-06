# Skill: Secret Scanning & Management

## Purpose
To prevent developers from accidentally committing sensitive information (e.g., API keys, database credentials, SSH keys) to a version control system (Git). Secret scanning tools automatically monitor your codebase and block commits or send alerts if secrets are detected.

## When to Use
- When working in a team on a shared repository
- When using third-party services (AWS, Stripe, OpenAI, SendGrid)
- As part of the CI/CD pipeline to ensure no new secrets are introduced
- To comply with security audits and SOC2/ISO 27001 requirements

## Procedure

### 1. The Strategy: Prevent vs. Detect
- **Prevention**: Use pre-commit hooks to block secrets *before* they are committed.
- **Detection**: Use automated scanners to find secrets *after* they are pushed to the server (e.g., GitHub Secret Scanning).

### 2. Implementation: Local Prevention (gitleaks)
[Gitleaks](https://github.com/gitleaks/gitleaks) is a popular, open-source secret scanner.

**Installation**:
```bash
# macOS
brew install gitleaks
# Windows
winget install gitleaks
```

**Run a manual scan**:
```bash
gitleaks detect --source . --verbose
```

**Integration with Husky (Pre-commit hook)**:
1. Install Husky: `npm install husky --save-dev`
2. Add a pre-commit hook:
```bash
npx husky add .husky/pre-commit "gitleaks protect --staged --verbose"
```

### 3. Implementation: GitHub Secret Scanning
GitHub automatically scans public and private repositories for known secrets (AWS keys, Stripe tokens, etc.).

**How to enable**:
1. Go to your repository **Settings**.
2. Select **Code security and analysis**.
3. Enable **Secret scanning**.
4. (Optional but recommended) Enable **Push protection**. This will block any `git push` that contains a detected secret.

### 4. Correct Way to Manage Secrets (.env)
Never hardcode secrets. Always use environment variables.

**`.env`** (DO NOT commit this file!)
```env
STRIPE_API_KEY=sk_test_...
DATABASE_URL=postgres://user:pass@localhost:5432/db
```

**`.gitignore`**
```text
.env
.env.local
.env.*.local
```

**`.env.example`** (Commit this file)
```env
STRIPE_API_KEY=
DATABASE_URL=
```

## Best Practices
- **Rotate Secrets Regularly**: Even if you don't think a secret is leaked, change it every 90 days.
- **Use a Secret Manager**: For production, don't store secrets in plain text `.env` files on the server. Use a dedicated secret manager like **AWS Secrets Manager**, **HashiCorp Vault**, or **GitHub Actions Secrets**.
- **Minimum Permission Keys**: If you need an API key for a script, don't use the "Admin" key. Create a restricted key that only has the permissions needed for that specific task.
- **I Leaked a Secret! What do I do?**:
    1. **Revoke immediately**: Deleting the commit from Git is NOT enough. The secret is already compromised. Revoke it on the provider's dashboard.
    2. **Generate a new one**: Replace the old secret with a new one.
    3. **Invalidate the Git history**: If the leak was on a public repo, use tools like `bfg-repo-cleaner` or `git filter-repo` to completely remove the secret from all branches and tags.
- **Scan Third-party Dependencies**: Use tools like `npm audit` or `Snyk` to ensure your dependencies don't have vulnerabilities or hardcoded secrets.
- **Education**: Ensure every developer on the team understands the risks of hardcoding secrets and knows how to use the project's secret management tools.