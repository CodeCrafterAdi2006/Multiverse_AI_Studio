# Skill: Role-Based Access Control (RBAC)

## Purpose
To manage user permissions in a systematic and scalable way. RBAC allows you to define "Roles" (e.g., `Admin`, `Editor`, `User`) and assign "Permissions" (e.g., `read:users`, `write:posts`) to those roles. Users are then assigned roles, and the application checks if a user's role has the required permission to perform an action.

## When to Use
- When building multi-user applications with different levels of access
- To protect specific API endpoints or UI elements based on user types
- When managing large organizations with complex permission structures
- To improve security by ensuring users only have the permissions they need (Principle of Least Privilege)

## Procedure

### 1. Define the Role-Permission Mapping
Create a clear mapping of which roles have which permissions.

```javascript
const ROLES = {
  ADMIN: 'admin',
  EDITOR: 'editor',
  USER: 'user'
};

const PERMISSIONS = {
  READ_USERS: 'read:users',
  WRITE_POSTS: 'write:posts',
  DELETE_POSTS: 'delete:posts',
  MANAGE_SETTINGS: 'manage:settings'
};

const ROLE_PERMISSIONS = {
  [ROLES.ADMIN]: [
    PERMISSIONS.READ_USERS,
    PERMISSIONS.WRITE_POSTS,
    PERMISSIONS.DELETE_POSTS,
    PERMISSIONS.MANAGE_SETTINGS
  ],
  [ROLES.EDITOR]: [
    PERMISSIONS.WRITE_POSTS,
    PERMISSIONS.DELETE_POSTS
  ],
  [ROLES.USER]: [
    PERMISSIONS.WRITE_POSTS
  ]
};
```

### 2. Implementation: Middleware (Node.js/Express)
Create a reusable middleware function to check for permissions.

```javascript
function checkPermission(requiredPermission) {
  return (req, res, next) => {
    const userRole = req.user.role; // Assume user info is attached to req (e.g., from JWT)
    const userPermissions = ROLE_PERMISSIONS[userRole] || [];

    if (userPermissions.includes(requiredPermission)) {
      next();
    } else {
      res.status(403).json({ error: 'Forbidden: Insufficient permissions' });
    }
  };
}

// 3. Protect routes
app.get('/api/users', checkPermission(PERMISSIONS.READ_USERS), (req, res) => {
  // ...
});

app.delete('/api/posts/:id', checkPermission(PERMISSIONS.DELETE_POSTS), (req, res) => {
  // ...
});
```

### 4. Implementation: UI Logic (React)
Show or hide elements based on user permissions.

```tsx
export const PostActions = ({ post, user }) => {
  const canDelete = ROLE_PERMISSIONS[user.role].includes(PERMISSIONS.DELETE_POSTS);

  return (
    <div>
      <button>Edit</button>
      {canDelete && <button>Delete</button>}
    </div>
  );
};
```

## Best Practices
- **Prefer Permissions over Roles**: Always check for specific permissions (`can:delete_post`) rather than checking for roles (`is:admin`). This makes your system more flexible if you need to add a new role later or change a role's permissions.
- **Hierarchical Roles (Optional)**: If roles are strictly nested (e.g., Admin is always an Editor, Editor is always a User), you can simplify your mapping or use a library that supports role inheritance.
- **Store Roles in JWT**: Include the user's role in their JWT payload so you don't have to query the database on every request to check permissions.
- **Audit Logs**: For critical actions (e.g., `manage:settings`), log which user performed the action and when.
- **Dynamic Permissions (Optional)**: For very complex systems, store role-permission mappings in a database instead of hardcoding them. This allows admins to change permissions without redeploying the app.
- **Use a Library**: For advanced scenarios (e.g., Attribute-Based Access Control - ABAC), consider using libraries like `accesscontrol` or `casl`.