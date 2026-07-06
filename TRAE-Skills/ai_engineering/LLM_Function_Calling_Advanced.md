# Skill: Advanced LLM Function Calling

## Purpose
To implement advanced function calling patterns with Large Language Models, enabling them to interact with external APIs, databases, and tools in a structured, safe way.

## When to Use
- When building AI agents that need to take real-world actions
- For integrating LLMs with existing APIs and services
- When you need structured, deterministic outputs from LLMs
- For building copilots and assistant applications
- When implementing multi-step reasoning and tool use

## Procedure

### 1. Function Definition Schema
Define functions with clear descriptions and schemas.

```javascript
import OpenAI from 'openai';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const functions = [
  {
    name: 'get_weather',
    description: 'Get the current weather in a given location',
    parameters: {
      type: 'object',
      properties: {
        location: {
          type: 'string',
          description: 'The city and state, e.g., San Francisco, CA',
        },
        unit: {
          type: 'string',
          enum: ['celsius', 'fahrenheit'],
          description: 'The temperature unit to use',
        },
      },
      required: ['location'],
    },
  },
  {
    name: 'search_products',
    description: 'Search for products in the catalog',
    parameters: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'The search query',
        },
        category: {
          type: 'string',
          enum: ['electronics', 'clothing', 'books'],
          description: 'Product category',
        },
        max_results: {
          type: 'integer',
          description: 'Maximum number of results to return',
        },
      },
      required: ['query'],
    },
  },
];
```

### 2. Function Calling Loop
Implement a loop to handle multiple function calls.

```javascript
async function chatWithFunctions(messages) {
  let response = await openai.chat.completions.create({
    model: 'gpt-4',
    messages,
    functions,
    function_call: 'auto',
  });

  let message = response.choices[0].message;

  while (message.function_call) {
    const functionName = message.function_call.name;
    const functionArgs = JSON.parse(message.function_call.arguments);

    // Execute the function
    let functionResponse;
    switch (functionName) {
      case 'get_weather':
        functionResponse = await getWeather(functionArgs);
        break;
      case 'search_products':
        functionResponse = await searchProducts(functionArgs);
        break;
      default:
        functionResponse = { error: `Unknown function: ${functionName}` };
    }

    // Add the function response to messages
    messages.push(message);
    messages.push({
      role: 'function',
      name: functionName,
      content: JSON.stringify(functionResponse),
    });

    // Get next response from LLM
    response = await openai.chat.completions.create({
      model: 'gpt-4',
      messages,
      functions,
      function_call: 'auto',
    });

    message = response.choices[0].message;
  }

  return message.content;
}

// Usage
const messages = [
  { role: 'user', content: 'What is the weather in New York and show me 3 electronics products?' }
];

const result = await chatWithFunctions(messages);
console.log(result);
```

### 3. Parallel Function Calling
Execute multiple functions in parallel.

```javascript
async function chatWithParallelFunctions(messages) {
  let response = await openai.chat.completions.create({
    model: 'gpt-4',
    messages,
    functions,
    function_call: 'auto',
  });

  let message = response.choices[0].message;

  while (message.function_call || message.tool_calls) {
    const calls = message.tool_calls || [message.function_call];
    
    // Execute all functions in parallel
    const functionResponses = await Promise.all(
      calls.map(async (call) => {
        const funcCall = call.type === 'function' ? call.function : call;
        const name = funcCall.name;
        const args = JSON.parse(funcCall.arguments);
        
        let result;
        switch (name) {
          case 'get_weather':
            result = await getWeather(args);
            break;
          case 'search_products':
            result = await searchProducts(args);
            break;
          default:
            result = { error: `Unknown function: ${name}` };
        }
        
        return {
          id: call.id,
          role: 'tool',
          name: name,
          content: JSON.stringify(result),
        };
      })
    );

    messages.push(message);
    messages.push(...functionResponses);

    response = await openai.chat.completions.create({
      model: 'gpt-4',
      messages,
      functions,
      function_call: 'auto',
    });

    message = response.choices[0].message;
  }

  return message.content;
}
```

### 4. Safety & Validation
Validate function inputs before execution.

```javascript
import { z } from 'zod';

const GetWeatherSchema = z.object({
  location: z.string().min(2),
  unit: z.enum(['celsius', 'fahrenheit']).optional().default('celsius'),
});

async function getWeatherSafe(args) {
  try {
    const validatedArgs = GetWeatherSchema.parse(args);
    return await getWeather(validatedArgs);
  } catch (error) {
    return { error: 'Invalid arguments', details: error.message };
  }
}

// Add authentication and authorization
async function executeFunction(name, args, userId) {
  // Check if user has permission to use this function
  if (!hasPermission(userId, name)) {
    return { error: 'Permission denied' };
  }
  
  // Validate arguments
  // Execute function
  // Log the function call for auditing
  logFunctionCall(userId, name, args);
}
```

## Best Practices
- **Clear Descriptions**: Write clear, detailed descriptions for functions and parameters
- **Input Validation**: Always validate function inputs before execution
- **Error Handling**: Gracefully handle errors and communicate them back to the LLM
- **Safety**: Implement authentication, authorization, and rate limiting
- **Idempotency**: Make functions idempotent when possible
- **Logging**: Log all function calls for debugging and auditing
- **Context Limit**: Be mindful of context limits and manage conversation history
