# Skill: CORS Configuration Best Practices

## Purpose
To correctly configure Cross-Origin Resource Sharing (CORS) in backend applications, ensuring that only trusted domains can access your API while preventing unauthorized cross-origin requests.

## When to Use
- When building APIs consumed by frontend applications hosted on different domains (e.g., `api.example.com` and `app.example.com`)
- When resolving browser errors like `No 'Access-Control-Allow-Origin' header is present on the requested resource`
- When securing microservices that communicate over HTTP

## Procedure

### 1. The Problem with `cors()` Defaults
Many developers simply use `app.use(cors())` without arguments. This is **dangerous** for production because it sets `Access-Control-Allow-Origin: *`, allowing *any* website to make requests to your API.

### 2. Secure Configuration (Express.js Example)

Instead of a wildcard, define an explicit whitelist of allowed origins.

```javascript
const express = require('express');
const cors = require('cors');

const app = express();

// Define allowed origins based on the environment
const whitelist = [
  'https://www.myproductionapp.com',
  'https://admin.myproductionapp.com'
];

// Allow localhost during development
if (process.env.NODE_ENV !== 'production') {
  whitelist.push('http://localhost:3000');
  whitelist.push('http://localhost:5173');
}

const corsOptions = {
  origin: function (origin, callback) {
    // Allow requests with no origin (like mobile apps, curl, or Postman)
    // If you want to block REST clients/mobile apps, remove `!origin`
    if (!origin || whitelist.indexOf(origin) !== -1) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  
  // Allow specific HTTP methods
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  
  // Allow specific headers
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  
  // Allow cookies/sessions to be sent cross-origin
  credentials: true,
  
  // Cache the preflight (OPTIONS) request response for 10 minutes
  // Reduces latency for subsequent requests
  maxAge: 600 
};

// Apply CORS middleware globally
app.use(cors(corsOptions));
```

### 3. Dynamic Subdomains (Regex)
If you have dynamic subdomains (e.g., `tenant1.myapp.com`, `tenant2.myapp.com`), use a regular expression instead of an array.

```javascript
const corsOptions = {
  origin: [
    /https:\/\/[a-z0-9-]+\.myapp\.com$/ // Matches any valid subdomain
  ],
  credentials: true
};
app.use(cors(corsOptions));
```

## Best Practices
- **Never use `*` in production** unless you are building a completely public API (like a weather service or public CDN).
- **Understand Preflight Requests**: Browsers send an `OPTIONS` request before sending a `POST`, `PUT`, or `DELETE` request with custom headers (like `Authorization`). Use the `maxAge` option to cache this preflight response and improve performance.
- **`credentials: true` requires exact origins**: If your API uses cookies for sessions, you MUST set `credentials: true`. However, the CORS specification forbids using `Access-Control-Allow-Origin: *` when credentials are true. You must specify the exact origin.