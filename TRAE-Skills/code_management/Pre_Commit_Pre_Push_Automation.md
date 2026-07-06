# Skill: Pre-Commit & Pre-Push Hooks Automation

## Purpose
To catch issues *before* commits/pushes to CI, saving time.

## When to Use
- When you forget to lint/format before committing
- For teams that want consistent code quality
- When you want to reduce CI failures

## Procedure

### 1. Pre-Commit with Husky + lint-staged
Run linters/formatters on staged files.

```bash
# Install dependencies
npm install -D husky lint-staged
# Initialize Husky
npx husky install
# Add pre-commit hook
npx husky add .husky/pre-commit "npx lint-staged"
# Make executable (Windows)
npx husky install
```

```json
// package.json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,css,md}": [
      "prettier --write"
    ]
  }
}
```

### 2. Pre-Push Hook
Run tests before pushing.

```bash
# Add pre-push hook
npx husky add .husky/pre-push "npm test"
```

### 3. Pre-Commit Framework (Python, etc.)
For non-JS projects.

```yaml
# .pre-commit-config.yaml
repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.6.0
  hooks:
  - id: trailing-whitespace
  - id: end-of-file-fixer
  - id: check-yaml
- repo: https://github.com/psf/black
  rev: 24.4.2
  hooks:
  - id: black
```

```bash
# Install pre-commit
pip install pre-commit
pre-commit install
```

### 4. Commit Message Hook
Enforce Conventional Commits.

```bash
# .husky/commit-msg
npx --no -- commitlint --edit "$1"
```

```javascript
// commitlint.config.js
export default {
  extends: ['@commitlint/config-conventional'],
};
```

## Best Practices
- **Lint Staged**: Only lint staged files to save time
- **Fast Hooks**: Keep hooks < 10 seconds
- **Test in CI**: Also run checks in CI as a safety net
- **Allow Bypass**: Allow `--no-verify` for emergencies (document!)
- **Install Script**: Add a `prepare` script to auto-install husky
```json
{
  "scripts": {
    "prepare": "husky install"
  }
}
```
