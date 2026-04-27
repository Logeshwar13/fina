import { authState } from '../auth.js';
import { API_URL } from '../utils.js';

export default async function renderInsurance() {
    const { user } = authState.get();
    if (!user) return '<div>Please log in</div>';

    return `
        <div class="page-header">
            <div>
                <h1 class="page-title">Insurance Management</h1>
                <p class="page-subtitle">Protect your financial future with smart insurance planning</p>
            </div>
            <div class="page-actions">
                <button id="btn-load-demo" class="btn btn-secondary">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                        <path d="M2 17l10 5 10-5"></path>
                        <path d="M2 12l10 5 10-5"></path>
                    </svg>
                    Load Demo Data
                </button>
                <button id="btn-add-policy" class="btn btn-primary">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    Add Policy
                </button>
            </div>
        </div>

        <!-- Insurance Calculator Card -->
        <div class="card" style="margin-bottom: 2rem;">
            <div class="card-header">
                <div class="card-title-group">
                    <h3 class="card-title">Insurance Calculator</h3>
                    <p class="card-subtitle">Calculate how much insurance coverage you need</p>
                </div>
                <button id="btn-calculate" class="btn btn-primary btn-sm">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Calculate Coverage
                </button>
            </div>
            <div class="card-body">
                <div id="calculator-content" class="calculator-grid">
                    <div class="calculator-input">
                        <label>Your Age</label>
                        <input type="number" id="calc-age" placeholder="30" min="18" max="80">
                    </div>
                    <div class="calculator-input">
                        <label>Annual Income (₹)</label>
                        <input type="number" id="calc-income" placeholder="1200000" min="0">
                    </div>
                    <div class="calculator-input">
                        <label>Dependents</label>
                        <input type="number" id="calc-dependents" placeholder="2" min="0">
                    </div>
                    <div class="calculator-input">
                        <label>Existing Loans (₹)</label>
                        <input type="number" id="calc-loans" placeholder="500000" min="0">
                    </div>
                </div>
                <div id="calculator-results" class="calculator-results" style="display: none;">
                    <div class="result-card">
                        <h4>Recommended Life Insurance</h4>
                        <div class="result-amount" id="life-amount">₹0</div>
                        <p class="result-desc">Based on 10-12x your annual income</p>
                    </div>
                    <div class="result-card">
                        <h4>Recommended Health Insurance</h4>
                        <div class="result-amount" id="health-amount">₹0</div>
                        <p class="result-desc">Covers medical emergencies and treatments</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Policy Types Grid -->
        <div class="grid grid-3" style="margin-bottom: 2rem;">
            <div class="card policy-type-card" data-type="health">
                <div class="card-body">
                    <div class="policy-type-icon health">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                        </svg>
                    </div>
                    <h3>Health Insurance</h3>
                    <p>Covers medical expenses, hospitalization, and treatments</p>
                    <div class="policy-stats">
                        <span id="health-count">0 policies</span>
                        <span id="health-coverage">₹0 coverage</span>
                    </div>
                </div>
            </div>

            <div class="card policy-type-card" data-type="life">
                <div class="card-body">
                    <div class="policy-type-icon life">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                    </div>
                    <h3>Life Insurance</h3>
                    <p>Financial protection for your family and dependents</p>
                    <div class="policy-stats">
                        <span id="life-count">0 policies</span>
                        <span id="life-coverage">₹0 coverage</span>
                    </div>
                </div>
            </div>

            <div class="card policy-type-card" data-type="vehicle">
                <div class="card-body">
                    <div class="policy-type-icon vehicle">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9L18.4 10c-.4-.8-1.2-1.3-2.1-1.3H7.7c-.9 0-1.7.5-2.1 1.3l-2.1 1.1C2.7 11.3 2 12.1 2 13v3c0 .6.4 1 1 1h2"></path>
                            <circle cx="7" cy="17" r="2"></circle>
                            <circle cx="17" cy="17" r="2"></circle>
                        </svg>
                    </div>
                    <h3>Vehicle Insurance</h3>
                    <p>Comprehensive coverage for your cars and bikes</p>
                    <div class="policy-stats">
                        <span id="vehicle-count">0 policies</span>
                        <span id="vehicle-coverage">₹0 coverage</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- My Policies Section -->
        <div class="card">
            <div class="card-header">
                <div class="card-title-group">
                    <h3 class="card-title">My Insurance Policies</h3>
                    <p class="card-subtitle">Manage and track all your insurance policies</p>
                </div>
                <div class="card-filters">
                    <button class="filter-btn active" data-filter="all">All</button>
                    <button class="filter-btn" data-filter="health">Health</button>
                    <button class="filter-btn" data-filter="life">Life</button>
                    <button class="filter-btn" data-filter="vehicle">Vehicle</button>
                </div>
            </div>
            <div class="card-body">
                <div id="policies-list" class="policies-list">
                    <div class="empty-state">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                        </svg>
                        <h4>No Insurance Policies Yet</h4>
                        <p>Start by adding your first insurance policy or load demo data to explore features</p>
                        <button class="btn btn-primary" onclick="document.getElementById('btn-add-policy').click()">
                            Add Your First Policy
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add Policy Modal -->
        <div id="add-policy-modal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Add Insurance Policy</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="policy-form">
                        <div class="form-group">
                            <label>Policy Type</label>
                            <select id="policy-type" required>
                                <option value="">Select insurance type</option>
                                <option value="health">Health Insurance</option>
                                <option value="life">Life Insurance</option>
                                <option value="vehicle">Vehicle Insurance</option>
                                <option value="home">Home Insurance</option>
                                <option value="travel">Travel Insurance</option>
                            </select>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>Insurance Provider</label>
                                <input type="text" id="provider" placeholder="e.g., HDFC Ergo, LIC" required>
                            </div>
                            <div class="form-group">
                                <label>Policy Number</label>
                                <input type="text" id="policy-number" placeholder="Policy number">
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>Coverage Amount (₹)</label>
                                <input type="number" id="coverage-amount" placeholder="500000" required>
                            </div>
                            <div class="form-group">
                                <label>Annual Premium (₹)</label>
                                <input type="number" id="premium-amount" placeholder="12000" required>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>Start Date</label>
                                <input type="date" id="start-date" required>
                            </div>
                            <div class="form-group">
                                <label>End Date</label>
                                <input type="date" id="end-date" required>
                            </div>
                        </div>

                        <div class="modal-actions">
                            <button type="button" class="btn btn-secondary modal-close">Cancel</button>
                            <button type="submit" class="btn btn-primary">Add Policy</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
}

// Initialize after DOM is ready
setTimeout(() => {
    initInsuranceFeature();
}, 100);

let userPolicies = [];
let currentFilter = 'all';

function initInsuranceFeature() {
    const { user } = authState.get();
    if (!user) return;

    loadUserPolicies();
    setupEventListeners();
}

function setupEventListeners() {
    // Load demo data
    document.getElementById('btn-load-demo')?.addEventListener('click', loadDemoData);
    
    // Add policy
    document.getElementById('btn-add-policy')?.addEventListener('click', openAddPolicyModal);
    
    // Calculate coverage
    document.getElementById('btn-calculate')?.addEventListener('click', calculateCoverage);
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            renderPolicies();
        });
    });
    
    // Modal close
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('add-policy-modal').style.display = 'none';
        });
    });
    
    // Policy form submit
    document.getElementById('policy-form')?.addEventListener('submit', handleAddPolicy);
    
    // Policy type cards click
    document.querySelectorAll('.policy-type-card').forEach(card => {
        card.addEventListener('click', () => {
            const type = card.dataset.type;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            document.querySelector(`[data-filter="${type}"]`)?.classList.add('active');
            currentFilter = type;
            renderPolicies();
        });
    });
}

function loadUserPolicies() {
    try {
        const stored = localStorage.getItem('user_insurance_policies');
        userPolicies = stored ? JSON.parse(stored) : [];
        renderPolicies();
        updatePolicyStats();
    } catch (error) {
        console.error('Error loading policies:', error);
        userPolicies = [];
    }
}

function savePolicies() {
    try {
        localStorage.setItem('user_insurance_policies', JSON.stringify(userPolicies));
        updatePolicyStats();
    } catch (error) {
        console.error('Error saving policies:', error);
    }
}

function renderPolicies() {
    const container = document.getElementById('policies-list');
    if (!container) return;

    const filtered = currentFilter === 'all' 
        ? userPolicies 
        : userPolicies.filter(p => p.type === currentFilter);

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
                <h4>No ${currentFilter === 'all' ? '' : currentFilter} policies found</h4>
                <p>Add your first ${currentFilter === 'all' ? 'insurance' : currentFilter} policy to get started</p>
                <button class="btn btn-primary" onclick="document.getElementById('btn-add-policy').click()">
                    Add Policy
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = filtered.map(policy => `
        <div class="policy-item">
            <div class="policy-icon ${policy.type}">
                ${getPolicyIcon(policy.type)}
            </div>
            <div class="policy-details">
                <h4>${policy.type.charAt(0).toUpperCase() + policy.type.slice(1)} Insurance</h4>
                <p class="policy-provider">${policy.provider}</p>
                <p class="policy-number">${policy.policyNumber || 'No policy number'}</p>
            </div>
            <div class="policy-amounts">
                <div class="coverage-amount">₹${policy.coverageAmount.toLocaleString('en-IN')}</div>
                <div class="premium-amount">₹${policy.premiumAmount.toLocaleString('en-IN')}/year</div>
            </div>
            <div class="policy-dates">
                <div class="end-date">Expires: ${new Date(policy.endDate).toLocaleDateString('en-IN')}</div>
                ${isExpiringSoon(policy.endDate) ? '<span class="expiry-warning">⚠️ Expiring Soon</span>' : ''}
            </div>
            <button class="btn btn-danger btn-sm" onclick="deletePolicy('${policy.id}')">Delete</button>
        </div>
    `).join('');
}

function updatePolicyStats() {
    const healthPolicies = userPolicies.filter(p => p.type === 'health');
    const lifePolicies = userPolicies.filter(p => p.type === 'life');
    const vehiclePolicies = userPolicies.filter(p => p.type === 'vehicle');

    document.getElementById('health-count').textContent = `${healthPolicies.length} policies`;
    document.getElementById('health-coverage').textContent = `₹${healthPolicies.reduce((sum, p) => sum + p.coverageAmount, 0).toLocaleString('en-IN')} coverage`;

    document.getElementById('life-count').textContent = `${lifePolicies.length} policies`;
    document.getElementById('life-coverage').textContent = `₹${lifePolicies.reduce((sum, p) => sum + p.coverageAmount, 0).toLocaleString('en-IN')} coverage`;

    document.getElementById('vehicle-count').textContent = `${vehiclePolicies.length} policies`;
    document.getElementById('vehicle-coverage').textContent = `₹${vehiclePolicies.reduce((sum, p) => sum + p.coverageAmount, 0).toLocaleString('en-IN')} coverage`;
}

function calculateCoverage() {
    const age = parseInt(document.getElementById('calc-age').value) || 30;
    const income = parseInt(document.getElementById('calc-income').value) || 1200000;
    const dependents = parseInt(document.getElementById('calc-dependents').value) || 2;
    const loans = parseInt(document.getElementById('calc-loans').value) || 0;

    // Life insurance: 10-15x annual income + loans + dependent factor
    const lifeInsurance = (income * 12) + loans + (dependents * 500000);
    
    // Health insurance: Base amount + age factor + dependent factor
    let healthInsurance = 500000; // Base 5 lakh
    if (age > 30) healthInsurance += (age - 30) * 25000;
    healthInsurance += dependents * 200000;

    document.getElementById('life-amount').textContent = `₹${lifeInsurance.toLocaleString('en-IN')}`;
    document.getElementById('health-amount').textContent = `₹${healthInsurance.toLocaleString('en-IN')}`;
    
    document.getElementById('calculator-results').style.display = 'grid';
    
    showToast('Coverage calculated based on your profile!', 'success');
}

function loadDemoData() {
    const demoData = [
        {
            id: 'demo1',
            type: 'health',
            provider: 'HDFC Ergo',
            policyNumber: 'HE123456789',
            coverageAmount: 500000,
            premiumAmount: 12000,
            startDate: '2024-01-01',
            endDate: '2024-12-31'
        },
        {
            id: 'demo2',
            type: 'life',
            provider: 'LIC of India',
            policyNumber: 'LIC987654321',
            coverageAmount: 2000000,
            premiumAmount: 25000,
            startDate: '2023-06-01',
            endDate: '2043-06-01'
        },
        {
            id: 'demo3',
            type: 'vehicle',
            provider: 'Bajaj Allianz',
            policyNumber: 'BA456789123',
            coverageAmount: 800000,
            premiumAmount: 8500,
            startDate: '2024-03-15',
            endDate: '2025-03-14'
        }
    ];

    userPolicies = demoData;
    savePolicies();
    renderPolicies();
    showToast('Demo data loaded successfully!', 'success');
}

function openAddPolicyModal() {
    document.getElementById('add-policy-modal').style.display = 'flex';
}

function handleAddPolicy(e) {
    e.preventDefault();
    
    const newPolicy = {
        id: 'policy_' + Date.now(),
        type: document.getElementById('policy-type').value,
        provider: document.getElementById('provider').value,
        policyNumber: document.getElementById('policy-number').value,
        coverageAmount: parseInt(document.getElementById('coverage-amount').value),
        premiumAmount: parseInt(document.getElementById('premium-amount').value),
        startDate: document.getElementById('start-date').value,
        endDate: document.getElementById('end-date').value
    };

    userPolicies.push(newPolicy);
    savePolicies();
    renderPolicies();
    
    document.getElementById('add-policy-modal').style.display = 'none';
    document.getElementById('policy-form').reset();
    
    showToast('Policy added successfully!', 'success');
}

window.deletePolicy = function(policyId) {
    if (confirm('Are you sure you want to delete this policy?')) {
        userPolicies = userPolicies.filter(p => p.id !== policyId);
        savePolicies();
        renderPolicies();
        showToast('Policy deleted successfully!', 'success');
    }
};

function getPolicyIcon(type) {
    const icons = {
        health: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>',
        life: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>',
        vehicle: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9L18.4 10c-.4-.8-1.2-1.3-2.1-1.3H7.7c-.9 0-1.7.5-2.1 1.3l-2.1 1.1C2.7 11.3 2 12.1 2 13v3c0 .6.4 1 1 1h2"></path><circle cx="7" cy="17" r="2"></circle><circle cx="17" cy="17" r="2"></circle></svg>',
        home: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path></svg>',
        travel: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
    };
    return icons[type] || icons.health;
}

function isExpiringSoon(endDate) {
    const today = new Date();
    const expiry = new Date(endDate);
    const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry <= 60 && daysUntilExpiry > 0;
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