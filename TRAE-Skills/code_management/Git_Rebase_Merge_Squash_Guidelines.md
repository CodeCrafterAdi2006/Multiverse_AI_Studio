# Skill: Git Rebase, Merge & Squash Guidelines

## Purpose
To choose the right Git operation for clean history and clear merges.

## When to Use
- When cleaning up commit history
- For merging feature branches
- When you want a clean main branch
- For teams confused about rebase/merge

## Procedure

### 1. When to Use `git merge --no-ff
Preserve branch history (good for GitFlow).

```bash
# Merge feature branch to main, preserving history
git checkout main
git pull
git merge --no-ff feature/my-feature
# Result: Merge commit + all feature commits
```

### 2. When to Use `git rebase`
Clean up history before merging (good for Trunk-Based).

```bash
# Rebase feature branch on top of main
git checkout feature/my-feature
git fetch origin
git rebase origin/main
# Fix conflicts if any
git add .
git rebase --continue
# Push (force-with-lease for safety
git push --force-with-lease
```

### 3. When to Use Squash Merge
Squash all feature commits into one (clean main history).

```bash
# GitHub/GitLab: "Squash and merge" option in PR
# Result: One clean commit on main
# Example commit message: feat: add dark mode (closes #123)
```

### 4. Interactive Rebase
Clean up your commit history.

```bash
git rebase -i HEAD~5  # Edit last 5 commits
# In editor:
# pick = keep commit
# squash = combine with previous
# reword = edit commit message
# fixup = combine without message
# Example:
pick abc123 First commit
squash def456 Fix typo
squash ghi789 Add tests
# Result: One commit combining all changes
```

## Best Practices
- **Never Rebase Public**: Never rebase shared branches (main/develop)
- **Force-With-Lease**: Use `--force-with-lease` instead of `--force`
- **Squash Feature Commits**: Squash small, related commits for clean history
- **Merge Main Branches**: Use `--no-ff` for GitFlow releases
- **Rebase Feature**: Rebase feature branches on main often to avoid conflicts
- **Commit Messages**: Write good commit messages after squashing
