# Skill: CSRF Protection Strategies

## Purpose
To protect users from Cross-Site Request Forgery (CSRF) attacks, where a malicious website tricks a logged-in user's browser into sending unauthorized requests to your application (e.g., changing passwords or making purchases). CSRF exploits the fact that browsers automatically include cookies (like session tokens) in cross-site requests.

## When to Use
- When building web applications that use cookie-based sessions or authentication
- When your application performs state-changing actions (POST, PUT, DELETE, PATCH) via HTML forms or AJAX requests
- To secure banking, e-commerce, and admin-only features

## Procedure

### 1. The Modern Solution: `SameSite` Cookies
The easiest and most powerful defense. Setting the `SameSite` attribute on your cookies tells the browser whether to send cookies in cross-site requests.

- **`Strict`**: Cookies are only sent for first-party requests. (Highest security, but can break external links).
- **`Lax`**: (Default in modern browsers). Cookies are sent for top-level navigation (like clicking a link) but not for cross-site `POST` requests.
- **`None`**: Cookies are sent in all contexts. (Requires `Secure` flag).

**Implementation (Express)**:
```javascript
app.use(session({
  cookie: {
    sameSite: 'lax', // or 'strict'
    secure: true, // Requires HTTPS
    httpOnly: true,
  }
}));
```

### 2. The Traditional Solution: Anti-CSRF Tokens (Double Submit Cookie)
If you need to support older browsers or complex cross-domain setups, use anti-CSRF tokens. The server generates a random, unique token for each session and requires it to be included in every state-changing request.

**Implementation (Express + csurf)**:
```javascript
const csrf = require('csurf');
const cookieParser = require('cookie-parser');

app.use(cookieParser());
app.use(csrf({ cookie: true }));

// 1. Send the token to the client (e.g., via a meta tag or hidden input)
app.get('/form', (req, res) => {
  res.render('send', { csrfToken: req.csrfToken() });
});

// 2. The server will automatically validate the token on POST requests
app.post('/process', (req, res) => {
  res.send('data is being processed');
});
```

### 3. Protecting AJAX/SPA Requests
For Single Page Applications (SPAs), the server can send the CSRF token in a cookie that the frontend can read (non-HttpOnly) and then include in a custom header (like `X-CSRF-TOKEN`).

```javascript
// Server (Express)
res.cookie('XSRF-TOKEN', req.csrfToken());

// Client (Axios)
axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = 'XSRF-TOKEN';
axios.defaults.xsrfHeaderName = 'X-XSRF-TOKEN';
```

## Best Practices
- **Use `SameSite: Lax` by Default**: This is the best balance between security and usability for most applications.
- **Verify the `Origin` and `Referer` Headers**: For critical requests, ensure they are coming from your own domain.
- **Avoid GET for State Changes**: Never use `GET` requests to modify data (e.g., `/delete-account?id=123`). Browsers and proxies often pre-fetch GET requests, and they are much harder to protect against CSRF.
- **Require Re-Authentication for Sensitive Actions**: For critical actions (e.g., changing an email or password), ask the user to re-enter their password or provide a 2FA code, regardless of their current session status.
- **API-Only Apps**: If your API is purely for mobile apps or third-party integrations and doesn't use cookie-based authentication (uses `Authorization: Bearer ...` instead), you are inherently protected against CSRF because browsers don't automatically add custom headers to cross-site requests.
- **Logout CSRF**: Don't forget to protect your logout endpoint! Malicious sites can use CSRF to log users out of your application. Use a POST request for logout.