# Skill: Repository Structure & Project Organization

## Purpose
To structure repos consistently so anyone can find what they need quickly.

## When to Use
- When starting a new project
- For reorganizing messy repos
- When onboarding new developers
- For multi-team repos

## Procedure

### 1. Standard Monolith/Polyrepo Decision
Choose between monorepo and polyrepo.

```
# Polyrepo (separate repos for separate services/apps
├── user-service/    # Backend service
│   ├── src/
│   ├── tests/
│   └── package.json
├── checkout-service/
└── web-app/           # Frontend app

# Monorepo (all in one repo)
├── apps/
│   ├── web/
│   └── admin/
├── packages/
│   ├── ui-components/
│   └── utils/
└── package.json
```

### 2. Frontend Project Structure
Standard Next.js/React structure.

```
src/
├── app/                  # Next.js App Router pages
├── components/
│   ├── ui/               # Reusable UI components
│   └── features/         # Feature-specific components
├── lib/                  # Utilities, helpers
│   ├── utils/
│   └── api/            # API clients
├── hooks/                # Custom React hooks
├── types/                # TypeScript types
├── styles/               # Global styles
└── tests/                # Tests
```

### 3. Backend Project Structure
Express/NestJS structure.

```
src/
├── modules/              # Feature modules
│   ├── users/
│   │   ├── users.controller.ts
│   │   ├── users.service.ts
│   │   ├── users.module.ts
│   │   └── dto/
├── common/             # Shared code
│   ├── guards/
│   ├── interceptors/
│   └── filters/
├── config/             # Config files
├── prisma/             # Prisma schema
└── main.ts            # Entry point
```

### 4. Root-Level Files
Always include these.

```
your-repo/
├── .gitignore
├── README.md
├── CONTRIBUTING.md      # How to contribute
├── LICENSE
├── package.json
├── .eslintrc.js       # Lint config
├── .prettierrc         # Format config
├── .github/           # GitHub-specific files
│   └── workflows/     # GitHub Actions
├── .husky/            # Git hooks
└── .env.example       # Example env vars
```

## Best Practices
- **Consistency**: Keep structure consistent across repos
- **Naming**: Use clear, descriptive folder names
- **Colocation**: Keep related code together
- **Separation**: Separate concerns (src vs tests, etc.)
- **Flat**: Don't nest folders too deep
- **Document**: Add a small README in complex folders
