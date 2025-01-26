window.Aeodos = window.Aeodos || {};

if (!window.Aeodos.PlaygroundManager) {
    window.Aeodos.PlaygroundManager = class PlaygroundManager {
        constructor() {
            // Initialize only if we're on the right page
            const playgroundElements = {
                description: document.getElementById('websiteDescription'),
                style: document.getElementById('websiteStyle'),
                previewMode: document.getElementById('previewMode'),
                previewCode: document.getElementById('previewCode'),
                websitePreview: document.getElementById('websitePreview'),
                previewFrame: document.getElementById('previewFrame'),
                runButton: document.getElementById('runCode'),
                resetButton: document.getElementById('resetCode')
            };

            // Only proceed if we find the required elements
            if (playgroundElements.description || playgroundElements.style) {
                this.elements = playgroundElements;
                this.apiEndpoint = 'http://api.canopus.software/aeodos';
                this.demoApiKey = 'demo_key_123';
                this.init();
            }
        }

        init() {
            this.attachEventListeners();
            this.setInitialState();
        }

        attachEventListeners() {
            this.elements.runButton?.addEventListener('click', () => this.generateWebsite());
            this.elements.resetButton?.addEventListener('click', () => this.resetPlayground());
            this.elements.previewMode?.addEventListener('change', () => this.togglePreviewMode());
            
            // Handle checkbox changes
            document.querySelectorAll('.checkbox input[type="checkbox"]').forEach(checkbox => {
                checkbox.addEventListener('change', () => this.updatePages());
            });
        }

        setInitialState() {
            this.elements.description.value = 'A modern business website with a clean design';
            this.updatePreviewCode({
                message: 'Configure your website and click "Generate Website" to see the result'
            });
        }

        async generateWebsite() {
            try {
                this.elements.runButton.disabled = true;
                this.elements.runButton.textContent = 'Generating...';
                this.setPreviewLoading(true);

                const config = {
                    description: this.elements.description.value,
                    style: this.elements.style.value,
                    pages: this.getSelectedPages()
                };

                const response = await fetch(`${this.apiEndpoint}/generate/website`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.demoApiKey}`
                    },
                    body: JSON.stringify(config)
                });

                const data = await response.json();
                
                if (response.ok) {
                    this.updatePreviewCode(data);
                    if (data.previewUrl) {
                        this.elements.previewFrame.src = data.previewUrl;
                    }
                } else {
                    throw new Error(data.detail || 'Generation failed');
                }
            } catch (error) {
                this.showError(error.message);
            } finally {
                this.elements.runButton.disabled = false;
                this.elements.runButton.textContent = 'Generate Website';
                this.setPreviewLoading(false);
            }
        }

        getSelectedPages() {
            const pages = ['home'];
            document.querySelectorAll('.checkbox input[type="checkbox"]:checked').forEach(checkbox => {
                if (checkbox.value !== 'home') {
                    pages.push(checkbox.value);
                }
            });
            return pages;
        }

        updatePreviewCode(data) {
            this.elements.previewCode.textContent = JSON.stringify(data, null, 2);
            Prism.highlightElement(this.elements.previewCode);
        }

        togglePreviewMode() {
            const isResponse = this.elements.previewMode.value === 'response';
            const previewControls = this.elements.previewMode.closest('.preview-controls');
            
            this.elements.previewCode.parentElement.style.display = isResponse ? 'block' : 'none';
            this.elements.websitePreview.style.display = isResponse ? 'none' : 'block';
            
            // Update preview mode indicator
            previewControls.setAttribute('data-mode', isResponse ? 'response' : 'preview');
        }

        setPreviewLoading(loading) {
            const previewControls = this.elements.previewMode.closest('.preview-controls');
            if (loading) {
                previewControls.classList.add('loading');
                this.elements.previewMode.disabled = true;
            } else {
                previewControls.classList.remove('loading');
                this.elements.previewMode.disabled = false;
            }
        }

        resetPlayground() {
            this.elements.description.value = '';
            this.elements.style.value = 'modern';
            document.querySelectorAll('.checkbox input[type="checkbox"]').forEach(checkbox => {
                checkbox.checked = checkbox.value === 'home';
            });
            this.setInitialState();
        }

        showError(message) {
            this.updatePreviewCode({
                error: true,
                message: message
            });
        }
    }
}

// Initialize only when DOM is ready and not already initialized
if (!window.playground) {
    document.addEventListener('DOMContentLoaded', () => {
        window.playground = new window.Aeodos.PlaygroundManager();
    });
}
