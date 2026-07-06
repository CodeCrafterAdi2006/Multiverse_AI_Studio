# Skill: Advanced Dependency Management (Dependabot & Renovate)

## Purpose
To automate dependency updates, reduce security risks, and keep dependencies fresh without manual toil.

## When to Use
- When you have outdated dependencies with security vulnerabilities
- For large projects with many npm/pip/go dependencies
- When you want to reduce manual dependency debt
- For teams that want consistent dependency updates (not just security patches)

## Procedure

### 1. GitHub Dependabot Setup
Automate security and version updates.

```yaml
# .github/dependabot.yml
version: 2
updates:
  # npm dependencies
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 5
    # Group related updates
    groups:
      eslint:
        patterns:
          - "eslint*"
          - "@typescript-eslint/*"
    # Ignore certain packages
    ignore:
      - dependency-name: "react"
        versions: ["19.x"  # Skip major version 19 for now
    reviewers:
      - "your-team-name"
    labels:
      - "dependencies"
  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
```

### 2. Renovate Setup (More Powerful)
More configurable than Dependabot.

```json
// renovate.json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:base"
  ],
  "schedule": ["before 3am on Monday"],
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "groupName": "minor and patch dependencies",
      "automerge": true,
      "automergeType": "branch"
    },
    {
      "matchDatasources": ["npm"],
      "matchPackagePatterns": ["^@types/"],
      "groupName": "type definitions"
    }
  ],
  "prHourlyLimit": 2,
  "prConcurrentLimit": 5,
  "vulnerabilityAlerts": {
    "enabled": true,
    "labels": ["security"]
  },
  "lockFileMaintenance": {
    "enabled": true,
    "schedule": ["before 4am on the first day of the month"]
  }
}
```

### 3. Manual Dependency Auditing
Check for vulnerabilities manually (npm example.

```bash
# npm audit
npm audit
npm audit fix  # Auto-fix compatible issues
npm audit fix --force  # Force fix (careful!)
# yarn audit
yarn audit
# pnpm audit
pnpm audit
# Check outdated
npm outdated
yarn outdated
pnpm outdated
# Update interactively
npm update --interactive
```

### 4. Pin Dependencies Correctly
Use lock files and pinning strategies.

```json
// package.json examples
{
  "dependencies": {
    "react": "^18.2.0",  // Caret: minor/patch updates
    "lodash": "~4.17.21",  // Tilde: patch only
    "axios": "1.7.2",  // Exact: no auto-updates (safe!)
    "next": "14.2.5"
  },
  "devDependencies": {
    "typescript": "5.5.3"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  },
  "packageManager": "pnpm@9.5.0"  // Specify package manager (Node 16+)
}
```

## Best Practices
- **Lock Files**: Always commit `package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml`
- **Exact Versions**: Prefer exact versions for production
- **Group Updates**: Group related dependencies to reduce PR noise
- **Automerge**: Automerge minor/patch if tests pass
- **Review**: Always review major version updates carefully
- **Schedule**: Run updates weekly/monthly to avoid debt
- **Security Patches**: Prioritize security patches immediately
