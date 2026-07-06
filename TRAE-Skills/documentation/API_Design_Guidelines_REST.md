# Skill: API Design Guidelines (REST/JSON)

## Purpose
To establish a consistent, intuitive, and future-proof set of rules for designing RESTful APIs. Good API design improves developer experience (DX), simplifies maintenance, and ensures consistency across microservices.

## When to Use
- When designing new API endpoints or versioning existing ones
- When establishing an API-first development process
- When creating documentation for external consumers
- When building backend services that communicate with multiple frontends (Mobile, Web, IoT)

## Procedure

### 1. Resource Naming (URIs)
Resources should be **nouns**, never verbs. Use plural nouns for consistency.

**❌ BAD**: `GET /getUsers`, `POST /createUser`
**✅ GOOD**: `GET /users`, `POST /users`

**Resource Hierarchy**:
`GET /users/123/orders/456` (Order 456 belonging to User 123)

### 2. HTTP Methods (Verbs)
Use HTTP verbs to define the action.

- `GET`: Retrieve a resource or collection. (Idempotent, safe)
- `POST`: Create a new resource. (Non-idempotent)
- `PUT`: Replace a resource entirely. (Idempotent)
- `PATCH`: Update a resource partially. (Non-idempotent)
- `DELETE`: Remove a resource. (Idempotent)

### 3. Status Codes
Use standard HTTP status codes to communicate the result.

- `200 OK`: Successful request.
- `201 Created`: Successful resource creation.
- `204 No Content`: Successful request, but no response body (e.g., after DELETE).
- `400 Bad Request`: Client-side error (invalid input).
- `401 Unauthorized`: Missing or invalid authentication.
- `403 Forbidden`: Authenticated, but no permission for this resource.
- `404 Not Found`: Resource does not exist.
- `429 Too Many Requests`: Rate limit exceeded.
- `500 Internal Server Error`: Server-side crash or unexpected error.

### 4. Query Parameters (Filtering, Sorting, Pagination)
Don't include filters in the path. Use query parameters instead.

- **Filtering**: `GET /users?status=active`
- **Sorting**: `GET /users?sort=-created_at` (Prefix with `-` for descending)
- **Pagination**: `GET /users?page=2&limit=50` (or `offset=50&limit=50`)

### 5. Error Response Format
Always return a consistent JSON structure for errors.

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Invalid email address format",
    "details": [
      { "field": "email", "issue": "must be a valid email" }
    ]
  }
}
```

## Best Practices
- **Version Your API**: Use URI versioning (e.g., `/v1/users`) or header versioning to avoid breaking existing clients when making major changes.
- **Use JSON Only**: Set the `Content-Type: application/json` header and always return JSON objects (not arrays) at the top level for future extensibility.
- **Use HATEOAS (Optional but Good)**: Provide links to related resources in the response body to make the API discoverable.
- **CamelCase vs snake_case**: Choose one for your keys and be consistent. `snake_case` is common in many public APIs (GitHub, Stripe).
- **Security First**: Never include sensitive data (passwords, internal IDs, debug info) in the response body.