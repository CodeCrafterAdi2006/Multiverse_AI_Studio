# Skill: Edge Computing with Vercel & Cloudflare Workers

## Purpose
To build and deploy low-latency, globally distributed edge functions and middleware.

## When to Use
- When you need ultra-low latency for APIs
- For geolocation-based personalization
- When implementing edge caching and performance optimization
- For A/B testing at the edge
- When handling authentication/authorization at the edge

## Procedure

### 1. Vercel Edge Function
Create a simple Vercel Edge Function.

```typescript
// app/api/edge/route.ts
import { NextResponse } from 'next/server';

export const runtime = 'edge';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const name = searchParams.get('name') || 'World';

  // Get geolocation
  const geo = request.geo;
  const ip = request.headers.get('x-forwarded-for') || 'unknown';

  return NextResponse.json({
    message: `Hello, ${name}!`,
    location: {
      city: geo?.city,
      country: geo?.country,
      region: geo?.region,
    },
    ip,
    timestamp: new Date().toISOString()
  }, {
    headers: {
      'Cache-Control': 's-maxage=300, stale-while-revalidate'
    }
  });
}
```

### 2. Vercel Middleware
Run code before requests reach your app.

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Redirect based on country
  const country = request.geo?.country;
  if (country === 'CN') {
    return NextResponse.redirect(new URL('/cn', request.url));
  }

  // A/B testing
  const cookie = request.cookies.get('ab-test');
  let variant = cookie?.value || 'A';
  if (!cookie) {
    variant = Math.random() < 0.5 ? 'A' : 'B';
  }

  const response = NextResponse.next();
  response.cookies.set('ab-test', variant, { path: '/' });
  response.headers.set('x-ab-variant', variant);

  // Auth check
  const authToken = request.cookies.get('auth-token');
  if (request.nextUrl.pathname.startsWith('/dashboard') && !authToken) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return response;
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

### 3. Cloudflare Worker
Create a Cloudflare Worker.

```javascript
// worker.js
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Route handling
    if (url.pathname === '/api/hello') {
      return handleHello(request);
    } else if (url.pathname === '/api/cache') {
      return handleCache(request, env);
    }

    return new Response('Not Found', { status: 404 });
  }
};

async function handleHello(request) {
  const { cf } = request;
  return new Response(JSON.stringify({
    message: 'Hello from Cloudflare Edge!',
    colo: cf.colo,
    country: cf.country,
    city: cf.city,
    timezone: cf.timezone
  }), {
    headers: { 'Content-Type': 'application/json' }
  });
}

async function handleCache(request, env) {
  const cacheKey = request.url;
  const cache = caches.default;

  // Check cache
  let response = await cache.match(cacheKey);
  if (response) {
    return new Response(response.body, {
      ...response,
      headers: {
        ...response.headers,
        'x-cache': 'HIT'
      }
    });
  }

  // Fetch from origin
  response = await fetch('https://api.example.com/data');
  const clonedResponse = new Response(response.body, response);
  clonedResponse.headers.set('x-cache', 'MISS');
  clonedResponse.headers.set('Cache-Control', 's-maxage=60');

  // Cache it
  ctx.waitUntil(cache.put(cacheKey, clonedResponse.clone()));

  return clonedResponse;
}
```

### 4. Cloudflare Worker with KV
Use Cloudflare KV for edge storage.

```javascript
// worker-kv.js
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === '/api/counter') {
      // Get current count
      let count = await env.COUNTER_KV.get('global-count');
      count = count ? parseInt(count) + 1 : 1;

      // Save to KV
      await env.COUNTER_KV.put('global-count', count.toString());

      return new Response(JSON.stringify({ count }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }

    if (url.pathname.startsWith('/api/user/')) {
      const userId = url.pathname.split('/')[3];

      if (request.method === 'GET') {
        const user = await env.USERS_KV.get(`user:${userId}`);
        return new Response(user || '{}', {
          headers: { 'Content-Type': 'application/json' }
        });
      }

      if (request.method === 'POST') {
        const userData = await request.json();
        await env.USERS_KV.put(`user:${userId}`, JSON.stringify(userData));
        return new Response(JSON.stringify({ success: true }), {
          headers: { 'Content-Type': 'application/json' }
        });
      }
    }

    return new Response('Not Found', { status: 404 });
  }
};
```

### 5. Edge Caching with Cloudflare
Implement advanced caching.

```javascript
// worker-cache.js
export default {
  async fetch(request, env) {
    const cache = caches.default;
    let response = await cache.match(request);

    if (!response) {
      // Add cache tags
      const cacheTags = ['api', 'data'];
      const originResponse = await fetch(request, {
        headers: {
          'Cache-Tag': cacheTags.join(',')
        }
      });

      response = new Response(originResponse.body, originResponse);
      response.headers.set('Cache-Control', 's-maxage=3600, stale-while-revalidate=86400');
      response.headers.set('Cache-Tag', cacheTags.join(','));

      // Cache the response
      ctx.waitUntil(cache.put(request, response.clone()));
    }

    return response;
  }
};
```

## Best Practices
- **Cold Starts**: Keep edge functions small and fast
- **Caching**: Use edge caching aggressively
- **Geolocation**: Leverage geolocation for personalization
- **KV Storage**: Use KV for edge-side state
- **Cost**: Monitor edge invocation counts
- **Fallback**: Add fallback for edge failures
- **Testing**: Test with wrangler (Cloudflare) or vercel dev
