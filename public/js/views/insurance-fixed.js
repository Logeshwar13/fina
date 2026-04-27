import { authState } from '../auth.js';
import { API_URL } from '../utils.js';

// Use API_URL instead of API_BASE
const API_BASE = API_URL;

// Storage keys for localStorage fallback
const STORAGE_KEYS = {
    policies: 'insurance_policies',
    assessments: 'insurance_assessments'
};

function getStorageData(key) {
    try {
        return JSON.parse(localStorage.getItem(key) || '[]');
    } catch {
        return [];
    }
}

function setStorageData(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

export default async function renderInsurance() {
    const { user } = authState.get();
    if (!user) return '<div>Please log in</div>';

    return `
        <div class="page-header">
            <div>
                <h1 class="page-title">Insurance Management</h1>
                <p class="page-subtitle">Manage your insurance policies and assess coverage needs</p>
            </div>
            <button id="btn-add-policy" class="btn btn-primary">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                Add Policy
            </button>
            <button id="btn-demo-data" class="btn btn-secondary" style="margin-left: 1rem;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                </svg>
                Load Demo Data
            </button>
        </div>

        <!-- Risk Assessment Card -->
        <div id="risk-assessment-card" class="card" style="margin-bottom: 1.5rem;">
            <div class="card-header">
                <h3 class="card-title">Insurance Risk Assessment</h3>
                <button id="btn-run-assessment" class="btn btn-secondary btn-sm">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 12a9 9 0 11-6.219-8.56"></path>
                    </svg>
                    Run Assessment
                </button>
            </div>
            <div id="assessment-content" class="card-body">
                <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 1rem; opacity: 0.5;">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <p>Run an assessment to get personalized insurance recommendations</p>
                </div>
            </div>
        </div>

        <!-- Policies Grid -->
        <div class="insurance-tabs" style="margin-bottom: 1.5rem;">
            <button class="insurance-tab active" data-type="all">All Policies</button>
            <button class="insurance-tab" data-type="health">Health</button>
            <button class="insurance-tab" data-type="life">Life</button>
            <button class="insurance-tab" data-type="vehicle">Vehicle</button>
            <button class="insurance-tab" data-type="home">Home</button>
            <button class="insurance-tab" data-type="travel">Travel</button>
        </div>

        <div id="policies-grid" class="grid grid-3">
            <div class="loading-spinner">Loading policies...</div>
        </div>

        <!-- Add/Edit Policy Modal -->
        <div id="policy-modal" class="modal" style="display: none;">
            <div class="modal-content" style="max-width: 600px;">
                <div class="modal-header">
                    <h3 id="modal-title">Add Insurance Policy</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="policy-form">
                        <input type="hidden" id="policy-id">
                        
                        <div class="form-group">
                            <label>Policy Type *</label>
                            <select id="policy-type" required>
                                <option value="">Select type</option>
                                <option value="health">Health Insurance</option>
                                <option value="life">Life Insurance</option>
                                <option value="vehicle">Vehicle Insurance</option>
                                <option value="home">Home Insurance</option>
                                <option value="travel">Travel Insurance</option>
                            </select>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>Provider *</label>
                                <input type="text" id="provider" placeholder="e.g., HDFC Ergo" required>
                            </div>
                            <div class="form-group">
                                <label>Policy Number</label>
                                <input type="text" id="policy-number" placeholder="Optional">
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>Coverage Amount (₹) *</label>
                                <input type="number" id="coverage-amount" placeholder="500000" required min="0">
                            </div>
                            <div class="form-group">
                                <label>Premium Amount (₹) *</label>
                                <input type="number" id="premium-amount" placeholder="10000" required min="0">
                            </div>
                        </div>

                        <div class="form-group">
                            <label>Premium Frequency *</label>
                            <select id="premium-frequency" required>
                                <option value="annual">Annual</option>
                                <option value="monthly">Monthly</option>
                                <option value="quarterly">Quarterly</option>
                            </select>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>Start Date *</label>
                                <input type="date" id="start-date" required>
                            </div>
                            <div class="form-group">
                                <label>End Date *</label>
                                <input type="date" id="end-date" required>
                            </div>
                        </div>

                        <div class="form-group">
                            <label>Notes</label>
                            <textarea id="notes" rows="3" placeholder="Additional information..."></textarea>
                        </div>

                        <div class="modal-actions">
                            <button type="button" class="btn btn-secondary modal-close">Cancel</button>
                            <button type="submit" class="btn btn-primary">Save Policy</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
}

// Initialize after render
setTimeout(() => {
    try {
        initInsuranceHandlers();
    } catch (error) {
        console.error('Error initializing insurance page:', error);
    }
}, 100);

let currentFilter = 'all';
let allPolicies = [];

async function initInsuranceHandlers() {
    const { user } = authState.get();
    if (!user) return;

    try {
        // Load policies
        await loadPolicies(user.id);

        // Tab switching
        document.querySelectorAll('.insurance-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.insurance-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                currentFilter = tab.dataset.type;
                renderPolicies();
            });
        });

        // Add policy button
        document.getElementById('btn-add-policy')?.addEventListener('click', () => {
            openPolicyModal();
        });

        // Demo data button
        document.getElementById('btn-demo-data')?.addEventListener('click', () => {
            loadDemoData(user.id);
        });

        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                btn.closest('.modal').style.display = 'none';
            });
        });

        // Policy form submit
        document.getElementById('policy-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await savePolicyForm(user.id);
        });

    } catch (error) {
        console.error('Error in initInsuranceHandlers:', error);
    }
}

async function loadPolicies(userId) {
    try {
        // Try localStorage first for demo
        const stored = getStorageData(STORAGE_KEYS.policies);
        allPolicies = stored.filter(p => p.user_id === userId);
        renderPolicies();
    } catch (err) {
        console.error('Error loading policies:', err);
        document.getElementById('policies-grid').innerHTML = 
            '<p style="color: var(--text-secondary); text-align: center; padding: 2rem;">Failed to load policies</p>';
    }
}

function renderPolicies() {
    const filtered = currentFilter === 'all' 
        ? allPolicies 
        : allPolicies.filter(p => p.policy_type === currentFilter);

    const grid = document.getElementById('policies-grid');
    
    if (filtered.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-secondary);">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 1rem; opacity: 0.5;">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
                <p>No ${currentFilter === 'all' ? '' : currentFilter} insurance policies found</p>
                <button class="btn btn-primary" style="margin-top: 1rem;" onclick="document.getElementById('btn-add-policy').click()">
                    Add Your First Policy
                </button>
            </div>
        `;
        return;
    }

    grid.innerHTML = filtered.map(policy => {
        const typeIcons = {
            health: '<path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>',
            life: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>',
            vehicle: '<path d="M5 17h14v2H5v-2zm0-4h14v2H5v-2zm0-4h14v2H5V9z"></path>',
            home: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>',
            travel: '<circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>'
        };

        return `
            <div class="card policy-card" data-policy-id="${policy.id}">
                <div class="card-body">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <div class="policy-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    ${typeIcons[policy.policy_type] || typeIcons.health}
                                </svg>
                            </div>
                            <div>
                                <h4 style="font-size: 0.875rem; font-weight: 600; text-transform: capitalize; margin-bottom: 0.25rem;">
                                    ${policy.policy_type} Insurance
                                </h4>
                                <p style="font-size: 0.75rem; color: var(--text-secondary);">${policy.provider}</p>
                            </div>
                        </div>
                    </div>

                    <div class="policy-details">
                        <div class="detail-row">
                            <span class="detail-label">Coverage</span>
                            <span class="detail-value">₹${policy.coverage_amount.toLocaleString('en-IN')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Premium</span>
                            <span class="detail-value">₹${policy.premium_amount.toLocaleString('en-IN')}/${policy.premium_frequency}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Valid Until</span>
                            <span class="detail-value">${new Date(policy.end_date).toLocaleDateString('en-IN')}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function openPolicyModal() {
    const modal = document.getElementById('policy-modal');
    const form = document.getElementById('policy-form');
    form.reset();
    document.getElementById('modal-title').textContent = 'Add Insurance Policy';
    modal.style.display = 'flex';
}

async function savePolicyForm(userId) {
    const data = {
        id: 'policy_' + Date.now(),
        user_id: userId,
        policy_type: document.getElementById('policy-type').value,
        provider: document.getElementById('provider').value,
        policy_number: document.getElementById('policy-number').value,
        coverage_amount: parseFloat(document.getElementById('coverage-amount').value),
        premium_amount: parseFloat(document.getElementById('premium-amount').value),
        premium_frequency: document.getElementById('premium-frequency').value,
        start_date: new Date(document.getElementById('start-date').value).toISOString(),
        end_date: new Date(document.getElementById('end-date').value).toISOString(),
        beneficiaries: [],
        status: 'active',
        notes: document.getElementById('notes').value,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
    };

    try {
        // Save to localStorage
        const stored = getStorageData(STORAGE_KEYS.policies);
        stored.push(data);
        setStorageData(STORAGE_KEYS.policies, stored);

        document.getElementById('policy-modal').style.display = 'none';
        await loadPolicies(userId);
        showToast('Policy added successfully', 'success');
    } catch (err) {
        console.error('Error saving policy:', err);
        showToast('Failed to save policy', 'error');
    }
}

function loadDemoData(userId) {
    const demoPolicies = [
        {
            id: 'demo_health_1',
            user_id: userId,
            policy_type: 'health',
            provider: 'HDFC Ergo',
            policy_number: 'HE123456789',
            coverage_amount: 500000,
            premium_amount: 12000,
            premium_frequency: 'annual',
            start_date: '2024-01-01T00:00:00Z',
            end_date: '2024-12-31T23:59:59Z',
            beneficiaries: [],
            status: 'active',
            notes: 'Family health insurance policy',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
        },
        {
            id: 'demo_life_1',
            user_id: userId,
            policy_type: 'life',
            provider: 'LIC of India',
            policy_number: 'LIC987654321',
            coverage_amount: 2000000,
            premium_amount: 25000,
            premium_frequency: 'annual',
            start_date: '2023-06-01T00:00:00Z',
            end_date: '2043-06-01T23:59:59Z',
            beneficiaries: [],
            status: 'active',
            notes: 'Term life insurance policy',
            created_at: '2023-06-01T00:00:00Z',
            updated_at: '2023-06-01T00:00:00Z'
        }
    ];

    setStorageData(STORAGE_KEYS.policies, demoPolicies);
    loadPolicies(userId);
    showToast('Demo data loaded successfully', 'success');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}