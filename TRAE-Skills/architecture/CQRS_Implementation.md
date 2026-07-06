# Skill: CQRS (Command Query Responsibility Segregation) Implementation

## Purpose
To separate read and write operations using CQRS pattern for scalability, performance, and flexibility.

## When to Use
- When you have high read/write ratio discrepancies
- For complex business domains
- When you need different data models for reading and writing
- For event-driven architectures
- When scaling read-heavy applications

## Procedure

### 1. Define Commands and Queries
Separate command and query models.

```typescript
// Command Models
interface CreateProductCommand {
  type: 'CREATE_PRODUCT';
  name: string;
  description: string;
  price: number;
  category: string;
}

interface UpdateProductCommand {
  type: 'UPDATE_PRODUCT';
  id: string;
  name?: string;
  description?: string;
  price?: number;
  category?: string;
}

interface DeleteProductCommand {
  type: 'DELETE_PRODUCT';
  id: string;
}

type ProductCommand = CreateProductCommand | UpdateProductCommand | DeleteProductCommand;

// Query Models
interface GetProductQuery {
  id: string;
}

interface ListProductsQuery {
  category?: string;
  minPrice?: number;
  maxPrice?: number;
  page?: number;
  limit?: number;
}

interface ProductDTO {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  createdAt: string;
  updatedAt: string;
}
```

### 2. Command Handlers
Implement command handlers for write operations.

```typescript
import { v4 as uuidv4 } from 'uuid';

interface ProductEvent {
  id: string;
  type: string;
  aggregateId: string;
  data: any;
  timestamp: Date;
}

class ProductCommandHandler {
  private eventStore: ProductEvent[] = [];
  
  async handle(command: ProductCommand): Promise<string> {
    switch (command.type) {
      case 'CREATE_PRODUCT':
        return await this.createProduct(command);
      case 'UPDATE_PRODUCT':
        return await this.updateProduct(command);
      case 'DELETE_PRODUCT':
        return await this.deleteProduct(command);
      default:
        throw new Error('Unknown command type');
    }
  }
  
  private async createProduct(command: CreateProductCommand): Promise<string> {
    const productId = uuidv4();
    
    const event: ProductEvent = {
      id: uuidv4(),
      type: 'PRODUCT_CREATED',
      aggregateId: productId,
      data: {
        name: command.name,
        description: command.description,
        price: command.price,
        category: command.category
      },
      timestamp: new Date()
    };
    
    this.eventStore.push(event);
    await this.publishEvent(event);
    
    return productId;
  }
  
  private async updateProduct(command: UpdateProductCommand): Promise<string> {
    const event: ProductEvent = {
      id: uuidv4(),
      type: 'PRODUCT_UPDATED',
      aggregateId: command.id,
      data: {
        name: command.name,
        description: command.description,
        price: command.price,
        category: command.category
      },
      timestamp: new Date()
    };
    
    this.eventStore.push(event);
    await this.publishEvent(event);
    
    return command.id;
  }
  
  private async deleteProduct(command: DeleteProductCommand): Promise<string> {
    const event: ProductEvent = {
      id: uuidv4(),
      type: 'PRODUCT_DELETED',
      aggregateId: command.id,
      data: {},
      timestamp: new Date()
    };
    
    this.eventStore.push(event);
    await this.publishEvent(event);
    
    return command.id;
  }
  
  private async publishEvent(event: ProductEvent) {
    // Publish to event bus (Kafka, Redis, etc.)
    console.log('Publishing event:', event);
  }
}
```

### 3. Query Handlers
Implement query handlers for read operations.

