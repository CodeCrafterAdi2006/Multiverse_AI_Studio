# Skill: Real-time Data Processing (Kafka)

## Purpose
To set up, configure, and use Apache Kafka for building real-time data pipelines, event streaming applications, and microservices communication.

## When to Use
- When building real-time analytics dashboards
- For event-driven microservices architectures
- When processing high-throughput data streams (logs, metrics, user events)
- For implementing CDC (Change Data Capture) from databases
- When building real-time ETL pipelines

## Procedure

### 1. Kafka Producer Setup (Node.js)
Create a producer to send messages to Kafka topics.

```javascript
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'my-app',
  brokers: ['localhost:9092']
});

const producer = kafka.producer();

async function sendMessage(topic, messages) {
  await producer.connect();
  await producer.send({
    topic,
    messages: messages.map(msg => ({ value: JSON.stringify(msg) }))
  });
  await producer.disconnect();
}

// Usage
sendMessage('user-events', [
  { type: 'signup', userId: '123', email: 'user@example.com' },
  { type: 'login', userId: '123' }
]);
```

### 2. Kafka Consumer Setup (Node.js)
Create a consumer to process messages from topics.

```javascript
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'analytics-consumer',
  brokers: ['localhost:9092']
});

const consumer = kafka.consumer({ groupId: 'analytics-group' });

async function consumeMessages() {
  await consumer.connect();
  await consumer.subscribe({ topic: 'user-events', fromBeginning: true });

  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      const event = JSON.parse(message.value.toString());
      console.log('Processing event:', event);
      // Process the event (e.g., update database, trigger analytics)
    },
  });
}

consumeMessages();
```

### 3. Topic Configuration
Configure topics with appropriate replication and partitions.

```javascript
const admin = kafka.admin();

async function createTopic(topicName, numPartitions = 3, replicationFactor = 2) {
  await admin.connect();
  await admin.createTopics({
    topics: [{
      topic: topicName,
      numPartitions,
      replicationFactor
    }]
  });
  await admin.disconnect();
}
```

### 4. Error Handling & Retries
Implement robust error handling and retry logic.

```javascript
const consumer = kafka.consumer({ 
  groupId: 'analytics-group',
  retry: {
    retries: 5,
    initialRetryTime: 100,
    maxRetryTime: 30000
  }
});

async function processWithRetry(event) {
  try {
    // Process the event
  } catch (error) {
    console.error('Error processing event:', error);
    // Send to dead-letter queue for later processing
    await sendMessage('dlq-user-events', [{ ...event, error: error.message }]);
  }
}
```

## Best Practices
- **Partitioning Strategy**: Choose a good partition key to ensure even distribution of messages
- **Consumer Groups**: Use separate consumer groups for different processing needs
- **Idempotency**: Make consumers idempotent to handle duplicate messages
- **Monitoring**: Monitor lag, throughput, and error rates with tools like Prometheus
- **Dead-Letter Queues**: Implement DLQs for messages that fail processing repeatedly
- **Compaction**: Use log compaction for topics that need to retain the latest state for each key
