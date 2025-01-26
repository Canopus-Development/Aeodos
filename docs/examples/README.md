# Code Examples

## Basic Examples

### Website Generation

#### JavaScript (Node.js)
```javascript
const Aeodos = require('@aeodos/client');
const aeodos = new Aeodos(process.env.AEODOS_API_KEY);

async function generateBusinessWebsite() {
    try {
        const website = await aeodos.generate({
            description: "A professional business website with modern design",
            style: "corporate",
            pages: ["home", "about", "services", "contact"],
            features: ["contact-form", "newsletter", "blog"]
        });
        
        console.log(`Website generated: ${website.url}`);
        return website;
    } catch (error) {
        console.error('Generation failed:', error);
        throw error;
    }
}
```

#### Python
```python
from aeodos import Client
import os

aeodos = Client(os.getenv('AEODOS_API_KEY'))

async def generate_business_website():
    try:
        website = await aeodos.generate(
            description="A professional business website with modern design",
            style="corporate",
            pages=["home", "about", "services", "contact"],
            features=["contact-form", "newsletter", "blog"]
        )
        
        print(f"Website generated: {website.url}")
        return website
    except Exception as e:
        print(f"Generation failed: {str(e)}")
        raise
```

## Advanced Examples

### Custom Website Templates

```javascript
const template = {
    layout: "custom",
    components: {
        header: {
            type: "sticky",
            logo: "url-to-logo",
            navigation: ["home", "about", "services"]
        },
        hero: {
            type: "fullscreen",
            background: "video",
            content: {
                heading: "Welcome to Our Company",
                subheading: "Innovation Meets Excellence"
            }
        }
    },
    styling: {
        theme: "custom",
        colors: {
            primary: "#1a2b3c",
            secondary: "#4c5d6e",
            accent: "#7e8f9a"
        },
        typography: {
            headings: "Montserrat",
            body: "Open Sans"
        }
    }
};

const website = await aeodos.generate({
    description: "Custom business website",
    template: template,
    pages: ["home", "about", "services"]
});
```

### Real-time Status Updates

```javascript
const websiteId = "web_abc123";

// Using WebSocket connection
const statusSocket = aeodos.subscribeToStatus(websiteId);

statusSocket.on('progress', (status) => {
    console.log(`Generation progress: ${status.percentage}%`);
    console.log(`Current step: ${status.currentStep}`);
});

statusSocket.on('complete', (website) => {
    console.log('Website generation complete!');
    console.log(`Website URL: ${website.url}`);
});

statusSocket.on('error', (error) => {
    console.error('Generation failed:', error);
});
```

### Error Handling and Retries

```javascript
class AeodosClient {
    constructor(apiKey, options = {}) {
        this.client = new Aeodos(apiKey);
        this.maxRetries = options.maxRetries || 3;
        this.backoffFactor = options.backoffFactor || 1.5;
    }

    async generateWithRetry(config) {
        let retries = 0;
        
        while (retries < this.maxRetries) {
            try {
                return await this.client.generate(config);
            } catch (error) {
                if (!this.isRetryable(error) || retries === this.maxRetries - 1) {
                    throw error;
                }
                
                const delay = this.calculateBackoff(retries);
                await new Promise(resolve => setTimeout(resolve, delay));
                retries++;
            }
        }
    }

    isRetryable(error) {
        return error.code === 'RATE_LIMIT_EXCEEDED' ||
               error.code === 'SERVER_ERROR' ||
               error.code === 'NETWORK_ERROR';
    }

    calculateBackoff(retry) {
        return Math.pow(this.backoffFactor, retry) * 1000;
    }
}
