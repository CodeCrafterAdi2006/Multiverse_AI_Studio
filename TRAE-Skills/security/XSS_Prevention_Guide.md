# Skill: XSS Prevention & Sanitization

## Purpose
To protect users from Cross-Site Scripting (XSS) attacks, where malicious actors inject scripts into a web application to steal cookies, hijack sessions, or deface websites. XSS occurs when untrusted data is rendered on a page without proper validation or encoding.

## When to Use
- When displaying user-generated content (e.g., comments, profiles, forum posts)
- When building search results pages that reflect user queries
- When using dangerouslySetInnerHTML in React or similar features in other frameworks
- To secure URLs that accept dynamic parameters (e.g., `?redirect_url=...`)

## Procedure

### 1. The Strategy: Encode vs. Sanitize
- **Encoding**: Convert characters to their HTML entities (e.g., `<` becomes `&lt;`). Use this for simple text display. Most modern frameworks (React, Vue) do this automatically.
- **Sanitization**: Remove or strip dangerous HTML tags (e.g., `<script>`) while allowing safe ones (e.g., `<b>`). Use this when you *must* allow users to provide some HTML (like a rich text editor).

### 2. Implementation: HTML Sanitization (Node.js/Frontend)
Using the `dompurify` library, which is the industry standard.

**Installation**:
```bash
npm install dompurify jsdom # jsdom is needed for backend usage
```

**Usage (Backend/Node.js)**:
```javascript
const createDOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');

const window = new JSDOM('').window;
const DOMPurify = createDOMPurify(window);

function cleanUserInput(dirtyHtml) {
  return DOMPurify.sanitize(dirtyHtml, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'],
    ALLOWED_ATTR: ['href']
  });
}
```

**Usage (Frontend/React)**:
```tsx
import DOMPurify from 'dompurify';

export const UserContent = ({ html }: { html: string }) => {
  // Always sanitize before using dangerouslySetInnerHTML
  const cleanHtml = DOMPurify.sanitize(html);
  
  return <div dangerouslySetInnerHTML={{ __html: cleanHtml }} />;
};
```

### 3. Securing URLs (Redirects)
Never redirect to a URL provided by a user without validation.

**❌ VULNERABLE**:
```javascript
app.get('/login', (req, res) => {
  const next = req.query.next;
  res.redirect(next); // Vulnerable to Open Redirect (next=javascript:alert(1))
});
```

**✅ SECURE**:
```javascript
function safeRedirect(url) {
  // Only allow relative paths or a specific whitelist of domains
  if (url.startsWith('/') && !url.startsWith('//')) {
    return url;
  }
  return '/dashboard'; // Default fallback
}
```

### 4. Input Validation (Zod)
Use Zod to ensure input is in the expected format before it even reaches your sanitization logic.

```javascript
const { z } = require('zod');

const CommentSchema = z.object({
  content: z.string().min(1).max(1000), // Enforce length limits
  author: z.string().regex(/^[a-zA-Z0-9]+$/) // Only allow alphanumeric
});
```

## Best Practices
- **Content Security Policy (CSP)**: CSP is your second line of defense. Even if XSS occurs, a good CSP will prevent the malicious script from executing.
- **HttpOnly Cookies**: Store session tokens in cookies with the `HttpOnly` flag. This makes them inaccessible to JavaScript, preventing them from being stolen via XSS.
- **Sanitize on Output**: Always sanitize data just before you render it, rather than just before you save it to the database. This ensures that even if your sanitization logic improves later, your stored data remains "raw".
- **Avoid `eval()` and `new Function()`**: These can be used to execute arbitrary strings as code.
- **Validate Everything**: Treat all data from the client (URLs, cookies, headers, body) as untrusted.
- **Use Modern Frameworks**: React and Vue provide built-in protection by encoding text by default. Use their "dangerously" features only when absolutely necessary and with extreme caution.