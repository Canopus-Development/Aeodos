# Aeodos Configuration Guide

## Overview
Configuration is managed via environment variables in Aeodos. This guide helps you customize the application for development, staging, or production.

## Environment Variables
Use the `.env` file to set critical configuration values.

Example:
```ini
# Server
HOST=0.0.0.0
PORT=7297
DEBUG=True
WORKERS=4

# Database
DATABASE_URL=postgresql://user:pass@localhost/aeodos

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key
API_KEY_EXPIRY_DAYS=30
CORS_ORIGINS=["*"]
```

## Database Configuration
- PostgreSQL by default
- Other SQLAlchemy-supported databases possible
- Update `DATABASE_URL` accordingly.

## Redis & Caching
- Redis is used for session management, rate limiting, and caching.
- Update `REDIS_URL` for your environment.

## Debug & Logging
- `DEBUG` enables debug mode in FastAPI.
- Use `LOG_LEVEL`, `LOG_FORMAT`, or a custom logging config if needed.

## Overriding Environments
- You can override variables via system environment, Docker secrets, or orchestration tools (K8s config maps).

## Best Practices
- Use strong secrets in production.
- Restrict CORS to known domains.
- Enable TLS termination at your load balancer or proxy.

## References
- [Installation Guide](../installation/README.md)
- [Deployment Guide](../deployment/README.md)
- [Security Documentation](../security/README.md)
