# Skill: Semantic Versioning Strategy

## Purpose
To use Semantic Versioning (SemVer) as a clear and predictable way to communicate the nature and impact of code changes to consumers, stakeholders, and other developers.

## When to Use
- When maintaining libraries, packages, APIs, or microservices
- When setting up CI/CD release pipelines
- When defining backward compatibility guarantees

## Procedure

### 1. Understanding the Format
Version numbers must follow the `MAJOR.MINOR.PATCH` format.

- **MAJOR version**: When you make incompatible API changes or breaking changes.
  - E.g., Changing the signature of a widely used public function.
  - Resets `MINOR` and `PATCH` to 0. (e.g., `1.4.2` -> `2.0.0`)
- **MINOR version**: When you add functionality in a backward-compatible manner.
  - E.g., Adding a new optional parameter, or a completely new feature that doesn't affect existing workflows.
  - Resets `PATCH` to 0. (e.g., `1.4.2` -> `1.5.0`)
- **PATCH version**: When you make backward-compatible bug fixes.
  - E.g., Fixing a typo, patching a security vulnerability without altering the API.
  - (e.g., `1.4.2` -> `1.4.3`)

### 2. Pre-release Tags and Build Metadata
Use pre-release tags for betas and release candidates:
- `1.0.0-alpha.1`
- `1.0.0-beta.2`
- `1.0.0-rc.1`

Build metadata can be appended with a plus sign (ignored by SemVer precedence):
- `1.0.0+20130313144700`

### 3. Version Zero (0.y.z)
Use major version zero for initial development. Anything MAY change at any time. The public API should not be considered stable.
- Start at `0.1.0`.
- Release `1.0.0` when the API is stable enough for production use.

### 4. Automation Tools
Instead of manually guessing versions, automate the process based on Conventional Commits.

**Using `semantic-release` (Node.js)**
```bash
npm install -D semantic-release
```

Create a `.releaserc` file:
```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/npm",
    "@semantic-release/github",
    "@semantic-release/git"
  ]
}
```

This will automatically:
1. Analyze commits (`fix:` -> PATCH, `feat:` -> MINOR, `BREAKING CHANGE:` -> MAJOR).
2. Generate a Changelog.
3. Bump the version in `package.json`.
4. Create a Git tag and GitHub Release.

## Best Practices
- Never reuse a version number once published. If a release is botched, publish a new patch version.
- Treat documentation updates and refactors that do not affect the public API as chores or patches depending on your pipeline.