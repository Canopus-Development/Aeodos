window.Aeodos = window.Aeodos || {};

if (!window.Aeodos.CodePreview) {
    window.Aeodos.CodePreview = class CodePreview {
        constructor() {
            this.preview = document.getElementById('codePreview');
            this.codeSnippet = `// Example website generation
const website = await aeodos.generate({
    description: "Modern business website",
    style: "minimal",
    pages: ["home", "about", "contact"]
});

// Result
{
    "status": "success",
    "projectId": "proj_abc123",
    "url": "https://aeodos.canopus.software/preview/abc123"
}`;
            
            this.init();
        }

        init() {
            if (!this.preview) return;

            try {
                this.preview.innerHTML = `<pre><code class="language-javascript">${this.escapeHtml(this.codeSnippet)}</code></pre>`;
                
                // Check if Prism is available
                if (typeof Prism !== 'undefined' && Prism.highlightAll) {
                    Prism.highlightAll();
                } else {
                    console.warn('Prism syntax highlighting not available, falling back to plain text');
                    this.applyBasicFormatting();
                }
            } catch (error) {
                console.error('Error initializing code preview:', error);
                this.handleInitError();
            }
        }

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        applyBasicFormatting() {
            const codeElement = this.preview.querySelector('code');
            if (codeElement) {
                codeElement.style.display = 'block';
                codeElement.style.padding = '1em';
                codeElement.style.background = '#f8fafc';
                codeElement.style.borderRadius = '8px';
                codeElement.style.whiteSpace = 'pre';
            }
        }

        handleInitError() {
            if (this.preview) {
                this.preview.innerHTML = `
                    <div class="code-preview-error">
                        <p>Code preview temporarily unavailable</p>
                        <pre><code>${this.escapeHtml(this.codeSnippet)}</code></pre>
                    </div>`;
            }
        }
    }
}

// Initialize only when DOM is ready and not already initialized
if (!window.codePreview) {
    document.addEventListener('DOMContentLoaded', () => {
        window.codePreview = new window.Aeodos.CodePreview();
    });
}
