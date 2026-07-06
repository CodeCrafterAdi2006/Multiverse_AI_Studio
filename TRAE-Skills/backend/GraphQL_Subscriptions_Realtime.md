# Skill: Real-time GraphQL Subscriptions

## Purpose
To implement real-time data updates in GraphQL APIs using subscriptions over WebSockets.

## When to Use
- When building chat applications or messaging systems
- For real-time collaboration tools (Google Docs-like apps)
- When you need live dashboards or analytics
- For real-time notifications and alerts
- When building multiplayer games

## Procedure

### 1. Server Setup (Apollo Server + Node.js)
Set up a GraphQL server with subscriptions.

```javascript
import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@apollo/server/express4';
import { ApolloServerPluginDrainHttpServer } from '@apollo/server/plugin/drainHttpServer';
import { createServer } from 'http';
import { makeExecutableSchema } from '@graphql-tools/schema';
import { WebSocketServer } from 'ws';
import { useServer } from 'graphql-ws/lib/use/ws';
import express from 'express';
import { PubSub } from 'graphql-subscriptions';

const pubsub = new PubSub();
const MESSAGE_ADDED = 'MESSAGE_ADDED';

const typeDefs = `#graphql
  type Message {
    id: ID!
    content: String!
    user: String!
    createdAt: String!
  }

  type Query {
    messages: [Message!]!
  }

  type Mutation {
    addMessage(content: String!, user: String!): Message!
  }

  type Subscription {
    messageAdded: Message!
  }
`;

const messages = [];

const resolvers = {
  Query: {
    messages: () => messages,
  },
  Mutation: {
    addMessage: (_, { content, user }) => {
      const message = {
        id: String(messages.length + 1),
        content,
        user,
        createdAt: new Date().toISOString(),
      };
      messages.push(message);
      pubsub.publish(MESSAGE_ADDED, { messageAdded: message });
      return message;
    },
  },
  Subscription: {
    messageAdded: {
      subscribe: () => pubsub.asyncIterator([MESSAGE_ADDED]),
    },
  },
};

const schema = makeExecutableSchema({ typeDefs, resolvers });

const app = express();
const httpServer = createServer(app);

const wsServer = new WebSocketServer({
  server: httpServer,
  path: '/graphql',
});

const serverCleanup = useServer({ schema }, wsServer);

const server = new ApolloServer({
  schema,
  plugins: [
    ApolloServerPluginDrainHttpServer({ httpServer }),
    {
      async serverWillStart() {
        return {
          async drainServer() {
            await serverCleanup.dispose();
          },
        };
      },
    },
  ],
});

await server.start();
app.use('/graphql', express.json(), expressMiddleware(server));

const PORT = 4000;
httpServer.listen(PORT, () => {
  console.log(`Server ready at http://localhost:${PORT}/graphql`);
});
```

### 2. Client Setup (Apollo Client + React)
Connect a React client to the subscription.

```javascript
import { ApolloClient, InMemoryCache, ApolloProvider, createHttpLink, split } from '@apollo/client';
import { GraphQLWsLink } from '@apollo/client/link/subscriptions';
import { createClient } from 'graphql-ws';
import { getMainDefinition } from '@apollo/client/utilities';
import { useSubscription, gql } from '@apollo/client';

const httpLink = createHttpLink({
  uri: 'http://localhost:4000/graphql',
});

const wsLink = new GraphQLWsLink(createClient({
  url: 'ws://localhost:4000/graphql',
}));

const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    );
  },
  wsLink,
  httpLink,
);

const client = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache(),
});

const MESSAGE_ADDED_SUBSCRIPTION = gql`
  subscription OnMessageAdded {
    messageAdded {
      id
      content
      user
      createdAt
    }
  }
`;

function Chat() {
  const { data } = useSubscription(MESSAGE_ADDED_SUBSCRIPTION);

  return (
    <div>
      {data?.messageAdded && (
        <div>
          <strong>{data.messageAdded.user}</strong>: {data.messageAdded.content}
        </div>
      )}
    </div>
  );
}

function App() {
  return (
    <ApolloProvider client={client}>
      <Chat />
    </ApolloProvider>
  );
}
```

### 3. Subscription Filters
Filter subscription events based on criteria.

```javascript
const typeDefs = `#graphql
  type Subscription {
    messageAdded(roomId: ID!): Message!
  }
`;

const resolvers = {
  Subscription: {
    messageAdded: {
      subscribe: (_, { roomId }) => pubsub.asyncIterator([`${MESSAGE_ADDED}_${roomId}`]),
    },
  },
  Mutation: {
    addMessage: (_, { content, user, roomId }) => {
      const message = {
        id: String(messages.length + 1),
        content,
        user,
        roomId,
        createdAt: new Date().toISOString(),
      };
      messages.push(message);
      pubsub.publish(`${MESSAGE_ADDED}_${roomId}`, { messageAdded: message });
      return message;
    },
  },
};
```

## Best Practices
- **Authentication**: Authenticate WebSocket connections just like HTTP requests
- **Error Handling**: Handle connection errors and reconnections gracefully
- **Performance**: Use pagination for historical data, subscriptions only for new updates
- **Throttling**: Consider rate limiting subscriptions to prevent abuse
- **Scalability**: Use Redis Pub/Sub instead of in-memory PubSub for production and scaling
- **Monitoring**: Monitor WebSocket connections and subscription performance
