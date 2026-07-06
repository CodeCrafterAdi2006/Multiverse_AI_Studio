# Skill: Scalable WebSocket Applications with Socket.IO

## Purpose
To build and scale real-time WebSocket applications using Socket.IO with Redis adapter for horizontal scaling.

## When to Use
- When building chat applications with many concurrent users
- For real-time collaboration tools
- When you need to scale WebSocket servers horizontally
- For live dashboards and real-time analytics
- When building multiplayer games

## Procedure

### 1. Basic Socket.IO Server
Set up a simple Socket.IO server.

```javascript
import express from 'express';
import http from 'http';
import { Server } from 'socket.io';

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "https://your-frontend.com",
    methods: ["GET", "POST"]
  }
});

io.on('connection', (socket) => {
  console.log('User connected:', socket.id);

  socket.on('join-room', (roomId) => {
    socket.join(roomId);
    console.log('User', socket.id, 'joined room', roomId);
  });

  socket.on('send-message', (data) => {
    io.to(data.roomId).emit('new-message', {
      id: Date.now(),
      content: data.content,
      user: data.user,
      timestamp: new Date().toISOString()
    });
  });

  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### 2. Socket.IO Client
Connect from the frontend.

```javascript
import { io } from 'socket.io-client';

const socket = io('https://your-server.com');

socket.on('connect', () => {
  console.log('Connected with ID:', socket.id);
});

socket.on('new-message', (message) => {
  console.log('New message:', message);
  // Update UI with new message
});

// Join a room
socket.emit('join-room', 'room-123');

// Send a message
socket.emit('send-message', {
  roomId: 'room-123',
  content: 'Hello, everyone!',
  user: 'John Doe'
});
```

### 3. Scale with Redis Adapter
Enable horizontal scaling with Redis.

```javascript
import express from 'express';
import http from 'http';
import { Server } from 'socket.io';
import { createAdapter } from '@socket.io/redis-adapter';
import { createClient } from 'redis';

const app = express();
const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: "https://your-frontend.com",
    methods: ["GET", "POST"]
  }
});

// Set up Redis adapter
const pubClient = createClient({ host: 'localhost', port: 6379 });
const subClient = pubClient.duplicate();

Promise.all([pubClient.connect(), subClient.connect()]).then(() => {
  io.adapter(createAdapter(pubClient, subClient));
  console.log('Redis adapter enabled');
});

io.on('connection', (socket) => {
  console.log('User connected:', socket.id);

  socket.on('join-room', (roomId) => {
    socket.join(roomId);
    // Notify everyone in the room
    io.to(roomId).emit('user-joined', socket.id);
  });

  socket.on('send-message', (data) => {
    io.to(data.roomId).emit('new-message', {
      id: Date.now(),
      content: data.content,
      user: data.user,
      timestamp: new Date().toISOString()
    });
  });

  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### 4. Load Balancing with Nginx
Configure Nginx for load balancing.

```nginx
http {
    upstream socketio_servers {
        least_conn;
        server localhost:3001;
        server localhost:3002;
        server localhost:3003;
    }

    server {
        listen 80;
        server_name your-domain.com;

        location /socket.io/ {
            proxy_pass http://socketio_servers/socket.io/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket timeout settings
            proxy_connect_timeout 7d;
            proxy_send_timeout 7d;
            proxy_read_timeout 7d;
        }
    }
}
```

### 5. Authentication
Add JWT authentication to Socket.IO.

```javascript
import jwt from 'jsonwebtoken';

io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  if (!token) {
    return next(new Error('Authentication required'));
  }
  
  try {
    const decoded = jwt.verify(token, 'your-secret-key');
    socket.user = decoded;
    next();
  } catch (error) {
    return next(new Error('Invalid token'));
  }
});

io.on('connection', (socket) => {
  console.log('Authenticated user:', socket.user.id);
  
  socket.on('send-message', (data) => {
    io.to(data.roomId).emit('new-message', {
      id: Date.now(),
      content: data.content,
      userId: socket.user.id,
      username: socket.user.name,
      timestamp: new Date().toISOString()
    });
  });
});
```

### 6. Presence Tracking
Track online users.

```javascript
const onlineUsers = new Map();

io.on('connection', (socket) => {
  const userId = socket.user.id;
  onlineUsers.set(userId, {
    id: userId,
    name: socket.user.name,
    socketId: socket.id
  });

  // Notify everyone that this user came online
  io.emit('user-online', { userId, name: socket.user.name });

  // Send list of online users to new user
  socket.emit('online-users', Array.from(onlineUsers.values()));

  socket.on('disconnect', () => {
    onlineUsers.delete(userId);
    io.emit('user-offline', userId);
  });
});
```

## Best Practices
- **Always Use Adapter**: Use Redis (or other) adapter for scaling
- **Connection State Recovery**: Enable connection state recovery
- **Heartbeats**: Configure appropriate heartbeat intervals
- **Error Handling**: Handle errors gracefully
- **Rate Limiting**: Implement rate limiting to prevent abuse
- **Message Acknowledgements**: Use acknowledgements for important messages
- **Rooms**: Use rooms for efficient message broadcasting
- **Monitoring**: Monitor connection count and message rates
