
# Aoede Installation Guide

## Overview
Aoede provides a robust platform for AI-driven website generation. This guide walks you through the initial installation and setup.

## Prerequisites
- Python 3.9+
- PostgreSQL 13+ (or compatible)
- Redis 6+
- Git

## Steps

1. Clone the Repository  
   ```bash
   git clone https://github.com/canopus-development/Aoede.git
   cd Aoede
   ```

2. Create and Activate Virtual Environment  
   ```bash
   python -m venv venv
   source venv/bin/activate
   # or on Windows:
   .\venv\Scripts\activate
   ```

3. Install Dependencies  
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Configure Environment  
   ```bash
   cp .env.example .env
   # Modify .env with your settings
   ```

5. Database Setup  
   ```bash
   alembic upgrade head
   # or
   python scripts/init_db.py
   ```

6. Verify Installation  
   ```bash
   pytest
   uvicorn app.main:app --reload
   ```

## Troubleshooting
- Make sure PostgreSQL and Redis are running.
- Check that your .env file has correct credentials.
- For permission issues, run terminal with elevated privileges.

## Next Steps
- [Configuration Guide](../configuration/README.md)
- [Deployment Guide](../deployment/README.md)
- [Development Guide](../development/README.md)