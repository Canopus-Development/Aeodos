# API Reference Documentation

## Overview

The Aeodos API provides endpoints for website generation using AI. This reference documents all available endpoints, request/response formats, and authentication methods.

## Base URL
```
http://api.canopus.software/aeodos
```

## Authentication

All endpoints except `/demo/generate` require API key authentication:

```python
headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}
```

## Endpoints

### Website Generation
- [Generate Website](endpoints/website/generate.md)
- [Check Status](endpoints/website/status.md)
- [Get Preview](endpoints/website/preview.md)

### Demo
- [Demo Generation](endpoints/demo/generate.md)
- [Demo Status](endpoints/demo/status.md)

### Error Handling

All errors follow this format:
```json
{
    "error": true,
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {
        "additional": "error context"
    },
    "timestamp": "2024-01-20T12:00:00Z"
}
```

### Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| /demo/generate | 50 | 1 hour |
| /generate | 100 | 1 hour |
| /status | 1000 | 1 hour |

## Request Examples

### Generate Website
```bash
curl -X POST "http://api.canopus.software/aeodos/generate" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "description": "Modern business website",
       "style": "minimal",
       "pages": ["home", "about", "contact"]
     }'
```

### Check Status
```bash
curl "http://api.canopus.software/aeodos/status/GENERATION_ID" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

### Response Examples

#### Successful Generation
```json
{
    "id": "gen_abc123",
    "status": "completed",
    "url": "https://preview.aeodos.dev/abc123",
    "created_at": "2024-01-20T12:00:00Z"
}
```

#### Error Response
```json
{
    "error": true,
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
        "description": "Description is required"
    }
}
```
