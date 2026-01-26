# Docker Deployment Guide

This directory contains Docker configuration for deploying the Agent Control Plane.

## Quick Start

### Production Deployment

```bash
# Build and start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Development Environment

```bash
# Start development container
docker-compose --profile dev up -d acp-dev

# Enter the container
docker exec -it acp-dev bash

# Run tests inside container
python -m pytest tests/

# Run examples
python examples/basic_usage.py
```

### Distributed Setup (with Redis)

```bash
# Start with Redis for distributed coordination
docker-compose --profile distributed up -d

# This includes Redis for message queues and caching
```

## Configuration

### Environment Variables

- `ACP_DATA_DIR`: Directory for persistent data (default: `/app/data`)
- `ACP_LOG_LEVEL`: Logging level (default: `INFO`, options: `DEBUG`, `INFO`, `WARNING`, `ERROR`)

### Volumes

- `acp-data`: Persistent storage for audit logs, databases, and configurations
- `acp-dev-data`: Separate volume for development work
- `redis-data`: Redis persistence (when using distributed profile)

## Building Images

### Build Production Image

```bash
docker build --target production -t agent-control-plane:latest .
```

### Build Development Image

```bash
docker build --target development -t agent-control-plane:dev .
```

## Health Checks

The production container includes health checks:

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' acp-main
```

## Networking

All services are connected via the `acp-network` bridge network, allowing inter-container communication.

## Security Considerations

1. **Non-root User**: Containers run as `acp` user (UID 1000)
2. **Read-only Mounts**: Examples are mounted read-only
3. **Network Isolation**: Services communicate only via defined network
4. **Secrets Management**: Use Docker secrets for sensitive data in production

### Using Docker Secrets

```bash
# Create a secret
echo "your-secret-value" | docker secret create acp_secret -

# Reference in docker-compose.yml
services:
  agent-control-plane:
    secrets:
      - acp_secret
```

## Production Deployment Checklist

- [ ] Review and set appropriate environment variables
- [ ] Configure volume persistence for audit logs
- [ ] Set up monitoring and alerting
- [ ] Configure resource limits (CPU, memory)
- [ ] Enable TLS/SSL for API endpoints
- [ ] Set up backup strategy for data volumes
- [ ] Review security hardening options
- [ ] Configure log aggregation

## Resource Limits

Add resource limits in production:

```yaml
services:
  agent-control-plane:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Kubernetes Deployment

For Kubernetes deployment, see `k8s/` directory (coming soon).

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs agent-control-plane

# Check health
docker inspect acp-main
```

### Permission issues

```bash
# Fix volume permissions
docker-compose run --rm agent-control-plane chown -R acp:acp /app/data
```

### Network issues

```bash
# Inspect network
docker network inspect acp-network

# Test connectivity
docker-compose exec agent-control-plane ping redis
```

## Updates and Maintenance

```bash
# Update to latest version
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Backup data before updates
docker run --rm -v acp-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/acp-data-backup.tar.gz /data
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/imran-siddique/agent-control-plane/issues
- Documentation: https://github.com/imran-siddique/agent-control-plane/tree/main/docs
