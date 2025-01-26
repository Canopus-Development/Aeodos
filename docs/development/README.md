# Development Guide

## Environment Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Git

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/canopus-development/aeodos.git
cd aeodos
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Setup environment variables:
```bash
cp .env.example .env
# Edit .env with your configurations
```

5. Initialize database:
```bash
alembic upgrade head
```

6. Run development server:
```bash
uvicorn app.main:app --reload --port 7297
```

## Project Structure

```
aeodos/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Core functionality
│   ├── models/        # Database models
│   ├── services/      # Business logic
│   └── utils/         # Utilities
├── tests/             # Test suite
├── alembic/           # Database migrations
└── docs/             # Documentation
```

## Code Style

We follow strict Python coding standards:

### Formatting
- Black for code formatting
- isort for import sorting
- Flake8 for linting

```bash
# Format code
black .

# Sort imports
isort .

# Run linter
flake8
```

### Type Hints
All new code must include type hints:

```python
from typing import List, Optional

def generate_pages(
    description: str,
    pages: List[str],
    style: Optional[str] = None
) -> dict:
    ...
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Generate coverage report
pytest --cov=app --cov-report=html tests/
```

### Writing Tests

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_endpoint():
    response = client.post(
        "/generate",
        json={
            "description": "Test website",
            "pages": ["home"]
        }
    )
    assert response.status_code == 200
    assert "id" in response.json()
```

## Database Migrations

### Create Migration
```bash
alembic revision --autogenerate -m "description"
```

### Apply Migration
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1
```

## Error Handling

Use the standard error format:

```python
from app.utils.errors import APIError

def process_request(data: dict) -> dict:
    if not data.get("description"):
        raise APIError(
            code="VALIDATION_ERROR",
            message="Description is required",
            status_code=400
        )
```

## Logging

Use the logging module:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Processing request", extra={
    "request_id": request_id,
    "user_id": user_id
})
```

## Security

### API Key Validation
```python
from app.core.security import validate_api_key

async def validate_request(api_key: str) -> bool:
    return await validate_api_key(api_key)
```

### Rate Limiting
```python
from app.core.rate_limit import rate_limit

@rate_limit(max_requests=100, window_seconds=3600)
async def protected_endpoint():
    ...
```

## Performance

### Caching
```python
from app.core.cache import cache

@cache(ttl=3600)
async def get_cached_data(key: str) -> dict:
    ...
```

### Database Optimization
- Use database indexes
- Implement connection pooling
- Use async queries when possible

## Deployment

See [Deployment Guide](../deployment/README.md) for:
- Docker deployment
- Kubernetes setup
- Monitoring
- Scaling strategies

## Contributing

1. Create feature branch:
```bash
git checkout -b feature/your-feature
```

2. Make changes and test:
```bash
pytest
black .
flake8
```

3. Submit pull request

See [Contributing Guidelines](../../CONTRIBUTING.md) for more details.
