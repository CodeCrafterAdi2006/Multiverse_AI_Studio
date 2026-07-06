# Skill: CHANGELOG Conventional Changelog Auto-Generation

## Purpose
To keep a clear, human-readable CHANGELOG that tells users what changed in each release.

## When to Use
- For libraries/apps with users (internal or external)
- When you want to automate release notes
- For teams that forget to update CHANGELOGs

## Procedure

### 1. Keep a CHANGELOG
Follow the Keep a CHANGELOG format.

```markdown
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2024-06-14
### Added
- Dark mode toggle
- User profile page

### Fixed
- Payment timeout issue
- Broken links in docs

### Changed
- Updated dependencies

## [1.1.0] - 2024-05-20
### Added
- Cart persistence
```

### 2. Auto-Generate with Conventional Changelog
Use Conventional Commits to auto-generate.

```bash
# Install dependencies
npm install -D standard-version
# Add script
```

```json
{
  "scripts": {
    "release": "standard-version"
  }
}
```

```bash
# First release
npm run release -- --first-release
# Patch release (fixes)
npm run release
# Minor release (features)
npm run release -- --release-as minor
# Major release (breaking)
npm run release -- --release-as major
```

### 3. GitHub Release Notes
Auto-generate GitHub releases with Release Drafter.

```yaml
# .github/release-drafter.yml
name-template: 'v$RESOLVED_VERSION'
tag-template: 'v$RESOLVED_VERSION'
categories:
  - title: '🚀 Features'
    labels:
      - 'feature'
  - title: '🐛 Bug Fixes'
    labels:
      - 'fix'
  - title: '📝 Documentation'
    labels:
      - 'docs'
version-resolver:
  major:
    labels:
      - 'breaking'
  minor:
    labels:
      - 'feature'
  patch:
    labels:
      - 'fix'
      - 'chore'
```

## Best Practices
- **Keep a CHANGELOG**: Follow the Keep a CHANGELOG format
- **Group Changes**: Group by Added/Changed/Fixed/Removed
- **Link Versions**: Link versions to compare URLs
- **Date Releases**: Always add release dates
- **Semantic Versioning**: Use SemVer with Conventional Commits
- **Auto-Generate**: Use tools to reduce manual work
- **Human-Readable**: Make it easy for users (not just devs!)
