# Skill: Diagramming with Mermaid.js

## Purpose
To create complex diagrams (flowcharts, sequence diagrams, gantt charts, etc.) directly within Markdown files using a simple, text-based syntax. This ensures documentation and diagrams stay in sync with the code and are easily versionable via Git.

## When to Use
- When documenting system architecture, data flows, or complex logic
- When explaining authentication sequences (OAuth2, JWT)
- When defining project timelines or state machines
- To avoid using external binary image files for diagrams that change frequently

## Procedure

### 1. Basic Flowchart Syntax
Flowcharts represent processes or workflows.

```mermaid
graph TD
    A[Start] --> B{Is logged in?}
    B -- Yes --> C[Dashboard]
    B -- No --> D[Login Page]
    D --> B
```

### 2. Sequence Diagrams
Perfect for showing interactions between different services or components over time.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant AuthServer
    participant Database

    User->>Frontend: Click Login
    Frontend->>AuthServer: POST /auth/login
    AuthServer->>Database: Query User
    Database-->>AuthServer: User Data
    AuthServer-->>Frontend: JWT Token
    Frontend-->>User: Show Dashboard
```

### 3. Entity Relationship (ER) Diagrams
Useful for documenting database schemas.

```mermaid
erDiagram
    USER ||--o{ POST : writes
    USER {
        string username
        string email
        string password
    }
    POST {
        string title
        string content
        datetime created_at
    }
```

### 4. State Diagrams
Best for documenting complex UI states or business logic transitions.

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Loading: Search clicked
    Loading --> Success: Data fetched
    Loading --> Error: Fetch failed
    Success --> Idle: Clear search
    Error --> Loading: Retry
```

## Best Practices
- **Keep it Simple**: Don't try to fit too much information into a single diagram. Break complex systems into multiple smaller diagrams.
- **Direction Matters**: Use `TD` (Top-Down) or `LR` (Left-to-Right) consistently based on what makes the flow easier to read.
- **Use meaningful labels**: Instead of `A --> B`, use `Start --> Process`.
- **Git Versioning**: Since Mermaid is text, you can see exact changes in diagrams during code reviews (diffs). Always prefer Mermaid over embedded screenshots of diagrams.