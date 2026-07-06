# Skill: Git Workflow Strategies (GitFlow, Trunk-Based, GitHub Flow)

## Purpose
To choose and implement the right Git workflow for your team, ensuring smooth collaboration, releases.

## When to Use
- When onboarding a new team to Git
- For teams working on different release cadences
- When switching from ad-hoc commits to structured workflows
- For teams using CI/CD pipelines
- When you need clarity on branching, merging, and releasing

## Procedure

### 1. GitHub Flow (Simplest Workflow
Perfect for continuous deployment.

```bash
# 1. Create a feature branch from main
git checkout -b feature/new-checkout
# 2. Commit changes
git add .
git commit -m "feat: add new checkout flow"
# 3. Push branch
git push -u origin feature/new-checkout
# 4. Open Pull Request (PR)
# 5. Review, discuss, update PR
# 6. Merge PR to main
# 7. Deploy immediately
git checkout main
git pull
git branch -d feature/new-checkout  # Cleanup
```

### 2. GitFlow (For Scheduled Releases)
Ideal for teams with regular release cycles (e.g., monthly).

```bash
# 1. Main branches: main (production) and develop
git checkout -b develop  # Start from develop for new features
# 2. Feature branch from develop
git checkout -b feature/user-profile develop
git commit -m "feat: add user profile page"
git push origin feature/user-profile
# 3. Merge feature to develop via PR
# 4. When ready for release: create release branch from develop
git checkout -b release/v1.2.0 develop
# 5. Fix bugs on release branch
git commit -m "fix: adjust pricing calculation"
# 6. Merge release to main AND develop
git checkout main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "Release v1.2.0"
git checkout develop
git merge --no-ff release/v1.2.0
# 7. Delete release branch
git branch -d release/v1.2.0
# 8. Hotfix from main
git checkout -b hotfix/critical-bug main
git commit -m "fix: resolve payment timeout"
git checkout main
git merge --no-ff hotfix/critical-bug
git tag -a v1.2.1 -m "Hotfix v1.2.1"
git checkout develop
git merge --no-ff hotfix/critical-bug
git branch -d hotfix/critical-bug
```

### 3. Trunk-Based Development (High-Velocity Teams)
For teams that deploy multiple times per day.

```bash
# 1. Work directly on short-lived feature branches (max 1-2 days)
git checkout -b feat/fast-feature main
# 2. Small, focused commits
git commit -m "feat: add button hover"
# 3. Push and merge to main quickly (via PR with tests!)
# 4. Use feature flags for incomplete features
# Example: Feature flag in code
if (featureFlags.newDashboard) {
  renderNewDashboard();
}
# 5. Clean up feature flags once released
```

## Best Practices
- **GitHub Flow**: Use for startups/teams with continuous deployment
- **GitFlow**: Use for scheduled releases (e.g., enterprise software)
- **Trunk-Based**: Use for high-velocity teams with strong CI/CD
- **Short-Lived Branches**: Keep branches < 1-2 days max
- **Small Commits**: Atomic, focused commits for easier review/rollback
- **CI on PR**: Always run tests before merging
- **Cleanup**: Delete branches after merging
- **Tags**: Use semantic tags for releases
