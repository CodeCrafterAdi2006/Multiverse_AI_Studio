# Skill: User Story Mapping (Agile)

## Purpose
To visualize the entire user journey within an application and identify the core features, dependencies, and Minimum Viable Product (MVP) based on user needs rather than a flat backlog of tasks.

## When to Use
- When initiating a new project or major product feature
- When prioritizing a backlog of features with stakeholders
- When identifying gaps in the user experience (UX)
- To align a development team on the "Big Picture" before starting work

## Procedure

### 1. The Concept (Hierarchy)
- **User Personas**: Who are we building this for? (e.g., "End User", "Admin")
- **Activities (The Backbone)**: High-level tasks users perform. (e.g., "Manage Orders")
- **Steps (The Ribs)**: Specific actions within an activity. (e.g., "View Order List", "Edit Order Details", "Cancel Order")
- **User Stories (The Flesh)**: Small, deliverable features. (e.g., "As a user, I want to filter orders by date")

### 2. Mapping the Journey (Example: E-commerce)
1. **Persona**: Customer
2. **Activities**: Browse Products -> Cart -> Checkout -> Post-Purchase
3. **Steps (Browse Products)**: Search -> View Details -> Filter -> Sort
4. **Stories (Search)**:
    - Search by name (MVP)
    - Search by category (MVP)
    - Search by SKU (Release 2)
    - Autocomplete (Release 3)

### 3. Slicing for MVP
Draw a horizontal line across the map.
- **Above the Line**: The absolute minimum stories needed to complete the user journey. This is your **MVP**.
- **Below the Line**: Future releases, optimizations, and "nice-to-have" features.

### 4. Refining Stories (INVEST Principle)
Ensure every story in the map is:
- **I**ndependent: Can be developed separately.
- **N**egotiable: Not a rigid contract; open to discussion.
- **V**aluable: Provides clear value to the user.
- **E**stimable: The team can estimate the effort.
- **S**mall: Can be completed within a single sprint.
- **T**estable: Has clear acceptance criteria.

### 5. Documenting Acceptance Criteria (Gherkin)
For every story, define clear rules for completion.

```gherkin
Feature: Order Filtering
  Scenario: Filter orders by date range
    Given I am on the "My Orders" page
    And I have 5 orders from last month and 2 from this month
    When I select the date range for "This Month"
    Then I should see only 2 orders in the list
    And the "Total Count" should show 2
```

## Best Practices
- **Involve Everyone**: User Story Mapping should be a collaborative exercise involving Developers, Designers, and Product Owners.
- **Focus on the "Why"**: Every story must have a clear "so that..." statement (e.g., "As a user, I want to filter orders **so that I can quickly find my recent purchases**").
- **Don't Forget Edge Cases**: Map out error states (e.g., "No results found", "Payment failed") as part of the journey.
- **Keep it Physical (or Digital)**: Use tools like Miro, Mural, or physical sticky notes to make the map visual and interactive. Do not just use a spreadsheet.