/**
 * Stinger Browser Extension Integration Example
 * 
 * This example shows how to integrate Stinger guardrails into a browser extension
 * that monitors chat interfaces and provides real-time content checking.
 */

// Configuration
const STINGER_API_URL = 'http://localhost:8888';
const PRESET = 'customer_service';

// Stinger API client
class StingerClient {
    constructor(baseUrl = STINGER_API_URL) {
        this.baseUrl = baseUrl;
        this.cache = new Map();
    }

    async checkContent(text, kind = 'prompt') {
        try {
            const response = await fetch(`${this.baseUrl}/v1/check`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    kind: kind,
                    preset: PRESET
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Stinger API error:', error);
            return null;
        }
    }

    async getRules(preset = PRESET) {
        // Check cache first
        const cached = this.cache.get(preset);
        if (cached && Date.now() - cached.timestamp < 300000) { // 5 min cache
            return cached.data;
        }

        try {
            const response = await fetch(`${this.baseUrl}/v1/rules?preset=${preset}`);
            const data = await response.json();
            
            this.cache.set(preset, {
                data: data,
                timestamp: Date.now()
            });
            
            return data;
        } catch (error) {
            console.error('Failed to fetch rules:', error);
            return null;
        }
    }

    async checkHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return await response.json();
        } catch (error) {
            return { status: 'error', message: error.message };
        }
    }
}

// UI integration
class GuardrailUI {
    constructor() {
        this.client = new StingerClient();
        this.init();
    }

    init() {
        // Create status indicator
        this.createStatusIndicator();
        
        // Monitor text inputs
        this.monitorInputs();
        
        // Check API health
        this.checkApiHealth();
    }

    createStatusIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'stinger-status';
        indicator.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 10px 15px;
            background: #28a745;
            color: white;
            border-radius: 5px;
            font-family: Arial, sans-serif;
            font-size: 14px;
            z-index: 10000;
            cursor: pointer;
        `;
        indicator.textContent = 'Stinger: Active';
        document.body.appendChild(indicator);
        
        // Click to see details
        indicator.addEventListener('click', () => this.showDetails());
    }

    async checkApiHealth() {
        const health = await this.client.checkHealth();
        const indicator = document.getElementById('stinger-status');
        
        if (health.status === 'healthy') {
            indicator.style.background = '#28a745';
            indicator.textContent = 'Stinger: Active';
        } else {
            indicator.style.background = '#dc3545';
            indicator.textContent = 'Stinger: Offline';
        }
    }

    monitorInputs() {
        // Monitor all textareas and input fields
        document.addEventListener('input', async (event) => {
            const target = event.target;
            
            if (target.tagName === 'TEXTAREA' || 
                (target.tagName === 'INPUT' && target.type === 'text')) {
                
                // Debounce to avoid too many API calls
                clearTimeout(target.checkTimeout);
                target.checkTimeout = setTimeout(() => {
                    this.checkInput(target);
                }, 500);
            }
        });

        // Check on form submission
        document.addEventListener('submit', async (event) => {
            const form = event.target;
            const inputs = form.querySelectorAll('textarea, input[type="text"]');
            
            for (const input of inputs) {
                const result = await this.checkInput(input, false);
                if (result && result.action === 'block') {
                    event.preventDefault();
                    this.showWarning(input, result.reasons);
                    return;
                }
            }
        });
    }

    async checkInput(element, showIndicator = true) {
        const text = element.value.trim();
        if (!text) return null;

        const result = await this.client.checkContent(text);
        if (!result) return null;

        // Remove any existing indicators
        const existing = element.parentElement.querySelector('.stinger-indicator');
        if (existing) existing.remove();

        if (showIndicator) {
            // Create visual indicator
            const indicator = document.createElement('div');
            indicator.className = 'stinger-indicator';
            indicator.style.cssText = `
                position: absolute;
                right: 5px;
                top: 5px;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                pointer-events: none;
            `;

            // Set color based on action
            if (result.action === 'block') {
                indicator.style.background = '#dc3545';
            } else if (result.action === 'warn') {
                indicator.style.background = '#ffc107';
            } else {
                indicator.style.background = '#28a745';
            }

            // Position relative to input
            element.style.position = 'relative';
            element.parentElement.appendChild(indicator);
        }

        return result;
    }

    showWarning(element, reasons) {
        const warning = document.createElement('div');
        warning.style.cssText = `
            position: absolute;
            background: #dc3545;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-top: 5px;
            z-index: 10001;
            max-width: 300px;
        `;
        warning.innerHTML = `
            <strong>Content Blocked:</strong><br>
            ${reasons.join('<br>')}
        `;
        
        element.parentElement.appendChild(warning);
        
        // Remove after 5 seconds
        setTimeout(() => warning.remove(), 5000);
    }

    async showDetails() {
        const rules = await this.client.getRules();
        const health = await this.client.checkHealth();
        
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 10002;
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
        `;
        
        modal.innerHTML = `
            <h2>Stinger Guardrails Status</h2>
            <p><strong>API Status:</strong> ${health.status}</p>
            <p><strong>Preset:</strong> ${rules?.preset || 'N/A'}</p>
            <p><strong>Active Guardrails:</strong> ${health.guardrail_count || 0}</p>
            
            <h3>Input Guardrails:</h3>
            <ul>
                ${Object.entries(rules?.guardrails?.input_guardrails || {})
                    .map(([name, config]) => `<li>${name} (${config.type})</li>`)
                    .join('')}
            </ul>
            
            <h3>Output Guardrails:</h3>
            <ul>
                ${Object.entries(rules?.guardrails?.output_guardrails || {})
                    .map(([name, config]) => `<li>${name} (${config.type})</li>`)
                    .join('')}
            </ul>
            
            <button onclick="this.parentElement.remove()" style="
                margin-top: 15px;
                padding: 10px 20px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            ">Close</button>
        `;
        
        document.body.appendChild(modal);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new GuardrailUI());
} else {
    new GuardrailUI();
}