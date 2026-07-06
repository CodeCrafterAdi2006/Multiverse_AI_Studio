# Skill: JWT Authentication & Security

## Purpose
To use JSON Web Tokens (JWT) for secure, stateless authentication and authorization. JWTs allow the server to verify the user's identity without having to store session data in a database, making them ideal for scalable web and mobile applications.

## When to Use
- When building scalable microservices or serverless applications
- For mobile applications that need long-lived login sessions
- When delegating authentication to an external provider (like Auth0 or Firebase)
- To avoid "session stickiness" in multi-server environments

## Procedure

### 1. The Anatomy of a JWT
A JWT is composed of three parts, separated by dots:
1. **Header**: Contains the algorithm (e.g., `HS256`) and token type (`JWT`).
2. **Payload**: Contains the claims (e.g., `user_id`, `role`, `exp`).
3. **Signature**: Used to verify that the sender is who they say they are and that the token wasn't tampered with.

### 2. Implementation: Generating and Verifying (Node.js)
Using the `jsonwebtoken` library.

**Installation**:
```bash
npm install jsonwebtoken
```

**Implementation**:
```javascript
const jwt = require('jsonwebtoken');

const SECRET_KEY = process.env.JWT_SECRET_KEY;

// 1. Generate a JWT during login
function generateToken(user) {
  return jwt.sign(
    { sub: user.id, role: user.role }, // Payload
    SECRET_KEY,                       // Secret
    { expiresIn: '1h' }               // Options
  );
}

// 2. Middleware to verify JWT on every request
function verifyToken(req, res, next) {
  const token = req.headers['authorization']?.split(' ')[1]; // Bearer <token>
  
  if (!token) return res.status(401).send('No token provided');

  try {
    const decoded = jwt.verify(token, SECRET_KEY);
    req.user = decoded; // Attach user info to request
    next();
  } catch (err) {
    res.status(403).send('Invalid or expired token');
  }
}
```

### 3. Handling Expiration & Refresh Tokens
- **Access Token**: Short-lived (e.g., 15 minutes). Sent in every request.
- **Refresh Token**: Long-lived (e.g., 7 days). Stored securely (e.g., in an `httpOnly` cookie). Used *only* to get a new access token when the old one expires.

**Refreshing Flow**:
```javascript
app.post('/refresh', async (req, res) => {
  const refreshToken = req.cookies.refreshToken;
  // 1. Verify refresh token signature
  // 2. Check if refresh token is in database (to allow revoking)
  // 3. Generate a new access token
  const newAccessToken = generateToken(user);
  res.json({ accessToken: newAccessToken });
});
```

## Best Practices
- **Never Store Sensitive Data in the Payload**: JWTs are encoded, not encrypted. Anyone can decode the payload at `jwt.io`. Never include passwords, emails, or personal IDs.
- **Use a Strong Secret**: Use a long, random string (at least 256 bits) as your `JWT_SECRET_KEY`.
- **Set an Expiration (`exp`)**: Every JWT should have a short lifespan. This limits the damage if a token is stolen.
- **Use `httpOnly` and `Secure` Cookies**: If you must store tokens in the browser, don't use `localStorage`. Use cookies with `httpOnly: true` to prevent XSS and `Secure: true` to ensure they are only sent over HTTPS.
- **Implement Revocation**: Since JWTs are stateless, you cannot "log out" a user immediately unless you keep a blacklist of revoked tokens in a fast database like Redis.
- **Validate the `iss` (Issuer) and `aud` (Audience)**: Ensure the token was issued by your own server and is intended for your specific application.
- **Use Asymmetric Algorithms (RS256)**: For production systems, use private/public key pairs. The server signs with the private key, and anyone (like other microservices) can verify with the public key. This is more secure than sharing a single secret across services.