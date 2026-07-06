# Skill: Technical Specification Writing (RFC/Design Doc)

## Purpose
To document the architectural decisions, data models, and implementation plans for a complex feature or system before any code is written. This allows for early feedback, cross-team alignment, and avoids costly architectural mistakes.

## When to Use
- Before starting a task that takes more than 1 week of development
- When introducing a new technology, database, or infrastructure change
- When building features that impact multiple teams or microservices
- To document the rationale behind "why" a specific approach was chosen over others

## Procedure

### 1. Document Structure
A standard Technical Spec should include these core sections:

1. **Overview/Abstract**: 1-2 paragraphs summarizing the problem and the proposed solution.
2. **Background**: Context on why this change is necessary (links to tickets, user research, or performance logs).
3. **Goals & Non-Goals**:
    - **Goals**: What we *must* achieve (e.g., "Reduce latency by 50%").
    - **Non-Goals**: Explicitly state what is *out of scope* to prevent scope creep.
4. **Proposed Architecture**: High-level design, diagrams (Mermaid), and data flow.
5. **Data Model**: Schema changes, new tables, or API contracts.
6. **Detailed Implementation Plan**: Step-by-step breakdown of the work.
7. **Alternatives Considered**: Why we didn't choose other approaches (e.g., "We considered MongoDB but chose PostgreSQL because...").
8. **Security & Performance**: Potential risks and mitigation strategies.
9. **Monitoring & Metrics**: How will we measure success? (e.g., "New Datadog dashboard for error rates").

### 2. The "Alternatives Considered" Section
This is the most important section for senior engineers. It demonstrates depth of thought and prevents repeating past mistakes.
- List at least 2 other ways the problem could have been solved.
- Provide a brief pros/cons list for each.
- Explain the specific trade-offs (e.g., "Option A was faster to build but had higher long-term maintenance costs").

### 3. Review Process
1. **Draft**: Write the spec in Markdown or a collaborative tool (Google Docs, Notion).
2. **Internal Feedback**: Share with your immediate team for technical sanity checks.
3. **Broad Review**: Share with stakeholders (Product, Security, SRE) for sign-off.
4. **Implementation**: Only start coding once the spec is approved.

### 4. Updating the Spec
Specs are living documents. If the implementation plan changes significantly during development, update the spec to reflect the reality.

## Best Practices
- **Write for the Future**: Imagine someone reading this spec 2 years from now. Will they understand *why* these decisions were made?
- **Be Concise**: Use bullet points and diagrams. Avoid "walls of text".
- **Use Clear Language**: Avoid vague terms like "scalable" or "performant". Use numbers (e.g., "Handle 10,000 requests per second").
- **Link Everything**: Link to PRs, Jira tickets, and related architectural docs (ADRs).
- **Acknowledge Trade-offs**: Every architectural decision has a downside. Be honest about them.