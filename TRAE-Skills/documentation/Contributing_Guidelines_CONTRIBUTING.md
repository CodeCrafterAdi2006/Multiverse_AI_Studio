# Skill: Contributing Guidelines (CONTRIBUTING.md)

## Purpose
To establish clear, welcoming, and standardized procedures for external and internal contributors to collaborate on a project. A well-crafted `CONTRIBUTING.md` minimizes friction, sets expectations, and ensures code quality.

## When to Use
- When initializing a new open-source or inner-source repository
- When the project starts accepting pull requests from other teams or the public
- When there is confusion about the workflow, commit standards, or testing requirements

## Procedure

### 1. Code of Conduct Integration
Always begin by linking to or establishing a Code of Conduct to ensure a safe and inclusive environment.

### 2. Getting Started & Setup
Provide exact commands to get the project running locally.

```bash
# Example setup instructions
git clone https://github.com/organization/project.git
cd project
npm install  # or pip install -r requirements.txt
cp .env.example .env
npm run dev
```

### 3. Branching Strategy
Define the naming conventions for branches.
- `feature/short-description`
- `fix/issue-number-description`
- `docs/what-changed`

### 4. Commit Message Convention
Enforce a standard, such as Conventional Commits.
```
type(scope): subject

body

footer (e.g., Closes #123)
```
Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`.

### 5. Pull Request Process
Outline the steps to submit a PR:
1. Ensure all tests pass (`npm run test`).
2. Run linters and formatters (`npm run lint`).
3. Update relevant documentation.
4. Fill out the Pull Request template completely.
5. Request review from code owners.

### 6. Issue Reporting
Provide templates or guidelines for:
- **Bug Reports**: Expected behavior, actual behavior, steps to reproduce, environment details.
- **Feature Requests**: Problem description, proposed solution, alternatives considered.

## Best Practices
- Keep it concise but comprehensive.
- Use automated checks (e.g., GitHub Actions, Husky) to enforce these guidelines automatically.
- Provide links to architectural documentation if the project is complex.