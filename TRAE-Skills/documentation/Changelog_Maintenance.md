# Skill: Release Notes & Changelog Maintenance

## Purpose
To communicate product updates, bug fixes, and security patches to users and internal stakeholders in a clear, consistent, and useful format. A good changelog builds trust and helps users understand how the product is evolving.

## When to Use
- After every production deployment or version release
- When publishing open-source libraries (e.g., via npm, PyPI)
- To maintain a historical record of system changes for audit or debugging purposes

## Procedure

### 1. The Standard: Keep a Changelog
Follow the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

**`CHANGELOG.md` Structure**:
- `Added`: For new features.
- `Changed`: For changes in existing functionality.
- `Deprecated`: For soon-to-be-removed features.
- `Removed`: For now-removed features.
- `Fixed`: For any bug fixes.
- `Security`: In case of vulnerabilities.

### 2. Format Example

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2023-10-27
### Added
- Multi-language support (English, Italian, Spanish).
- Dark mode toggle in user settings.

### Fixed
- Issue where the login button was unresponsive on iOS Safari.
- Memory leak in the analytics background worker.

### Security
- Updated `axios` to 1.6.0 to address a critical vulnerability.

## [1.1.0] - 2023-09-15
### Changed
- Refactored the authentication flow to use JWT instead of sessions.
```

### 3. Writing for the Audience
- **Internal/Developer Audience**: Be technical. Include PR numbers, internal IDs, and technical details (e.g., "Optimized SQL query on the `users` table").
- **External/User Audience**: Be benefit-oriented. Avoid jargon. (e.g., "The app now loads 30% faster on slow connections").

### 4. Automation with `semantic-release`
Instead of manual updates, automate the changelog generation based on **Conventional Commits**.

```bash
# Commit message format:
# feat: add dark mode
# fix: resolve login button issue
```

Tools like `semantic-release` or `standard-version` will:
1. Detect the version bump (Major/Minor/Patch).
2. Generate the `CHANGELOG.md` entries automatically.
3. Tag the release in Git.

## Best Practices
- **Don't just dump Git logs**: A commit history is not a changelog. Commits like "fix typo" or "WIP" should not appear in release notes.
- **Group by Version**: Always list the most recent version at the top.
- **Include Dates**: Every version must have a release date (YYYY-MM-DD).
- **Link to Versions**: If using GitHub, link the version number to the specific tag or diff (e.g., `[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0`).
- **Highlight Breaking Changes**: Make them extremely obvious using bold text or a dedicated section.