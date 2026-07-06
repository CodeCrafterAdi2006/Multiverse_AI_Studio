# Skill: Rate Limiting & Brute-Force Protection (Redis)

## Purpose
To protect your application from automated attacks, such as brute-force login attempts, DDoS attacks, and API scraping, by limiting the number of requests a user (or IP address) can make within a specific timeframe.

## When to Use
- On sensitive endpoints (e.g., `POST /login`, `POST /signup`, `POST /forgot-password`)
- On public APIs to prevent resource exhaustion and manage quotas
- To block aggressive web scrapers and crawlers
- When protecting microservices from cascading failures due to sudden traffic spikes

## Procedure

### 1. The Strategy: Fixed Window vs. Token Bucket
- **Fixed Window**: (e.g., 100 requests per minute). Simplest but can allow double the traffic at the edge of the window.
- **Token Bucket/Sliding Window**: More complex but provides a smoother flow of requests.

### 2. Implementation Example (Express + Redis)
Using the `express-rate-limit` and `rate-limit-redis` libraries.

**Installation**:
```bash
npm install express-rate-limit rate-limit-redis redis
```

**Setup**:
```javascript
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const { createClient } = require('redis');

const redisClient = createClient({ url: 'redis://localhost:6379' });
redisClient.connect();

// 1. Define the general API rate limiter
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
  
  // 2. Use Redis for distributed rate limiting
  store: new RedisStore({
    sendCommand: (...args) => redisClient.sendCommand(args),
  }),
  
  // 3. Custom message when limit is exceeded
  message: {
    error: 'Too many requests',
    message: 'You have exceeded the request limit. Please try again later.'
  }
});

// Apply globally to all /api/ routes
app.use('/api/', apiLimiter);
```

### 3. Protecting Sensitive Endpoints (Strict Limiting)
Use a much stricter limit for login and password reset routes.

```javascript
const loginLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 5, // Limit each IP to 5 failed login attempts per hour
  message: 'Too many login attempts. Your IP has been blocked for 1 hour.',
  store: new RedisStore({
    sendCommand: (...args) => redisClient.sendCommand(args),
    prefix: 'rl-login:' // Separate prefix for login limits
  })
});

app.post('/api/auth/login', loginLimiter, (req, res) => {
  // ... login logic ...
});
```

### 4. Handling Proxy IPs
If your app is behind a proxy (like Nginx, Cloudflare, or Heroku), you must trust the proxy to get the real user's IP address.

```javascript
app.set('trust proxy', 1); // Trust the first proxy
```

## Best Practices
- **Use Redis for Distributed Apps**: If you have multiple server instances, local memory limiting won't work. Redis ensures all instances share the same counter.
- **Inform the User**: Use the standard `Retry-After` header to tell the user (or their browser) exactly how long they should wait before trying again.
- **Whitelisting**: Allow trusted IP addresses (e.g., internal services, specific partners) to bypass rate limits.
- **Dynamic Limits**: Consider different limits based on the user's plan (e.g., Free vs. Premium).
- **Log Blocked Requests**: Monitor your logs for IPs that frequently hit the rate limit. This can help you identify and permanently block malicious actors at the firewall level (e.g., via AWS WAF or Cloudflare).
- **Graceful Degradation**: If Redis is down, ensure your rate limiter fails "open" (allows requests) rather than blocking all traffic, unless security is more critical than availability.