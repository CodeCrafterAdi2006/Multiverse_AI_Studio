# Skill: Serverless Streaming & Webhooks at Scale

## Purpose
To build high-throughput, real-time streaming APIs and webhook systems using serverless technologies.

## When to Use
- For real-time LLM streaming (OpenAI, Anthropic)
- When building webhook systems for SaaS integrations
- For high-throughput event processing
- When you need serverless SSE (Server-Sent Events)
- For building async task queues with webhook callbacks

## Procedure

### 1. LLM Streaming (Next.js Edge Function)
Stream LLM responses from a serverless function.

```typescript
// app/api/chat/stream/route.ts
import OpenAI from 'openai';
import { OpenAIStream, StreamingTextResponse } from 'ai';

export const runtime = 'edge';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(req: Request) {
  const { messages } = await req.json();

  const response = await openai.chat.completions.create({
    model: 'gpt-4o',
    stream: true,
    messages,
  });

  const stream = OpenAIStream(response, {
    onStart: async () => {
      console.log('Stream started');
    },
    onCompletion: async (completion) => {
      console.log('Stream completed:', completion);
      // Save to database
    },
  });

  return new StreamingTextResponse(stream);
}
```

### 2. Client-Side Streaming
Consume the stream in React.

```tsx
// app/chat/page.tsx
'use client';

import { useChat } from 'ai/react';

export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: '/api/chat/stream',
    onResponse: (response) => {
      console.log('Response received:', response);
    },
    onFinish: (message) => {
      console.log('Finished:', message);
    },
  });

  return (
    <div className="p-8">
      <div className="space-y-4 mb-8">
        {messages.map((m) => (
          <div key={m.id} className="border p-4 rounded">
            <strong>{m.role}:</strong> {m.content}
          </div>
        ))}
      </div>
      
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Say something..."
          className="flex-1 border p-2 rounded"
        />
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
          Send
        </button>
      </form>
    </div>
  );
}
```

### 3. Webhook System (AWS Lambda + SQS)
Build a scalable webhook system with retries.

```typescript
// serverless.yml
service: webhook-service

provider:
  name: aws
  runtime: nodejs20.x
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - sqs:SendMessage
            - sqs:ReceiveMessage
            - sqs:DeleteMessage
          Resource: !GetAtt WebhookQueue.Arn

functions:
  sendWebhook:
    handler: handler.sendWebhook
    events:
      - sqs:
          arn: !GetAtt WebhookQueue.Arn
          batchSize: 1

resources:
  Resources:
    WebhookQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: webhook-queue
        VisibilityTimeout: 60
        RedrivePolicy:
          deadLetterTargetArn: !GetAtt WebhookDLQ.Arn
          maxReceiveCount: 5
    WebhookDLQ:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: webhook-dlq
```

```typescript
// handler.ts
import { SQSClient, SendMessageCommand } from '@aws-sdk/client-sqs';
import axios from 'axios';

const sqs = new SQSClient({ region: process.env.AWS_REGION });
const QUEUE_URL = process.env.WEBHOOK_QUEUE_URL!;

// Send webhook to queue (triggered by your app)
export async function queueWebhook(url: string, payload: any) {
  const command = new SendMessageCommand({
    QueueUrl: QUEUE_URL,
    MessageBody: JSON.stringify({
      url,
      payload,
      attempt: 1,
      maxAttempts: 5,
      createdAt: new Date().toISOString()
    }),
  });
  
  await sqs.send(command);
  return { success: true };
}

// Process webhook from queue
export async function sendWebhook(event: any) {
  for (const record of event.Records) {
    const { url, payload, attempt, maxAttempts } = JSON.parse(record.body);
    
    try {
      await axios.post(url, payload, {
        timeout: 5000,
        headers: {
          'Content-Type': 'application/json',
          'X-Webhook-Signature': generateSignature(payload),
        },
      });
      
      console.log(`Webhook sent to ${url} (attempt ${attempt})`);
    } catch (error) {
      console.error(`Webhook failed to ${url} (attempt ${attempt}):`, error);
      
      if (attempt < maxAttempts) {
        // Requeue with backoff
        await queueWebhook(url, payload);
      } else {
        // Send to DLQ or alert
        await sendToDLQ(record.body, error);
      }
    }
  }
}

function generateSignature(payload: any) {
  const hmac = crypto.createHmac('sha256', process.env.WEBHOOK_SECRET!);
  return hmac.update(JSON.stringify(payload)).digest('hex');
}
```

### 4. Server-Sent Events (SSE)
Build real-time updates with SSE.

```typescript
// app/api/sse/route.ts
import { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      // Send initial message
      controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'connected' })}\n\n`));

      // Send periodic updates
      const interval = setInterval(() => {
        const event = {
          type: 'update',
          timestamp: new Date().toISOString(),
          data: Math.random(),
        };
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(event)}\n\n`));
      }, 2000);

      // Cleanup
      request.signal.addEventListener('abort', () => {
        clearInterval(interval);
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
```

```tsx
// app/sse/page.tsx
'use client';

import { useEffect, useState } from 'react';

export default function SSEPage() {
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    const eventSource = new EventSource('/api/sse');

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents(prev => [...prev, data]);
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      eventSource.close();
    };

    return () => eventSource.close();
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl mb-4">SSE Updates</h1>
      <div className="space-y-2">
        {events.map((event, i) => (
          <div key={i} className="border p-2 rounded">
            {JSON.stringify(event)}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Best Practices
- **Retries with Backoff**: Implement exponential backoff for webhooks
- **Idempotency**: Add idempotency keys to avoid duplicate processing
- **Signatures**: Sign webhooks for security
- **Dead Letter Queues**: Use DLQs for failed webhooks
- **Timeouts**: Set reasonable timeouts for streaming
- **Monitoring**: Monitor webhook delivery rates
- **Rate Limiting**: Respect third-party rate limits
- **Error Alerting**: Alert on DLQ messages
