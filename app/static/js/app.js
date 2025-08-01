class AegisFinancialApp {
    constructor() {
        this.currentQuery = '';
        this.isProcessing = false;
        this.loadingSteps = ['step1', 'step2', 'step3', 'step4'];
        this.currentStep = 0;
        
        this.initializeElements();
        this.bindEvents();
        this.checkAPIStatus();
        this.initializeAnimations();
    }

    initializeElements() {
        // Input elements
        this.queryInput = document.getElementById('queryInput');
        this.submitBtn = document.getElementById('submitBtn');
        this.clearBtn = document.getElementById('clearBtn');
        
        // Status elements
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        
        // State containers
        this.resultsSection = document.getElementById('resultsSection');
        this.loadingState = document.getElementById('loadingState');
        this.resultsDisplay = document.getElementById('resultsDisplay');
        this.errorState = document.getElementById('errorState');
        
        // Content elements
        this.resultsContent = document.getElementById('resultsContent');
        this.errorMessage = document.getElementById('errorMessage');
        
        // Action buttons
        this.actionButtons = document.querySelectorAll('.action-btn');
        this.copyBtn = document.getElementById('copyBtn');
        this.shareBtn = document.getElementById('shareBtn');
        this.newQueryBtn = document.getElementById('newQueryBtn');
        this.retryBtn = document.getElementById('retryBtn');
    }

    bindEvents() {
        // Input events
        this.queryInput.addEventListener('input', this.handleInputChange.bind(this));
        this.queryInput.addEventListener('keydown', this.handleKeyDown.bind(this));
        
        // Button events
        this.submitBtn.addEventListener('click', this.handleSubmit.bind(this));
        this.clearBtn.addEventListener('click', this.handleClear.bind(this));
        this.newQueryBtn.addEventListener('click', this.handleNewQuery.bind(this));
        this.retryBtn.addEventListener('click', this.handleRetry.bind(this));
        
        // Action button events
        this.actionButtons.forEach(btn => {
            btn.addEventListener('click', this.handleQuickAction.bind(this));
        });
        
        // Utility button events
        this.copyBtn.addEventListener('click', this.handleCopy.bind(this));
        this.shareBtn.addEventListener('click', this.handleShare.bind(this));
        
        // Auto-resize textarea
        this.queryInput.addEventListener('input', this.autoResizeTextarea.bind(this));
    }

    initializeAnimations() {
        // Animate hero section on load
        this.animateOnLoad();
        
        // Intersection observer for scroll animations
        this.setupScrollAnimations();
    }

    animateOnLoad() {
        // Stagger animation for quick action buttons
        this.actionButtons.forEach((btn, index) => {
            btn.style.opacity = '0';
            btn.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                btn.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                btn.style.opacity = '1';
                btn.style.transform = 'translateY(0)';
            }, index * 100 + 500);
        });
    }

    setupScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });

        // Observe elements for scroll animations
        document.querySelectorAll('.query-container, .results-container').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
            observer.observe(el);
        });
    }

    async checkAPIStatus() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            if (data.status === 'healthy' && data.agent_ready) {
                this.updateStatus('online', 'System Ready');
            } else {
                this.updateStatus('error', 'System Initializing...');
                // Retry in 5 seconds
                setTimeout(() => this.checkAPIStatus(), 5000);
            }
        } catch (error) {
            this.updateStatus('error', 'Connection Failed');
            setTimeout(() => this.checkAPIStatus(), 10000);
        }
    }

    updateStatus(status, text) {
        this.statusDot.className = `status-dot ${status}`;
        this.statusText.textContent = text;
    }

    handleInputChange(event) {
        const value = event.target.value.trim();
        this.submitBtn.disabled = !value;
        
        // Update submit button text based on input
        const btnText = this.submitBtn.querySelector('.btn-text');
        if (value.length > 0) {
            btnText.textContent = 'Analyze';
            this.submitBtn.classList.add('ready');
        } else {
            btnText.textContent = 'Analyze';
            this.submitBtn.classList.remove('ready');
        }
    }

    handleKeyDown(event) {
        // Submit on Ctrl/Cmd + Enter
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            event.preventDefault();
            this.handleSubmit();
        }
    }

    autoResizeTextarea() {
        this.queryInput.style.height = 'auto';
        this.queryInput.style.height = Math.min(this.queryInput.scrollHeight, 200) + 'px';
    }

    handleQuickAction(event) {
        const query = event.currentTarget.dataset.query;
        this.queryInput.value = query;
        this.handleInputChange({ target: this.queryInput });
        
        // Auto-submit after a brief delay for UX
        setTimeout(() => {
            this.handleSubmit();
        }, 300);
        
        // Visual feedback
        event.currentTarget.style.transform = 'scale(0.95)';
        setTimeout(() => {
            event.currentTarget.style.transform = '';
        }, 150);
    }

    async handleSubmit() {
        if (this.isProcessing || !this.queryInput.value.trim()) return;
        
        this.currentQuery = this.queryInput.value.trim();
        this.isProcessing = true;
        
        // Show loading state
        this.showLoadingState();
        this.startLoadingAnimation();
        
        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: this.currentQuery
                })
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const data = await response.json();
            this.showResults(data.answer);
            
        } catch (error) {
            console.error('Query failed:', error);
            this.showError(error.message);
        } finally {
            this.isProcessing = false;
            this.stopLoadingAnimation();
        }
    }

    handleClear() {
        this.queryInput.value = '';
        this.handleInputChange({ target: this.queryInput });
        this.queryInput.focus();
        
        // Hide results if showing
        this.hideAllStates();
    }

    handleNewQuery() {
        this.hideAllStates();
        this.queryInput.focus();
        
        // Smooth scroll to top
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }

    handleRetry() {
        if (this.currentQuery) {
            this.queryInput.value = this.currentQuery;
            this.handleSubmit();
        }
    }

    async handleCopy() {
        try {
            const content = this.resultsContent.textContent;
            await navigator.clipboard.writeText(content);
            
            // Visual feedback
            const originalText = this.copyBtn.innerHTML;
            this.copyBtn.innerHTML = '<i class="fas fa-check"></i>';
            this.copyBtn.style.color = 'var(--accent-green)';
            
            setTimeout(() => {
                this.copyBtn.innerHTML = originalText;
                this.copyBtn.style.color = '';
            }, 2000);
            
        } catch (error) {
            console.error('Copy failed:', error);
        }
    }

    handleShare() {
        if (navigator.share) {
            navigator.share({
                title: 'Aegis Financial Analysis',
                text: this.resultsContent.textContent.substring(0, 200) + '...',
                url: window.location.href
            });
        } else {
            // Fallback to copy URL
            navigator.clipboard.writeText(window.location.href);
            
            // Visual feedback
            const originalText = this.shareBtn.innerHTML;
            this.shareBtn.innerHTML = '<i class="fas fa-check"></i>';
            this.shareBtn.style.color = 'var(--accent-green)';
            
            setTimeout(() => {
                this.shareBtn.innerHTML = originalText;
                this.shareBtn.style.color = '';
            }, 2000);
        }
    }

    showLoadingState() {
        this.hideAllStates();
        this.loadingState.classList.add('active');
        this.resultsSection.style.display = 'block';
        
        // Smooth scroll to results
        setTimeout(() => {
            this.resultsSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }, 100);
    }

    showResults(content) {
        this.hideAllStates();
        this.resultsDisplay.classList.add('active');
        this.resultsSection.style.display = 'block';
        
        // Format and display content
        this.formatAndDisplayContent(content);
        
        // Animate in
        this.resultsDisplay.style.opacity = '0';
        this.resultsDisplay.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            this.resultsDisplay.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            this.resultsDisplay.style.opacity = '1';
            this.resultsDisplay.style.transform = 'translateY(0)';
        }, 50);
    }

    showError(message) {
        this.hideAllStates();
        this.errorState.classList.add('active');
        this.errorMessage.textContent = message || 'An unexpected error occurred. Please try again.';
        this.resultsSection.style.display = 'block';
    }

    hideAllStates() {
        this.loadingState.classList.remove('active');
        this.resultsDisplay.classList.remove('active');
        this.errorState.classList.remove('active');
        
        // Reset loading steps
        document.querySelectorAll('.step').forEach(step => {
            step.classList.remove('active');
        });
    }

    formatAndDisplayContent(content) {
        // Convert newlines to paragraphs and format headers
        let formattedContent = content
            .split('\n\n')
            .map(paragraph => {
                paragraph = paragraph.trim();
                if (!paragraph) return '';
                
                // Check if it's a header (starts with ##, ###, etc.)
                if (paragraph.match(/^#+\s/)) {
                    const level = paragraph.match(/^#+/)[0].length;
                    const text = paragraph.replace(/^#+\s/, '');
                    return `<h${Math.min(level + 1, 6)}>${text}</h${Math.min(level + 1, 6)}>`;
                }
                
                // Check if it's a list item
                if (paragraph.match(/^\d+\.\s/) || paragraph.match(/^[-*]\s/)) {
                    return `<li>${paragraph.replace(/^(\d+\.\s|[-*]\s)/, '')}</li>`;
                }
                
                return `<p>${paragraph}</p>`;
            })
            .join('');
            
        // Wrap consecutive list items in ul/ol tags
        formattedContent = formattedContent
            .replace(/(<li>.*?<\/li>\s*)+/g, (match) => {
                return `<ul>${match}</ul>`;
            });
            
        this.resultsContent.innerHTML = formattedContent;
    }

    startLoadingAnimation() {
        this.currentStep = 0;
        this.animateLoadingSteps();
    }

    animateLoadingSteps() {
        if (!this.isProcessing) return;
        
        // Reset all steps
        document.querySelectorAll('.step').forEach(step => {
            step.classList.remove('active');
        });
        
        // Activate current step
        const currentStepElement = document.getElementById(this.loadingSteps[this.currentStep]);
        if (currentStepElement) {
            currentStepElement.classList.add('active');
        }
        
        // Move to next step
        this.currentStep = (this.currentStep + 1) % this.loadingSteps.length;
        
        // Continue animation
        setTimeout(() => {
            this.animateLoadingSteps();
        }, 1500);
    }

    stopLoadingAnimation() {
        // Activate all steps briefly to show completion
        document.querySelectorAll('.step').forEach(step => {
            step.classList.add('active');
        });
        
        setTimeout(() => {
            document.querySelectorAll('.step').forEach(step => {
                step.classList.remove('active');
            });
        }, 500);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AegisFinancialApp();
});

// Add some global utility functions
window.addEventListener('load', () => {
    // Remove loading class from body if it exists
    document.body.classList.remove('loading');
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Handle errors gracefully
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

// Add some nice touch interactions for mobile
if ('ontouchstart' in window) {
    document.body.classList.add('touch-device');
    
    // Add touch feedback to buttons
    document.addEventListener('touchstart', (e) => {
        if (e.target.matches('button, .btn-primary, .btn-secondary, .action-btn')) {
            e.target.style.transform = 'scale(0.95)';
        }
    });
    
    document.addEventListener('touchend', (e) => {
        if (e.target.matches('button, .btn-primary, .btn-secondary, .action-btn')) {
            setTimeout(() => {
                e.target.style.transform = '';
            }, 100);
        }
    });
}