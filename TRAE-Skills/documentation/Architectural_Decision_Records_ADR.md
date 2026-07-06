# Skill: Architectural Decision Records (ADR)

## Purpose
To document the "Why" behind significant architectural decisions in a way that is easily searchable and immutable over time. ADRs provide context for future developers about the constraints, trade-offs, and rationale that led to a specific system design, preventing "architectural amnesia."

## When to Use
- When choosing a primary database (e.g., PostgreSQL vs. MongoDB)
- When adopting a new framework or major library (e.g., React vs. Vue, Next.js)
- When defining a communication protocol between services (e.g., REST, GraphQL, gRPC)
- When implementing a core design pattern (e.g., CQRS, Event Sourcing)

## Procedure

### 1. The Structure of an ADR
An ADR should be a short, focused Markdown file (usually stored in a `/docs/adr/` folder).

**ADR Template**:
- **Title**: Short and descriptive (e.g., `ADR 001: Use PostgreSQL for User Data`)
- **Date**: YYYY-MM-DD
- **Status**: `Proposed`, `Accepted`, `Deprecated`, or `Superseded` (by ADR XXX)
- **Context**: What is the problem we are solving? What are the constraints?
- **Decision**: What did we decide to do?
- **Consequences**: What are the trade-offs? What is the impact (positive and negative)?

### 2. Format Example

```markdown
# ADR 005: Use GraphQL for Frontend-Backend Communication

**Status**: Accepted  
**Date**: 2023-10-27

## Context
Our current REST API requires multiple round-trips to fetch data for the dashboard, leading to high latency on mobile devices. Frontend developers are frequently blocked waiting for new REST endpoints to be created.

## Decision
We will use GraphQL (Apollo Server/Client) as the primary communication layer between our web/mobile apps and our microservices.

## Consequences
- **Positive**: Frontend can query exactly what they need, reducing payload size.
- **Positive**: Schema introspection provides better documentation and type safety.
- **Negative**: Increased complexity in handling caching (N+1 problem).
- **Negative**: Steep learning curve for the team compared to REST.
```

### 3. Managing ADRs
- **Immutable**: Once an ADR is `Accepted`, it should not be edited. If the decision changes later, create a *new* ADR that `Supersedes` the old one.
- **Sequential Numbering**: Use a 3-digit prefix (e.g., `001`, `002`) to maintain order.
- **Git Flow**: ADRs should be submitted as Pull Requests. This allows the team to discuss and refine the decision before it's officially accepted.

## Best Practices
- **Focus on the "Why"**: Don't just document the decision; document the *alternatives* that were rejected and the specific reasons why.
- **Keep it Short**: An ADR should be readable in 5 minutes. If it's too long, it might be a Technical Spec instead.
- **One Decision Per ADR**: Don't bundle unrelated decisions (e.g., "Use React and PostgreSQL") into one file.
- **Visible to All**: Store ADRs in the main repository so every developer can find them.
- **Refer to ADRs in PRs**: When a PR implements a major decision, link to the relevant ADR in the description.