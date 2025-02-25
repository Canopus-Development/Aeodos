<div align="center">
  <img src="assets/images/logo.svg" alt="Aoede" width="200" />
  <h1>Aoede</h1>
  <p>AI-Powered Website Generation Engine | FastAPI-based Open Source Project</p>

  [![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg?style=flat-square)](https://www.python.org/downloads/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.1.0-teal.svg?style=flat-square)](https://fastapi.tiangolo.com)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
  [![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)

</div>

## 🌟 Overview

Aoede is a Python-based open-source project that leverages AI for automated website generation. Built with FastAPI and modern Python practices, it provides a robust foundation for AI-driven web development.

## ⚡️ Key Features

- **FastAPI Backend**: High-performance asynchronous API
- **AI Integration**: Advanced website generation algorithms
- **SQLAlchemy ORM**: Robust database management
- **Redis Cache**: High-speed data caching
- **Async Support**: Built for scale with async/await
- **OpenAPI Docs**: Auto-generated API documentation

## 🛠 Requirements

- Python 3.9+
- Redis
- PostgreSQL
- Python packages (see `requirements.txt`)

## 🚀 Quick Start

### Setup Environment

```bash
# Clone the repository
git clone https://github.com/canopus-development/Aoede.git
cd Aoede

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configurations
```

### Database Setup

```bash
# Initialize database
python scripts/init_db.py

# Run migrations
alembic upgrade head
```

### Run Development Server

```bash
uvicorn main:app --reload --port 7297
```

## 📚 Project Structure

```
Aoede/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core functionality
│   ├── models/       # Database models
│   ├── services/     # Business logic
│   └── utils/        # Utilities
├── tests/            # Test suite
├── alembic/          # Database migrations
├── docs/             # Documentation
└── scripts/          # Utility scripts
```

## 🔧 Configuration

Example .env configuration:

```ini
# Server Settings
HOST=0.0.0.0
PORT=7297
DEBUG=True
WORKERS=4

# Database
DATABASE_URL=postgresql://user:pass@localhost/Aoede

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key
API_KEY_EXPIRY_DAYS=30
CORS_ORIGINS=["http://localhost:3000"]
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Generate coverage report
pytest --cov=app --cov-report=html tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```
3. Follow code style guidelines:
```bash
# Format code
black .

# Run linter
flake8

# Type checking
mypy .
```
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📖 Documentation

- [API Reference](docs/api-reference/README.md)
- [Architecture Overview](docs/architecture/README.md)
- [Development Guide](docs/development/README.md)
- [Deployment Guide](docs/deployment/README.md)

## 🔬 Demo API

Try our demo API with limited functionality:

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "https://api.canopus.software/Aoede/demo/generate",
        json={
            "description": "Modern business website",
            "style": "minimal",
            "pages": ["home", "about", "contact"]
        }
    )
    print(response.json())
```

Demo Limitations:
- 50 requests/hour
- Maximum 3 pages per website
- Basic templates only
- 24-hour result retention

## 📈 Production Deployment

For production deployment, see our [deployment guide](docs/deployment/README.md) for:
- Docker deployment
- Kubernetes configurations
- Scaling strategies
- Monitoring setup
- Security best practices

## 🛡 Security

- TLS 1.3 required for all connections
- API key authentication
- Rate limiting
- Input validation
- SQL injection protection
- XSS prevention

Report security issues to security@canopus.software

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

## 🤖 AI Models Support

Currently supported AI models:
- OpenAI GPT-3.5/4
- Local LLaMA models
- Custom fine-tuned models

## 🏗 Roadmap

- [ ] Custom model training pipeline
- [ ] GraphQL API support
- [ ] WebSocket real-time updates
- [ ] Plugin system
- [ ] CI/CD templates

---

<p align="center">Built with ❤️ by <a href="https://canopus.software">Canopus Development</a></p>

<p align="center">
<a href="https://github.com/canopus-development/Aoede/issues">Report Bug</a> · 
<a href="https://discord.gg/JUhv27kzcJ">Join Discord</a> · 
<a href="https://Aoede.canopus.software/docs">Documentation</a>
</p>
