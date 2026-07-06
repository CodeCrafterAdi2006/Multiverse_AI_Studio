# Skill: Repository Archiving & Legacy Code Retirement

## Purpose
To clean up old repos, reduce clutter, and retire legacy code safely.

## When to Use
- When you have unused repos
- For legacy code no longer in use
- When you want to reduce security risks from old code
- For offboarding projects

## Procedure

### 1. Archive a Repository (GitHub/GitLab)
Archive a repo that's no longer active.

```bash
# 1. Update README: Add notice at top
# [ARCHIVED] This project is no longer maintained.
# 2. Close all open issues/PRs
# 3. Archive the repo (GitHub: Settings → Danger Zone → Archive this repository)
# 4. Keep it read-only (no pushes/merges)
```

### 2. Retire Legacy Code in Active Repo
Remove legacy code in a live repo.

```bash
# 1. Mark as deprecated
/**
 * @deprecated Use newUserService instead
 */
function oldUserService() {
  console.warn('oldUserService is deprecated!');
  // ...
}
# 2. Keep for a grace period (2-3 releases)
# 3. Remove in major version
git rm src/legacy/
git commit -m "chore!: remove legacy user service"
```

### 3. Archive Old Branches
Clean up old branches.

```bash
# List merged branches
git branch --merged main
# Delete local merged branches
git branch -d old-feature
# Delete remote merged branches
git push origin --delete old-feature
# Auto-delete branches after merging (GitHub repo settings)
```

### 4. Archive Old CI/CD Pipelines
Disable old pipelines.

```yaml
# Add a notice at top of workflow
# [ARCHIVED] This workflow is no longer used
name: Old Deploy
on:
  push:
    branches: [old-branch]  # Disable triggers
```

## Best Practices
- **Document**: Add archive/retirement clearly
- **Grace Period**: Give users time to migrate
- **Backup**: Make sure you have a backup before archiving
- **Notify**: Notify stakeholders before archiving
- **Clean Up**: Delete old branches/tags
- **Security**: Archive old repos to reduce attack surface
