# Skill: Docker Swarm Orchestration

## Purpose
To deploy, manage, and scale containerized applications using Docker Swarm for container orchestration.

## When to Use
- When you need container orchestration but want something simpler than Kubernetes
- For deploying and managing multi-container applications across multiple nodes
- When you need high availability and load balancing for your services
- For rolling updates and rollbacks of application deployments
- When working with a small to medium-sized cluster

## Procedure

### 1. Initialize Docker Swarm
Create a Docker Swarm cluster.

```bash
# On the manager node
docker swarm init --advertise-addr <MANAGER-IP>

# Output will give you a command to join worker nodes
docker swarm join --token <TOKEN> <MANAGER-IP>:2377
```

### 2. Create a Docker Stack
Deploy services using a docker-compose.yml file.

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    networks:
      - webnet

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - db-data:/var/lib/postgresql/data
    deploy:
      placement:
        constraints:
          - node.role == manager
    networks:
      - webnet

volumes:
  db-data:

networks:
  webnet:
    driver: overlay
```

### 3. Deploy the Stack
Deploy your application stack.

```bash
docker stack deploy -c docker-compose.yml myapp
```

### 4. Manage Services
Monitor and manage your services.

```bash
# List stacks
docker stack ls

# List services in a stack
docker stack services myapp

# List running containers
docker stack ps myapp

# Scale a service
docker service scale myapp_web=5

# Update a service
docker service update --image nginx:latest myapp_web

# View service logs
docker service logs myapp_web

# Remove the stack
docker stack rm myapp
```

### 5. Rolling Updates & Rollbacks
Perform rolling updates and rollbacks.

```bash
# Update the image with rolling update
docker service update \
  --image myapp:v2 \
  --update-parallelism 2 \
  --update-delay 10s \
  myapp_web

# Rollback if something goes wrong
docker service rollback myapp_web
```

## Best Practices
- **Manager Nodes**: Use 3 or 5 manager nodes for high availability
- **Constraints**: Use placement constraints to control where services run
- **Secrets**: Use Docker Secrets for sensitive information instead of environment variables
- **Healthchecks**: Add healthchecks to your services for better reliability
- **Resource Limits**: Set CPU and memory limits for each service
- **Monitoring**: Monitor your swarm with tools like Prometheus and Grafana
- **Backup**: Regularly back up the swarm state (especially manager nodes)
