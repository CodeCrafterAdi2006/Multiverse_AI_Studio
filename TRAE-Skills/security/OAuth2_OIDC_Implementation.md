# Skill: OAuth2 & OpenID Connect (Auth0)

## Purpose
To implement secure, industry-standard authentication and authorization flows in modern applications. OAuth2 allows users to grant third-party applications access to their resources without sharing their passwords, while OpenID Connect (OIDC) adds an identity layer for user authentication.

## When to Use
- When building a "Login with Google/GitHub" feature
- To secure microservices that need to communicate on behalf of a user
- When centralizing authentication for multiple applications (Single Sign-On - SSO)
- To avoid building and maintaining a custom user database and password hashing system

## Procedure

### 1. The Core Flow (Authorization Code Flow with PKCE)
This is the most secure flow for Single Page Apps (SPA) and Mobile Apps.

1. **Authorize**: User clicks "Login". The app redirects to the Auth Server (e.g., Auth0, Okta).
2. **Authenticate**: User logs in on the Auth Server's page.
3. **Code**: Auth Server redirects back to the app with a one-time `code`.
4. **Exchange**: The app exchanges the `code` for an `access_token` and `id_token` using a secure back-channel.
5. **Access**: The app uses the `access_token` to call APIs.

### 2. Integration Example (React + Auth0)

**Installation**:
```bash
npm install @auth0/auth0-react
```

**Setup (`main.tsx`)**:
```tsx
import { Auth0Provider } from '@auth0/auth0-react';

ReactDOM.render(
  <Auth0Provider
    domain="YOUR_AUTH0_DOMAIN"
    clientId="YOUR_CLIENT_ID"
    authorizationParams={{
      redirect_uri: window.location.origin,
      audience: 'https://api.myapp.com' // Your backend API identifier
    }}
  >
    <App />
  </Auth0Provider>,
  document.getElementById('root')
);
```

**Usage in Component**:
```tsx
import { useAuth0 } from '@auth0/auth0-react';

export const LoginButton = () => {
  const { loginWithRedirect, isAuthenticated, user, logout } = useAuth0();

  if (isAuthenticated) {
    return (
      <div>
        <p>Welcome, {user?.name}</p>
        <button onClick={() => logout()}>Logout</button>
      </div>
    );
  }

  return <button onClick={() => loginWithRedirect()}>Log In</button>;
};
```

### 3. Backend Verification (Node.js/Express)
Verify the `access_token` sent in the `Authorization` header.

```javascript
const { auth } = require('express-oauth2-jwt-bearer');

// 1. Configure the JWT verification middleware
const checkJwt = auth({
  audience: 'https://api.myapp.com',
  issuerBaseURL: 'https://YOUR_AUTH0_DOMAIN/',
  tokenSigningAlg: 'RS256'
});

// 2. Protect specific routes
app.get('/api/private', checkJwt, (req, res) => {
  res.json({ message: 'Hello from a private endpoint! Your user ID is ' + req.auth.payload.sub });
});
```

## Best Practices
- **Use PKCE (Proof Key for Code Exchange)**: Mandatory for all frontend/mobile apps to prevent authorization code injection attacks.
- **Short-Lived Access Tokens**: Keep access tokens short-lived (e.g., 1 hour) and use **Refresh Tokens** with rotation to get new ones.
- **Audience & Scopes**: Always specify the `audience` (the API you're calling) and `scopes` (what the app is allowed to do, e.g., `read:profile`, `write:orders`).
- **Validate Tokens on the Server**: Never trust a JWT from a client. Always verify its signature, issuer, and expiration date on your backend using a trusted library.
- **Store Tokens Securely**: Never store tokens in `localStorage`. Use an `httpOnly` cookie or the Auth0 SDK's in-memory storage (which uses web workers to isolate tokens from XSS).