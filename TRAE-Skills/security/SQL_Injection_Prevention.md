# Skill: SQL Injection Prevention

## Purpose
To prevent malicious users from executing arbitrary SQL code against your database, which could lead to data breaches, data loss, or unauthorized access.

## When to Use
- When writing raw SQL queries in any backend language
- When building search filters, login forms, or data entry endpoints
- When migrating legacy codebases that rely on string concatenation for SQL queries

## Procedure

### 1. The Vulnerability (String Concatenation)
Never concatenate user input directly into a SQL string.

**❌ VULNERABLE CODE (Node.js / pg)**
```javascript
const username = req.body.username;
// If username is "admin' OR '1'='1", this logs them in as admin!
const query = `SELECT * FROM users WHERE username = '${username}'`;
const result = await client.query(query);
```

### 2. The Solution: Parameterized Queries (Prepared Statements)
Always use parameterized queries. The database driver sends the query structure and the data separately, ensuring the data is treated strictly as a literal value, not as executable code.

**✅ SECURE CODE (Node.js / pg)**
```javascript
const username = req.body.username;
// The $1 acts as a placeholder
const query = 'SELECT * FROM users WHERE username = $1';
const values = [username];

// The driver safely escapes the values
const result = await client.query(query, values);
```

### 3. Using ORMs and Query Builders
Modern ORMs (Prisma, TypeORM, Sequelize) and Query Builders (Knex, Kysely) handle parameterization automatically for most operations.

**✅ SECURE CODE (Prisma)**
```javascript
const user = await prisma.user.findUnique({
  where: {
    username: req.body.username // Prisma parameterizes this automatically
  }
});
```

### 4. Danger Zones in ORMs (Raw Queries)
Even when using ORMs, developers sometimes need to write raw SQL for complex queries. You must still use parameterization.

**❌ VULNERABLE (Prisma Raw)**
```javascript
const search = req.query.q;
// Vulnerable to injection!
const users = await prisma.$queryRawUnsafe(`SELECT * FROM User WHERE name LIKE '%${search}%'`);
```

**✅ SECURE (Prisma Raw)**
```javascript
const search = `%${req.query.q}%`;
// Prisma's $queryRaw uses template literals to parameterize values safely
const users = await prisma.$queryRaw`SELECT * FROM User WHERE name LIKE ${search}`;
```

## Best Practices
- **Use Parameterized Queries Everywhere**: No exceptions. Even for internal tools or scripts.
- **Sanitize Input**: While parameterization prevents SQL injection, validating input (e.g., using Zod to ensure an email is actually an email) provides defense-in-depth and prevents logic errors.
- **Principle of Least Privilege**: The database user account used by your application should only have the permissions it needs. Don't use the `root` or `postgres` superuser for your API. If a table is read-only, grant only `SELECT` permissions.
- **Avoid Dynamic Table/Column Names**: Parameterized queries cannot be used for table or column names (e.g., `SELECT * FROM $1`). If you must dynamically select a table, use a strict whitelist in your application code to validate the name before building the query string.