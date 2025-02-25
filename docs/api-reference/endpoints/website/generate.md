# Generate Website Endpoint

Generate a new website based on provided specifications.

## Endpoint

```
POST /Aoede/generate/website
```

## Authentication

```
Authorization: Bearer YOUR_API_KEY
```

## Request Body

```json
{
    "description": "A modern business website with blog functionality",
    "style": "minimal",
    "pages": ["home", "about", "blog", "contact"],
    "features": {
        "contact_form": true,
        "newsletter": true,
        "blog": true
    },
    "branding": {
        "colors": {
            "primary": "#1A2B3C",
            "secondary": "#4C5D6E"
        },
        "fonts": {
            "heading": "Montserrat",
            "body": "Open Sans"
        }
    }
}
```

### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| description | string | Yes | Description of the website |
| style | string | No | Website style (minimal, modern, corporate) |
| pages | array | No | List of pages to generate |
| features | object | No | Additional features to include |
| branding | object | No | Branding configuration |

## Response

### Success Response (202 Accepted)

```json
{
    "project_id": "proj_abc123",
    "status": "queued",
    "estimated_time": "30 seconds",
    "status_url": "/Aoede/projects/proj_abc123/status"
}
```

### Error Response (400 Bad Request)

```json
{
    "error": true,
    "code": "INVALID_REQUEST",
    "message": "Invalid request parameters",
    "details": {
        "description": "Description is required"
    }
}
```

## Rate Limiting

- Demo API: 50 requests per hour
- Rate limit headers included in response

```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 49
X-RateLimit-Reset: 1635724800
```

## Example Usage

### Python

```python
import httpx
import json

async def generate_website():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.canopus.software/Aoede/generate/website",
            headers={
                "Authorization": "Bearer YOUR_API_KEY",
                "Content-Type": "application/json"
            },
            json={
                "description": "Modern business website",
                "style": "minimal",
                "pages": ["home", "about", "contact"]
            }
        )
        
        if response.status_code == 202:
            result = response.json()
            print(f"Project ID: {result['project_id']}")
            return result
        else:
            print(f"Error: {response.text}")
```

## Error Codes

| Code | Description |
|------|-------------|
| INVALID_REQUEST | Invalid request parameters |
| RATE_LIMIT_EXCEEDED | Rate limit exceeded |
| GENERATION_ERROR | Website generation failed |
| INVALID_STYLE | Invalid style specified |
| INVALID_FEATURES | Invalid features specified |

## Notes

- Maximum 5 pages per website in demo mode
- Generation typically takes 30-60 seconds
- Generated websites are retained for 24 hours
- Use WebSocket connection for real-time status updates

## See Also

- [Check Generation Status](./status.md)
- [Get Website Preview](./preview.md)
- [Website Templates](../../templates/README.md)
