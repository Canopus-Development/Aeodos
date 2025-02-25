# Getting Started with Aoede API

## Prerequisites
- Valid API key
- Basic understanding of REST APIs
- Supported programming language (Python, JavaScript, PHP, Go, or cURL)

## Installation

### Using npm
```bash
npm install @Aoede/client
```

### Using pip
```bash
pip install Aoede-client
```

### Using Composer
```bash
composer require Aoede/client
```

### Using Go modules
```bash
go get github.com/canopus-development/Aoede-client
```

## Authentication
All API requests require authentication using your API key. To obtain an API key:

1. Visit [Aoede Dashboard](https://Aoede.canopus.software/dashboard)
2. Register for an account
3. Generate an API key

Include your API key in all requests using the Authorization header:
```bash
Authorization: Bearer YOUR_API_KEY
```

## Basic Usage

### JavaScript Example
```javascript
const Aoede = require('@Aoede/client');

const Aoede = new Aoede('YOUR_API_KEY');

async function generateWebsite() {
    try {
        const website = await Aoede.generate({
            description: "A modern business website",
            style: "minimal",
            pages: ["home", "about", "contact"]
        });
        
        console.log('Website generated:', website);
    } catch (error) {
        console.error('Generation failed:', error);
    }
}
```

### Rate Limits
- Free tier: 100 requests/hour
- Pro tier: 1000 requests/hour
- Enterprise tier: Custom limits

## Next Steps
- Explore the [API Reference](../api-reference/README.md)
- Check out [Examples](../examples/README.md)
- Read our [Best Practices Guide](../guides/best-practices.md)
