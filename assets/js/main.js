window.Aeodos = window.Aeodos || {};

if (!window.Aeodos.UI) {
    window.Aeodos.UI = class AeodosUI {
        constructor() {
            this.apiEndpoint = 'http://api.canopus.software/aeodos';
            this.modal = document.getElementById('apiKeyModal');
            this.init();
            this.initStatCounters();
        }

        init() {
            this.attachEventListeners();
            this.initializeAnimations();
        }

        attachEventListeners() {
            document.getElementById('getApiKey')?.addEventListener('click', (e) => {
                e.preventDefault();
                this.showApiKeyModal();
            });

            // Close modal when clicking outside
            window.addEventListener('click', (e) => {
                if (e.target === this.modal) {
                    this.hideModal();
                }
            });

            // Handle scroll animations
            window.addEventListener('scroll', this.handleScroll.bind(this));
        }

        showApiKeyModal() {
            // Calculate scrollbar width to prevent layout shift
            const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
            document.documentElement.style.setProperty('--scrollbar-width', `${scrollbarWidth}px`);

            const modalContent = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2>Get Your API Key</h2>
                            <p>Start building with Aeodos today</p>
                        </div>
                        <form id="apiKeyForm" class="api-key-form">
                            <div class="form-group">
                                <label for="email">Business Email</label>
                                <input type="email" id="email" 
                                    placeholder="you@company.com"
                                    autocomplete="email"
                                    required>
                            </div>
                            <div class="form-group">
                                <label for="company">Company Name</label>
                                <input type="text" id="company" 
                                    placeholder="Your Company Name"
                                    autocomplete="organization"
                                    required>
                            </div>
                            <div class="form-submit">
                                <button type="submit" class="primary-btn">
                                    <span>Generate API Key</span>
                                    <div class="loading-spinner" style="display: none;"></div>
                                </button>
                            </div>
                        </form>
                        <button class="modal-close" aria-label="Close">&times;</button>
                    </div>
                </div>
            `;

            // Store current focus for restoration
            this.previousActiveElement = document.activeElement;

            // Update modal content and show
            this.modal.innerHTML = modalContent;
            this.modal.style.display = 'block';
            document.body.classList.add('modal-open');
            
            // Trigger animation after a small delay
            requestAnimationFrame(() => {
                this.modal.classList.add('active');
                // Focus first input after animation
                setTimeout(() => {
                    document.getElementById('email')?.focus();
                }, 300);
            });

            // Setup event listeners
            this.setupModalEventListeners();
        }

        setupModalEventListeners() {
            const form = document.getElementById('apiKeyForm');
            const closeBtn = this.modal.querySelector('.modal-close');

            // Form submission
            form?.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleApiKeyGeneration(e);
            });

            // Close on backdrop click
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal || e.target.classList.contains('modal-dialog')) {
                    this.hideModal();
                }
            });

            // Close button click
            closeBtn?.addEventListener('click', () => this.hideModal());

            // Close on escape key
            const handleEscape = (e) => {
                if (e.key === 'Escape') {
                    this.hideModal();
                    document.removeEventListener('keydown', handleEscape);
                }
            };
            document.addEventListener('keydown', handleEscape);

            // Focus trap
            this.setupFocusTrap();
        }

        async handleApiKeyGeneration(e) {
            const form = e.target;
            const submitBtn = form.querySelector('button[type="submit"]');
            const spinner = form.querySelector('.loading-spinner');
            const email = form.querySelector('#email');
            const company = form.querySelector('#company');

            // Clear previous errors
            this.clearErrors(form);

            // Validate
            if (!this.validateForm(email, company)) return;

            try {
                // Show loading state
                this.setFormLoading(true, submitBtn, spinner);

                const response = await fetch(`${this.apiEndpoint}/keys/generate`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email.value,
                        company_name: company.value
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to generate API key');
                }

                await this.showSuccessMessage(data.api_key);
            } catch (error) {
                this.showErrorMessage(error.message, form);
            } finally {
                this.setFormLoading(false, submitBtn, spinner);
            }
        }

        validateForm(email, company) {
            let isValid = true;

            if (!this.isValidEmail(email.value)) {
                this.showFieldError(email, 'Please enter a valid business email');
                isValid = false;
            }

            if (company.value.length < 2) {
                this.showFieldError(company, 'Company name is too short');
                isValid = false;
            }

            return isValid;
        }

        isValidEmail(email) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        }

        showFieldError(field, message) {
            const group = field.closest('.form-group');
            group.classList.add('error');
            
            const error = document.createElement('div');
            error.className = 'error-message';
            error.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 16 16">
                    <circle cx="8" cy="8" r="7" stroke="currentColor" fill="none"/>
                    <path d="M8 4v5M8 11v1" stroke="currentColor"/>
                </svg>
                ${message}
            `;
            
            group.appendChild(error);
        }

        clearErrors(form) {
            form.querySelectorAll('.form-group.error').forEach(group => {
                group.classList.remove('error');
                group.querySelector('.error-message')?.remove();
            });
        }

        setFormLoading(loading, button, spinner) {
            const buttonText = button.querySelector('span');
            if (loading) {
                button.classList.add('loading');
                spinner.style.display = 'block';
                buttonText.textContent = 'Generating...';
            } else {
                button.classList.remove('loading');
                spinner.style.display = 'none';
                buttonText.textContent = 'Generate API Key';
            }
        }

        async showSuccessMessage(apiKey) {
            const content = `
                <div class="modal-header">
                    <h2>API Key Generated!</h2>
                    <p>Keep this key safe and secure</p>
                </div>
                <div class="success-message">
                    <div class="api-key-display">
                        <code>${apiKey}</code>
                        <button class="copy-btn" data-key="${apiKey}">
                            Copy
                        </button>
                    </div>
                    <p class="warning">⚠️ This key will only be shown once!</p>
                    <button class="primary-btn" onclick="aeodosUI.hideModal()">
                        Done
                    </button>
                </div>
            `;

            const modalContent = this.modal.querySelector('.modal-content');
            modalContent.innerHTML = content;

            // Handle copy button
            modalContent.querySelector('.copy-btn').addEventListener('click', async (e) => {
                const btn = e.target;
                const key = btn.dataset.key;
                
                try {
                    await navigator.clipboard.writeText(key);
                    btn.textContent = 'Copied!';
                    btn.classList.add('copied');
                    setTimeout(() => {
                        btn.textContent = 'Copy';
                        btn.classList.remove('copied');
                    }, 2000);
                } catch (err) {
                    console.error('Failed to copy:', err);
                }
            });
        }

        setupFocusTrap() {
            const focusableElements = this.modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const firstFocusable = focusableElements[0];
            const lastFocusable = focusableElements[focusableElements.length - 1];

            const handleTabKey = (e) => {
                if (e.key !== 'Tab') return;

                if (e.shiftKey) {
                    if (document.activeElement === firstFocusable) {
                        e.preventDefault();
                        lastFocusable.focus();
                    }
                } else {
                    if (document.activeElement === lastFocusable) {
                        e.preventDefault();
                        firstFocusable.focus();
                    }
                }
            };

            this.modal.addEventListener('keydown', handleTabKey);
        }

        hideModal() {
            this.modal.classList.remove('active');
            
            // Restore body scroll and cleanup
            setTimeout(() => {
                this.modal.style.display = 'none';
                document.body.classList.remove('modal-open');
                document.documentElement.style.removeProperty('--scrollbar-width');
                
                // Restore focus
                if (this.previousActiveElement instanceof HTMLElement) {
                    this.previousActiveElement.focus();
                }
            }, 300);
        }

        showErrorMessage(message) {
            const errorBanner = document.createElement('div');
            errorBanner.className = 'error-message';
            errorBanner.textContent = message;
            
            const form = document.getElementById('apiKeyForm');
            form.insertBefore(errorBanner, form.firstChild);

            setTimeout(() => errorBanner.remove(), 5000);
        }

        initializeAnimations() {
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                    }
                });
            }, observerOptions);

            document.querySelectorAll('.feature-card, .hero-content, .hero-image')
                .forEach(el => observer.observe(el));
        }

        handleScroll() {
            const header = document.querySelector('.header');
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }

        initStatCounters() {
            const stats = document.querySelectorAll('.stat-number');
            const observerOptions = {
                threshold: 0.5,
                rootMargin: '0px'
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateCounter(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            }, observerOptions);

            stats.forEach(stat => observer.observe(stat));
        }

        animateCounter(element) {
            const target = parseFloat(element.dataset.value);
            const duration = 2000;
            const startTime = performance.now();
            const isDecimal = target % 1 !== 0;

            const update = (currentTime) => {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);

                // Easing function
                const eased = 1 - Math.pow(1 - progress, 3);
                const current = target * eased;

                element.textContent = isDecimal ? 
                    current.toFixed(1) : 
                    Math.round(current).toString();

                if (progress < 1) {
                    requestAnimationFrame(update);
                }
            };

            requestAnimationFrame(update);
        }
    }
}

// Initialize only if not already done
if (!window.aeodosUI) {
    window.aeodosUI = new window.Aeodos.UI();
}

// Handle errors globally
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    // You might want to send this to your error tracking service
});
