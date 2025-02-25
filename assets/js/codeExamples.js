window.Aoede = window.Aoede || {};

if (!window.Aoede.CodeExamplesManager) {
    window.Aoede.CodeExamplesManager = class CodeExamplesManager {
        constructor() {
            this.currentLanguage = 'curl';
            this.codeExamples = {
                curl: {
                    authentication: `curl -X POST http://api.canopus.software/Aoede/keys/generate \
-H "Content-Type: application/json" \
-d '{
    "email": "your@email.com",
    "company_name": "Your Company"
}'`,
                    websiteGeneration: `curl -X POST http://api.canopus.software/Aoede/generate/website \
-H "Authorization: Bearer YOUR_API_KEY" \
-H "Content-Type: application/json" \
-d '{
    "description": "A modern business website",
    "style": "minimal",
    "pages": ["home", "about", "contact"]
}'`,
                    projectStatus: `curl http://api.canopus.software/Aoede/projects/PROJECT_ID/status \
-H "Authorization: Bearer YOUR_API_KEY"`
                },
                python: {
                    authentication: `import requests

response = requests.post(
    'http://api.canopus.software/Aoede/keys/generate',
    json={
        'email': 'your@email.com',
        'company_name': 'Your Company'
    }
)

api_key = response.json()['api_key']`,
                    websiteGeneration: `import requests

response = requests.post(
    'http://api.canopus.software/Aoede/generate/website',
    headers={'Authorization': 'Bearer YOUR_API_KEY'},
    json={
        'description': 'A modern business website',
        'style': 'minimal',
        'pages': ['home', 'about', 'contact']
    }
)

project = response.json()`,
                    projectStatus: `import requests

response = requests.get(
    'http://api.canopus.software/Aoede/projects/PROJECT_ID/status',
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)

status = response.json()`
                },
                javascript: {
                    authentication: `// Using fetch API
const response = await fetch('http://api.canopus.software/Aoede/keys/generate', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        email: 'your@email.com',
        company_name: 'Your Company'
    })
});

const { api_key } = await response.json();`,
                    websiteGeneration: `// Generate website
const response = await fetch('http://api.canopus.software/Aoede/generate/website', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        description: 'A modern business website',
        style: 'minimal',
        pages: ['home', 'about', 'contact']
    })
});

const project = await response.json();`,
                    projectStatus: `// Check project status
const response = await fetch(
    'http://api.canopus.software/Aoede/projects/PROJECT_ID/status',
    {
        headers: {
            'Authorization': 'Bearer YOUR_API_KEY'
        }
    }
);

const status = await response.json();`
                },
                php: {
                    authentication: `<?php
$ch = curl_init('http://api.canopus.software/Aoede/keys/generate');
$data = [
    'email' => 'your@email.com',
    'company_name' => 'Your Company'
];

curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
    CURLOPT_POSTFIELDS => json_encode($data)
]);

$response = curl_exec($ch);
$result = json_decode($response, true);
$api_key = $result['api_key'];
curl_close($ch);`,
                    websiteGeneration: `<?php
$ch = curl_init('http://api.canopus.software/Aoede/generate/website');
$data = [
    'description' => 'A modern business website',
    'style' => 'minimal',
    'pages' => ['home', 'about', 'contact']
];

curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => [
        'Authorization: Bearer YOUR_API_KEY',
        'Content-Type: application/json'
    ],
    CURLOPT_POSTFIELDS => json_encode($data)
]);

$response = curl_exec($ch);
$project = json_decode($response, true);
curl_close($ch);`,
                    projectStatus: `<?php
$ch = curl_init('http://api.canopus.software/Aoede/projects/PROJECT_ID/status');

curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => ['Authorization: Bearer YOUR_API_KEY']
]);

$response = curl_exec($ch);
$status = json_decode($response, true);
curl_close($ch);`
                },
                go: {
                    authentication: `package main

import (
    "bytes"
    "encoding/json"
    "net/http"
)

func main() {
    data := map[string]string{
        "email": "your@email.com",
        "company_name": "Your Company",
    }
    
    jsonData, _ := json.Marshal(data)
    
    req, _ := http.NewRequest("POST", 
        "http://api.canopus.software/Aoede/keys/generate",
        bytes.NewBuffer(jsonData))
        
    req.Header.Set("Content-Type", "application/json")
    
    client := &http.Client{}
    resp, _ := client.Do(req)
    
    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)
    apiKey := result["api_key"].(string)
}`,
                    websiteGeneration: `package main

import (
    "bytes"
    "encoding/json"
    "net/http"
)

func main() {
    data := map[string]interface{}{
        "description": "A modern business website",
        "style": "minimal",
        "pages": []string{"home", "about", "contact"},
    }
    
    jsonData, _ := json.Marshal(data)
    
    req, _ := http.NewRequest("POST",
        "http://api.canopus.software/Aoede/generate/website",
        bytes.NewBuffer(jsonData))
        
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("Authorization", "Bearer YOUR_API_KEY")
    
    client := &http.Client{}
    resp, _ := client.Do(req)
    
    var project map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&project)
}`,
                    projectStatus: `package main

import (
    "encoding/json"
    "net/http"
)

func main() {
    req, _ := http.NewRequest("GET",
        "http://api.canopus.software/Aoede/projects/PROJECT_ID/status",
        nil)
        
    req.Header.Set("Authorization", "Bearer YOUR_API_KEY")
    
    client := &http.Client{}
    resp, _ := client.Do(req)
    
    var status map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&status)
}`
                }
            };

            // Add loading states tracking
            this.isLoading = false;
            this.lastLanguage = 'curl';

            this.init();
        }

        init() {
            this.attachEventListeners();
            this.updateCodeExamples();
            this.updateLanguageIndicator();
        }

        attachEventListeners() {
            const languageSelect = document.getElementById('languageSelect');
            const tabButtons = document.querySelectorAll('.tab-btn');
            const copyButtons = document.querySelectorAll('.copy-btn');

            languageSelect?.addEventListener('change', async (e) => {
                try {
                    this.setLoading(true);
                    this.lastLanguage = this.currentLanguage;
                    this.currentLanguage = e.target.value;
                    
                    // Animate transition
                    await this.animateLanguageChange();
                    
                    this.updateCodeExamples();
                    this.updateLanguageIndicator();
                } catch (error) {
                    console.error('Language change failed:', error);
                    // Revert on error
                    this.currentLanguage = this.lastLanguage;
                    this.showError('Failed to change language');
                } finally {
                    this.setLoading(false);
                }
            });

            tabButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    this.handleTabClick(e);
                });
            });

            copyButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    this.handleCopy(e);
                });
            });
        }

        setLoading(loading) {
            this.isLoading = loading;
            const selector = document.querySelector('.language-selector');
            if (loading) {
                selector?.classList.add('loading');
            } else {
                selector?.classList.remove('loading');
            }
        }

        updateLanguageIndicator() {
            const selector = document.querySelector('.language-selector');
            if (selector) {
                selector.setAttribute('data-language', this.currentLanguage.toUpperCase());
            }
        }

        async animateLanguageChange() {
            const codeElements = document.querySelectorAll('.code-panel pre code');
            
            // Fade out
            await Promise.all(
                Array.from(codeElements).map(el => {
                    el.style.transition = 'opacity 0.3s ease';
                    el.style.opacity = '0';
                    return new Promise(resolve => setTimeout(resolve, 300));
                })
            );

            // Update content
            this.updateCodeExamples();

            // Fade in
            codeElements.forEach(el => {
                el.style.opacity = '1';
            });
        }

        showError(message) {
            const errorToast = document.createElement('div');
            errorToast.className = 'error-toast';
            errorToast.textContent = message;
            document.body.appendChild(errorToast);

            setTimeout(() => {
                errorToast.remove();
            }, 3000);
        }

        handleTabClick(e) {
            const tabButtons = document.querySelectorAll('.tab-btn');
            const codePanels = document.querySelectorAll('.code-panel');
            const targetTab = e.target.dataset.tab;

            tabButtons.forEach(btn => btn.classList.remove('active'));
            codePanels.forEach(panel => panel.classList.remove('active'));

            e.target.classList.add('active');
            document.getElementById(targetTab)?.classList.add('active');
        }

        async handleCopy(e) {
            const targetId = e.target.dataset.target;
            const codeElement = document.getElementById(targetId);
            
            try {
                await navigator.clipboard.writeText(codeElement.textContent);
                e.target.textContent = 'Copied!';
                setTimeout(() => {
                    e.target.textContent = 'Copy';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy code:', err);
            }
        }

        updateCodeExamples() {
            const examples = this.codeExamples[this.currentLanguage];
            if (!examples) return;

            try {
                document.getElementById('authCode').textContent = examples.authentication;
                document.getElementById('generateCode').textContent = examples.websiteGeneration;
                document.getElementById('statusCode').textContent = examples.projectStatus;

                // Safe Prism initialization
                if (typeof Prism !== 'undefined' && Prism.highlightAll) {
                    Prism.highlightAll();
                } else {
                    this.applyBasicFormatting();
                }
            } catch (error) {
                console.error('Error updating code examples:', error);
                this.handleUpdateError();
            }
        }

        applyBasicFormatting() {
            document.querySelectorAll('pre code').forEach(block => {
                block.style.display = 'block';
                block.style.padding = '1em';
                block.style.background = '#f8fafc';
                block.style.borderRadius = '8px';
                block.style.whiteSpace = 'pre';
            });
        }

        handleUpdateError() {
            const errorMessage = `<div class="code-preview-error">
                <p>Syntax highlighting temporarily unavailable</p>
            </div>`;
            
            ['authCode', 'generateCode', 'statusCode'].forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    element.parentElement.innerHTML = errorMessage;
                }
            });
        }
    }
}

// Initialize only if not already done
if (!window.codeExamples) {
    window.codeExamples = new window.Aoede.CodeExamplesManager();
}
