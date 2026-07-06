# Skill: Content Security Policy (CSP)

## Purpose
To provide a powerful, browser-based layer of defense against Cross-Site Scripting (XSS), data injection, and clickjacking attacks. CSP allows you to explicitly define which domains and sources of content (scripts, styles, images, iframes) are trusted by your web application.

## When to Use
- When deploying any public-facing web application
- When including third-party scripts (e.g., Google Analytics, Stripe, HubSpot)
- To prevent malicious actors from injecting unauthorized scripts into your pages
- When handling sensitive user data or financial transactions

## Procedure

### 1. How CSP Works
The browser receives the CSP policy via a `Content-Security-Policy` HTTP header (preferred) or a `<meta>` tag. If a script or resource violates the policy, the browser will block it and optionally report the violation to a URI you specify.

### 2. Basic Policy Example
A strict policy that only allows content from the same origin.

**HTTP Header**:
```http
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none';
```

### 3. Realistic Policy for Modern Apps
Most apps need to allow specific external domains (e.g., for analytics or fonts).

```http
Content-Security-Policy: 
  default-src 'self'; 
  script-src 'self' https://www.google-analytics.com https://js.stripe.com;
  style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
  font-src 'self' https://fonts.gstatic.com;
  img-src 'self' data: https://images.unsplash.com;
  connect-src 'self' https://api.myapp.com;
  frame-src 'self' https://js.stripe.com;
  object-src 'none';
  base-uri 'self';
  form-action 'self';
  frame-ancestors 'none';
  upgrade-insecure-requests;
```

### 4. Directives Explained
- `default-src 'self'`: The fallback for other directives. Only allow content from your own domain.
- `script-src`: Define trusted sources for JavaScript.
- `style-src`: Define trusted sources for CSS. (Avoid `'unsafe-inline'` if possible).
- `img-src`: Define trusted sources for images. Use `data:` to allow Base64 encoded images.
- `connect-src`: Define which URLs your app can call via `fetch()` or `XMLHttpRequest`.
- `frame-src`: Define which domains can be embedded in an `<iframe>`.
- `object-src 'none'`: Disable `<object>`, `<embed>`, and `<applet>` tags (often used for Flash/Java exploits).
- `frame-ancestors 'none'`: Prevents your site from being embedded in an iframe on *other* sites (Clickjacking protection).
- `upgrade-insecure-requests`: Automatically converts all HTTP requests to HTTPS.

### 5. Implementation (Express/Helmet)
Use the `helmet` middleware to automatically set secure headers, including CSP.

```javascript
const express = require('express');
const helmet = require('helmet');

const app = express();

app.use(
  helmet.contentSecurityPolicy({
    useDefaults: true,
    directives: {
      "script-src": ["'self'", "https://example.com"],
      "style-src": ["'self'", "https://fonts.googleapis.com"],
    },
  })
);
```

## Best Practices
- **Use 'self' by default**: Never use `*` or `https:` as a source. Be specific about the domains you trust.
- **Avoid `'unsafe-inline'` and `'unsafe-eval'`**: These significantly weaken your protection. If you must use inline scripts, use a **Nonce** (number used once) or a **Hash** to uniquely identify them.
- **Report-Only Mode**: Before rolling out a strict policy, use the `Content-Security-Policy-Report-Only` header. This will log violations to a specified endpoint without actually blocking any resources, allowing you to debug your policy.
- **CSP Evaluator**: Use Google's [CSP Evaluator](https://csp-evaluator.withgoogle.com/) to check if your policy has any bypasses or weaknesses.
- **Strict Content-Type**: Ensure your server sends the correct `Content-Type` headers. CSP works best when combined with `X-Content-Type-Options: nosniff`.
- **Refine Over Time**: As your app grows, keep your CSP updated. Remove domains you no longer use to maintain a tight security posture.