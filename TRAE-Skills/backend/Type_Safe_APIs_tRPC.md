# Skill: Type-Safe APIs with tRPC

## Purpose
To build end-to-end type-safe APIs without schemas or code generation, sharing types between frontend and backend.

## When to Use
- When building full-stack TypeScript applications
- For faster development with type safety
- When you want to avoid API schema duplication
- For Next.js apps (tRPC integrates perfectly)
- When you want auto-completion for API calls

## Procedure

### 1. Basic tRPC Setup (Next.js App Router)
Set up tRPC with Next.js App Router.

```typescript
// server/api/trpc/[trpc]/route.ts
import { initTRPC } from '@trpc/server';
import { fetchRequestHandler } from '@trpc/server/adapters/fetch';

const t = initTRPC.create();

// Define procedures
const publicProcedure = t.procedure;
const router = t.router;

// Create app router
const appRouter = router({
  hello: publicProcedure
    .input((val: unknown) => {
      if (typeof val === 'string') return val;
      throw new Error('Invalid input');
    })
    .query(({ input }) => {
      return {
        message: `Hello, ${input}!`,
        timestamp: new Date().toISOString()
      };
    }),
  addUser: publicProcedure
    .input((val: unknown) => {
      if (typeof val !== 'object' || val === null) throw new Error('Invalid input');
      const { name, email } = val as { name: string; email: string };
      if (typeof name !== 'string' || typeof email !== 'string') throw new Error('Invalid input');
      return { name, email };
    })
    .mutation(({ input }) => {
      return {
        id: Math.random().toString(36).substr(2, 9),
        name: input.name,
        email: input.email,
        createdAt: new Date().toISOString()
      };
    })
});

// Export router type
export type AppRouter = typeof appRouter;

// Handler
function handler(req: Request) {
  return fetchRequestHandler({
    endpoint: '/api/trpc',
    req,
    router: appRouter,
    createContext: () => ({}),
  });
}

export { handler as GET, handler as POST };
```

### 2. Client Setup
Set up the tRPC client.

```typescript
// lib/trpc.ts
import { createTRPCReact } from '@trpc/react-query';
import type { AppRouter } from '@/server/api/trpc/[trpc]/route';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { httpBatchLink } from '@trpc/client';

export const trpc = createTRPCReact<AppRouter>();

export function TRPCProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  const [trpcClient] = useState(() =>
    trpc.createClient({
      links: [
        httpBatchLink({
          url: '/api/trpc',
        }),
      ],
    })
  );

  return (
    <trpc.Provider client={trpcClient} queryClient={queryClient}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </trpc.Provider>
  );
}
```

### 3. Use in Components
Call tRPC procedures in React components.

```tsx
// app/page.tsx
'use client';

import { trpc } from '@/lib/trpc';

export default function Home() {
  // Query procedure
  const { data: helloData, isLoading: helloLoading } = trpc.hello.useQuery('World');
  
  // Mutation procedure
  const addUserMutation = trpc.addUser.useMutation();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const handleAddUser = async () => {
    const result = await addUserMutation.mutateAsync({ name, email });
    console.log('User added:', result);
    setName('');
    setEmail('');
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl mb-4">tRPC Demo</h1>
      
      <div className="mb-8">
        <h2 className="text-xl mb-2">Hello Query</h2>
        {helloLoading ? <p>Loading...</p> : <p>{helloData?.message}</p>}
      </div>

      <div className="mb-8">
        <h2 className="text-xl mb-2">Add User Mutation</h2>
        <input
          type="text"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="border p-2 mr-2"
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border p-2 mr-2"
        />
        <button
          onClick={handleAddUser}
          disabled={addUserMutation.isPending}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          {addUserMutation.isPending ? 'Adding...' : 'Add User'}
        </button>
        {addUserMutation.data && (
          <p className="mt-2 text-green-600">
            User added: {addUserMutation.data.name} ({addUserMutation.data.id})
          </p>
        )}
      </div>
    </div>
  );
}
```

### 4. Middleware & Context
Add authentication and context.

```typescript
// server/api/trpc/[trpc]/route.ts
import { initTRPC, TRPCError } from '@trpc/server';
import { getServerSession } from 'next-auth';

const t = initTRPC.context<typeof createContext>().create();

// Context
const createContext = async (opts: any) => {
  const session = await getServerSession();
  return {
    session,
    user: session?.user,
  };
};

// Middleware
const isAuthenticated = t.middleware(({ ctx, next }) => {
  if (!ctx.user) {
    throw new TRPCError({ code: 'UNAUTHORIZED' });
  }
  return next({
    ctx: {
      ...ctx,
      user: ctx.user,
    },
  });
});

const protectedProcedure = t.procedure.use(isAuthenticated);

// App router
const appRouter = router({
  // Public procedures
  hello: publicProcedure.query(() => ({ message: 'Hello!' })),
  
  // Protected procedures
  getProfile: protectedProcedure
    .query(({ ctx }) => {
      return {
        id: ctx.user.id,
        name: ctx.user.name,
        email: ctx.user.email,
      };
    }),
  
  // With Zod validation
  createPost: protectedProcedure
    .input(z.object({
      title: z.string().min(1).max(100),
      content: z.string().min(1),
      tags: z.array(z.string()).optional(),
    }))
    .mutation(({ ctx, input }) => {
      return {
        id: Math.random().toString(36).substr(2, 9),
        title: input.title,
        content: input.content,
        tags: input.tags || [],
        authorId: ctx.user.id,
        createdAt: new Date().toISOString()
      };
    })
});
```

### 5. Subscriptions (WebSockets)
Real-time subscriptions with tRPC.

```typescript
// Server
import { observable } from '@trpc/server/observable';

const appRouter = router({
  time: publicProcedure.subscription(() => {
    return observable((emit) => {
      const interval = setInterval(() => {
        emit.next(new Date().toISOString());
      }, 1000);

      return () => clearInterval(interval);
    });
  }),
  chat: protectedProcedure
    .input(z.object({ roomId: z.string() }))
    .subscription(({ ctx, input }) => {
      return observable((emit) => {
        // Subscribe to chat room
        const unsubscribe = subscribeToRoom(input.roomId, (message) => {
          emit.next(message);
        });
        return unsubscribe;
      });
    })
});

// Client
function ChatRoom({ roomId }: { roomId: string }) {
  const [messages, setMessages] = useState<string[]>([]);
  
  const chatSubscription = trpc.chat.useSubscription({ roomId }, {
    onData: (message) => {
      setMessages(prev => [...prev, message]);
    },
  });

  return (
    <div>
      {chatSubscription.isLoading && <p>Connecting...</p>}
      {messages.map((msg, i) => (
        <p key={i}>{msg}</p>
      ))}
    </div>
  );
}
```

## Best Practices
- **Zod Validation**: Always use Zod for input validation
- **Procedure Organization**: Group related procedures in routers
- **Middleware**: Use middleware for auth, logging, rate limiting
- **Error Handling**: Throw TRPCError with appropriate codes
- **React Query**: Leverage React Query for caching and invalidation
- **Batching**: Use httpBatchLink to batch requests
- **Type Safety**: Never use `any`, rely on inferred types
- **Inference**: Let tRPC infer types automatically
