# Skill: Event Sourcing Pattern

## Purpose
To implement event sourcing architecture, where all changes to application state are stored as a sequence of events, enabling audit trails, temporal queries, and state reconstruction.

## When to Use
- When you need a complete audit trail of all changes
- For systems that require temporal queries (what was the state at time X?)
- When building event-driven systems or microservices
- For complex business processes that benefit from event replay
- When you need to debug by replaying past events

## Procedure

### 1. Define Events
Define immutable events that represent state changes.

```typescript
// events.ts
type UserEvent = 
  | { type: 'USER_CREATED', id: string, name: string, email: string, timestamp: number }
  | { type: 'USER_UPDATED', id: string, name?: string, email?: string, timestamp: number }
  | { type: 'USER_DELETED', id: string, timestamp: number };

interface EventStore {
  append(aggregateId: string, events: UserEvent[]): Promise<void>;
  read(aggregateId: string): Promise<UserEvent[]>;
  readAll(): Promise<UserEvent[]>;
}
```

### 2. Implement Event Store
Create an event store to persist events.

```typescript
import { createClient } from 'redis';

class RedisEventStore implements EventStore {
  private client: ReturnType<typeof createClient>;

  constructor() {
    this.client = createClient();
  }

  async connect() {
    await this.client.connect();
  }

  async append(aggregateId: string, events: UserEvent[]): Promise<void> {
    const key = `events:${aggregateId}`;
    for (const event of events) {
      await this.client.rPush(key, JSON.stringify(event));
    }
    // Publish event for subscribers
    for (const event of events) {
      await this.client.publish('events', JSON.stringify(event));
    }
  }

  async read(aggregateId: string): Promise<UserEvent[]> {
    const key = `events:${aggregateId}`;
    const eventStrings = await this.client.lRange(key, 0, -1);
    return eventStrings.map(str => JSON.parse(str));
  }

  async readAll(): Promise<UserEvent[]> {
    const keys = await this.client.keys('events:*');
    const allEvents: UserEvent[] = [];
    for (const key of keys) {
      const eventStrings = await this.client.lRange(key, 0, -1);
      allEvents.push(...eventStrings.map(str => JSON.parse(str)));
    }
    return allEvents.sort((a, b) => a.timestamp - b.timestamp);
  }
}
```

### 3. Aggregate with Event Sourcing
Create an aggregate that reconstructs state from events.

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  deleted: boolean;
}

class UserAggregate {
  private user: User | null = null;
  private pendingEvents: UserEvent[] = [];

  constructor(private eventStore: EventStore) {}

  async load(id: string): Promise<void> {
    const events = await this.eventStore.read(id);
    for (const event of events) {
      this.applyEvent(event);
    }
  }

  private applyEvent(event: UserEvent): void {
    switch (event.type) {
      case 'USER_CREATED':
        this.user = {
          id: event.id,
          name: event.name,
          email: event.email,
          deleted: false,
        };
        break;
      case 'USER_UPDATED':
        if (this.user) {
          if (event.name) this.user.name = event.name;
          if (event.email) this.user.email = event.email;
        }
        break;
      case 'USER_DELETED':
        if (this.user) {
          this.user.deleted = true;
        }
        break;
    }
  }

  create(id: string, name: string, email: string): void {
    if (this.user) throw new Error('User already exists');
    const event: UserEvent = {
      type: 'USER_CREATED',
      id,
      name,
      email,
      timestamp: Date.now(),
    };
    this.applyEvent(event);
    this.pendingEvents.push(event);
  }

  update(name?: string, email?: string): void {
    if (!this.user || this.user.deleted) throw new Error('User not found or deleted');
    const event: UserEvent = {
      type: 'USER_UPDATED',
      id: this.user.id,
      name,
      email,
      timestamp: Date.now(),
    };
    this.applyEvent(event);
    this.pendingEvents.push(event);
  }

  delete(): void {
    if (!this.user || this.user.deleted) throw new Error('User not found or deleted');
    const event: UserEvent = {
      type: 'USER_DELETED',
      id: this.user.id,
      timestamp: Date.now(),
    };
    this.applyEvent(event);
    this.pendingEvents.push(event);
  }

  async save(): Promise<void> {
    if (this.user && this.pendingEvents.length > 0) {
      await this.eventStore.append(this.user.id, this.pendingEvents);
      this.pendingEvents = [];
    }
  }

  getState(): User | null {
    return this.user;
  }
}
```

### 4. Projections (CQRS)
Build read models from events.

```typescript
class UserProjection {
  private users: Map<string, User> = new Map();

  constructor(private eventStore: EventStore) {}

  async rebuild(): Promise<void> {
    this.users.clear();
    const events = await this.eventStore.readAll();
    for (const event of events) {
      this.apply(event);
    }
  }

  private apply(event: UserEvent): void {
    switch (event.type) {
      case 'USER_CREATED':
        this.users.set(event.id, {
          id: event.id,
          name: event.name,
          email: event.email,
          deleted: false,
        });
        break;
      case 'USER_UPDATED':
        const user = this.users.get(event.id);
        if (user) {
          if (event.name) user.name = event.name;
          if (event.email) user.email = event.email;
        }
        break;
      case 'USER_DELETED':
        const deletedUser = this.users.get(event.id);
        if (deletedUser) {
          deletedUser.deleted = true;
        }
        break;
    }
  }

  getById(id: string): User | undefined {
    return this.users.get(id);
  }

  getAll(): User[] {
    return Array.from(this.users.values()).filter(u => !u.deleted);
  }
}
```

## Best Practices
- **Immutability**: Events should be immutable and never modified
- **Idempotency**: Applying events multiple times should have the same effect
- **Versioning**: Version events to handle schema changes
- **Snapshots**: Use snapshots to optimize loading large aggregates
- **Error Handling**: Handle concurrency with optimistic locking
- **Observability**: Monitor event store performance and consistency
- **Backup**: Regularly back up the event store
- **Testing**: Test event replay and aggregate behavior thoroughly
