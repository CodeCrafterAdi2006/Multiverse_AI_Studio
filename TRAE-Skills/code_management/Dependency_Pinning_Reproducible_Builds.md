# Skill: Dependency Pinning & Reproducible Builds

## Purpose
To ensure your project builds the same way for everyone, every time.

## When to Use
- When "it works on my machine" issues
- For CI/CD pipelines
- For open-source projects
- When you need consistent builds

## Procedure

### 1. Lock Files
Always commit lock files.

```bash
# npm: package-lock.json
# yarn: yarn.lock
# pnpm: pnpm-lock.yaml
# Python: Pipfile.lock, requirements.txt (with hashes)
# Go: go.sum
```

### 2. Exact Versions
Pin versions in package.json (npm example.

```json
{
  "dependencies": {
    "react": "18.2.0",  // Exact version (no ^/~)
    "lodash": "4.17.21",
    "next": "14.2.5"
  },
  "devDependencies": {
    "typescript": "5.5.3"
  },
  "engines": {
    "node": "20.15.0",  // Exact Node version
    "pnpm": "9.5.0"
  },
  "packageManager": "pnpm@9.5.0"  // Enforce package manager
}
```

### 3. .nvmrc / .tool-versions
Specify Node version.

```bash
# .nvmrc
20.15.0
```

```
# .tool-versions (for asdf)
nodejs 20.15.0
python 3.12.0
```

### 4. npm ci (Clean Install)
Use `npm ci` instead of `npm install` in CI.

```bash
# npm: npm ci installs *exact* versions from lock file
npm ci
# pnpm: pnpm install --frozen-lockfile
pnpm install --frozen-lockfile
# yarn: yarn install --frozen-lockfile
yarn install --frozen-lockfile
```

### 5. Docker for Reproducibility
Use Docker to freeze the entire environment.

```dockerfile
# Use exact base image
FROM node:20.15.0-alpine
WORKDIR /app
# Copy lock file first for caching
COPY package.json pnpm-lock.yaml ./
# Install dependencies
RUN pnpm install --frozen-lockfile
# Copy code
COPY . .
# Build
RUN pnpm build
# Run
CMD ["pnpm", "start"]
```

## Best Practices
- **Commit Lock Files**: Always commit lock files to repo
- **Exact Versions**: Use exact versions for production
- **Enforce Package Manager**: Use `packageManager` field
- **Use `npm ci`**: Use in CI instead of `npm install`
- **Dockerize**: Use Docker for consistent environments
- **Cache Dependencies**: Cache dependencies in CI to speed up builds