```typescript
class ProductQueryHandler {
  private productReadModel: Map<string, ProductDTO> = new Map();
  
  async handleGetProduct(query: GetProductQuery): Promise<ProductDTO | null> {
    return this.productReadModel.get(query.id) || null;
  }
  
  async handleListProducts(query: ListProductsQuery): Promise<{ products: ProductDTO[], total: number }> {
    let products = Array.from(this.productReadModel.values());
    
    if (query.category) {
      products = products.filter(p => p.category === query.category);
    }
    
    if (query.minPrice !== undefined) {
      products = products.filter(p => p.price >= query.minPrice);
    }
    
    if (query.maxPrice !== undefined) {
      products = products.filter(p => p.price <= query.maxPrice);
    }
    
    const total = products.length;
    const page = query.page || 1;
    const limit = query.limit || 10;
    const start = (page - 1) * limit;
    const end = start + limit;
    
    return {
      products: products.slice(start, end),
      total
    };
  }
  
  // Update read model from events
  async applyEvent(event: ProductEvent) {
    switch (event.type) {
      case 'PRODUCT_CREATED':
        this.productReadModel.set(event.aggregateId, {
          id: event.aggregateId,
          name: event.data.name,
          description: event.data.description,
          price: event.data.price,
          category: event.data.category,
          createdAt: event.timestamp.toISOString(),
          updatedAt: event.timestamp.toISOString()
        });
        break;
      case 'PRODUCT_UPDATED':
        const product = this.productReadModel.get(event.aggregateId);
        if (product) {
          this.productReadModel.set(event.aggregateId, {
            ...product,
            ...event.data,
            updatedAt: event.timestamp.toISOString()
          });
        }
        break;
      case 'PRODUCT_DELETED':
        this.productReadModel.delete(event.aggregateId);
        break;
    }
  }
}
```

### 4. API Controllers
Create controllers for commands and queries.

```typescript
import express from 'express';

const app = express();
app.use(express.json());

const commandHandler = new ProductCommandHandler();
const queryHandler = new ProductQueryHandler();

// Command endpoints
app.post('/products', async (req, res) => {
  try {
    const command: CreateProductCommand = {
      type: 'CREATE_PRODUCT',
      name: req.body.name,
      description: req.body.description,
      price: req.body.price,
      category: req.body.category
    };
    
    const productId = await commandHandler.handle(command);
    res.status(201).json({ id: productId });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.put('/products/:id', async (req, res) => {
  try {
    const command: UpdateProductCommand = {
      type: 'UPDATE_PRODUCT',
      id: req.params.id,
      name: req.body.name,
      description: req.body.description,
      price: req.body.price,
      category: req.body.category
    };
    
    await commandHandler.handle(command);
    res.status(204).send();
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.delete('/products/:id', async (req, res) => {
  try {
    const command: DeleteProductCommand = {
      type: 'DELETE_PRODUCT',
      id: req.params.id
    };
    
    await commandHandler.handle(command);
    res.status(204).send();
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Query endpoints
app.get('/products/:id', async (req, res) => {
  try {
    const query: GetProductQuery = { id: req.params.id };
    const product = await queryHandler.handleGetProduct(query);
    
    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }
    
    res.json(product);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.get('/products', async (req, res) => {
  try {
    const query: ListProductsQuery = {
      category: req.query.category as string,
      minPrice: req.query.minPrice ? Number(req.query.minPrice) : undefined,
      maxPrice: req.query.maxPrice ? Number(req.query.maxPrice) : undefined,
      page: req.query.page ? Number(req.query.page) : undefined,
      limit: req.query.limit ? Number(req.query.limit) : undefined
    };
    
    const result = await queryHandler.handleListProducts(query);
    res.json(result);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('CQRS Server running on port 3000');
});
```

## Best Practices
- **Separate Models**: Keep write and read models separate
- **Eventual Consistency**: Embrace eventual consistency for read models
- **Event Sourcing**: Combine with Event Sourcing for full history
- **Validation**: Validate commands before processing
- **Idempotency**: Make commands idempotent
- **Performance**: Optimize read models for queries (denormalize, use indexes)
- **Scalability**: Scale read and write sides independently
- **Monitoring**: Monitor sync between write and read models
