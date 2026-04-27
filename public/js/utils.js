// Configuration
// Updated: v7 - Fixed toast positioning, budget calculations, navigation
export const API_URL = 'http://localhost:8000';

// Standard Fetch Wrapper
export async function apiFetch(endpoint, options = {}) {
    try {
        const res = await window.fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `API Error: ${res.status} ${res.statusText}`);
        }
        return await res.json();
    } catch (e) {
        console.error(`[API Call failed: ${endpoint}]`, e);
        
        // Provide more specific error messages
        if (e.name === 'TypeError' && e.message.includes('Failed to fetch')) {
            throw new Error('Network error: Unable to connect to server. Please check your internet connection.');
        } else if (e.message.includes('CORS')) {
            throw new Error('Server configuration error. Please contact support.');
        } else {
            throw e;
        }
    }
}

// Router Event System
const routerEvents = new EventTarget();
export const onNavigate = (cb) => routerEvents.addEventListener('route', cb);

export function navigateTo(path) {
    if (window.location.hash !== `#${path}`) {
        window.location.hash = path;
    }
    routerEvents.dispatchEvent(new CustomEvent('route', { detail: path }));
}

// Minimal reactivity state wrapper
export class Store {
    constructor(initialState) {
        this.state = initialState;
        this.listeners = new Set();
    }

    get() { return this.state; }

    set(newState) {
        this.state = { ...this.state, ...newState };
        this.notify();
    }

    subscribe(listener) {
        this.listeners.add(listener);
        return () => this.listeners.delete(listener);
    }

    notify() {
        this.listeners.forEach(l => l(this.state));
    }
}

// Compact confirmation dialog
export function showConfirm(message, title = 'Confirm Action') {
    return new Promise((resolve) => {
        const dialog = document.createElement('div');
        dialog.className = 'confirm-dialog';
        dialog.innerHTML = `
            <div class="confirm-dialog-content">
                <div class="confirm-dialog-header">
                    <svg class="confirm-dialog-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                    <h3 class="confirm-dialog-title">${title}</h3>
                </div>
                <p class="confirm-dialog-message">${message}</p>
                <div class="confirm-dialog-actions">
                    <button class="btn btn-secondary" data-action="cancel">Cancel</button>
                    <button class="btn btn-danger" data-action="confirm">Confirm</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        document.body.style.overflow = 'hidden';
        
        const handleClick = (e) => {
            const action = e.target.dataset.action;
            if (action) {
                dialog.remove();
                document.body.style.overflow = 'auto';
                resolve(action === 'confirm');
            }
        };
        
        dialog.addEventListener('click', (e) => {
            if (e.target === dialog) {
                dialog.remove();
                document.body.style.overflow = 'auto';
                resolve(false);
            }
        });
        
        dialog.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', handleClick);
        });
    });
}
