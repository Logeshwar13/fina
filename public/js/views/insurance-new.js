import { authState } from '../auth.js';
import { API_URL } from '../utils.js';

// VERSION CHECK - If you see this in console, the correct file is loading
console.log('🔵 Insurance View v30 loaded - NEW UI with all fields');

// Use API_URL as API_BASE for consistency
const API_BASE = API_URL;

// Temporary localStorage-based storage for demo (until Supabase tables are created)
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
    localStorage.setItem(key, JSON.stringify(data));
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
        </div>

        <!-- Risk Assessment Card -->
        <div id="risk-assessment-card" class="card" style="margin-bottom: 1.5rem;">
            <div class="card-header">
                <h3 class="card-title">Insurance Risk Assessment</h3>
                <div style="display: flex; gap: 0.5rem;">
                    <button id="btn-print-assessment" class="btn btn-secondary btn-sm" style="display: none;">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="6 9 6 2 18 2 18 9"></polyline>
                            <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
                            <rect x="6" y="14" width="12" height="8"></rect>
                        </svg>
                        Print Report
                    </button>
                    <button id="btn-run-assessment" class="btn btn-secondary btn-sm">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 12a9 9 0 11-6.219-8.56"></path>
                        </svg>
                        Run Assessment
                    </button>
                </div>
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

        <!-- Assessment Modal -->
        <div id="assessment-modal" class="modal" style="display: none;">
            <div class="modal-content" style="max-width: 700px;">
                <div class="modal-header">
                    <h3>Insurance Risk Assessment</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="assessment-form">
                        <div class="form-row">
                            <div class="form-group">
                                <label>Your Age *</label>
                                <input type="number" id="age" placeholder="30" required min="18" max="100">
                            </div>
                            <div class="form-group">
                                <label>Number of Dependents *</label>
                                <input type="number" id="dependents" placeholder="2" required min="0">
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>Annual Income (₹) *</label>
                                <input type="number" id="annual-income" placeholder="1200000" required min="0">
                            </div>
                            <div class="form-group">
                                <label>Monthly Expenses (₹) *</label>
                                <input type="number" id="monthly-expenses" placeholder="50000" required min="0">
                            </div>
                        </div>

                        <div class="form-group">
                            <label>Existing Loans (₹)</label>
                            <input type="number" id="existing-loans" placeholder="0" min="0">
                        </div>

                        <div class="form-group">
                            <label>Health Conditions (if any)</label>
                            <input type="text" id="health-conditions" placeholder="e.g., diabetes, hypertension (comma-separated)">
                        </div>

                        <div class="form-group">
                            <label style="display: flex; align-items: center; gap: 0.5rem;">
                                <input type="checkbox" id="smoking">
                                <span>I am a smoker</span>
                            </label>
                        </div>

                        <div class="form-group">
                            <label>City Tier</label>
                            <select id="city-tier">
                                <option value="metro">Metro (Mumbai, Delhi, Bangalore, etc.)</option>
                                <option value="tier1">Tier 1 City</option>
                                <option value="tier2">Tier 2 City</option>
                                <option value="tier3">Tier 3 City</option>
                            </select>
                        </div>

                        <div class="modal-actions">
                            <button type="button" class="btn btn-secondary modal-close">Cancel</button>
                            <button type="submit" class="btn btn-primary">Calculate Coverage</button>
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
        // Add demo data button inline to avoid import issues
        addDemoDataButtonInline();
    } catch (error) {
        console.error('Error initializing insurance page:', error);
        // Show a user-friendly error message
        const content = document.getElementById('assessment-content');
        if (content) {
            content.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    <p>Insurance feature is loading...</p>
                    <button onclick="location.reload()" class="btn btn-primary" style="margin-top: 1rem;">
                        Refresh Page
                    </button>
                </div>
            `;
        }
    }
}, 100);

function addDemoDataButtonInline() {
    const header = document.querySelector('.page-header');
    if (header && !document.getElementById('btn-demo-data')) {
        const demoBtn = document.createElement('button');
        demoBtn.id = 'btn-demo-data';
        demoBtn.className = 'btn btn-secondary';
        demoBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                <path d="M2 17l10 5 10-5"></path>
                <path d="M2 12l10 5 10-5"></path>
            </svg>
            Load Demo Data
        `;
        demoBtn.style.marginLeft = '1rem';
        
        demoBtn.addEventListener('click', () => {
            const { user } = authState.get();
            if (user) {
                generateDemoData(user.id);
                location.reload();
            }
        });
        
        header.appendChild(demoBtn);
    }
}

function generateDemoData(userId) {
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
            beneficiaries: [
                { name: 'Spouse', relation: 'Wife', percentage: 60 },
                { name: 'Child 1', relation: 'Son', percentage: 40 }
            ],
            status: 'active',
            notes: 'Term life insurance policy',
            created_at: '2023-06-01T00:00:00Z',
            updated_at: '2023-06-01T00:00:00Z'
        }
    ];

    const demoAssessment = {
        id: 'demo_assessment_1',
        user_id: userId,
        age: 32,
        dependents: 2,
        annual_income: 1200000,
        monthly_expenses: 60000,
        existing_loans: 500000,
        health_conditions: ['hypertension'],
        lifestyle_factors: {
            smoking: false,
            city_tier: 'metro'
        },
        recommended_life_coverage: 15000000,
        recommended_health_coverage: 1200000,
        current_life_coverage: 2000000,
        current_health_coverage: 500000,
        coverage_gap_life: 13000000,
        coverage_gap_health: 700000,
        risk_score: 78,
        risk_level: 'high',
        recommendations: [
            'Increase life insurance coverage by ₹1,30,00,000 to adequately protect your dependents.',
            'Increase health insurance coverage by ₹7,00,000 to cover potential medical expenses.'
        ],
        created_at: '2024-04-20T10:30:00Z',
        updated_at: '2024-04-20T10:30:00Z'
    };

    // Store in localStorage
    localStorage.setItem('insurance_policies', JSON.stringify(demoPolicies));
    localStorage.setItem('insurance_assessments', JSON.stringify([demoAssessment]));
}

let currentFilter = 'all';
let allPolicies = [];

async function initInsuranceHandlers() {
    const { user } = authState.get();
    if (!user) return;

    try {
        // Load policies
        await loadPolicies(user.id);

        // Load latest assessment
        await loadLatestAssessment(user.id);
    } catch (error) {
        console.error('Error initializing insurance:', error);
    }

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

    // Run assessment button
    document.getElementById('btn-run-assessment')?.addEventListener('click', () => {
        openAssessmentModal();
    });

    // Print assessment button
    document.getElementById('btn-print-assessment')?.addEventListener('click', () => {
        printAssessmentReport();
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

    // Assessment form submit
    document.getElementById('assessment-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await runAssessment(user.id);
    });
}

async function loadPolicies(userId) {
    try {
        // Try API first, fallback to localStorage
        try {
            const res = await fetch(`${API_BASE}/insurance/policies/${userId}`);
            if (res.ok) {
                allPolicies = await res.json();
                renderPolicies();
                return;
            }
        } catch (apiError) {
            console.log('API not available, using localStorage');
        }
        
        // Fallback to localStorage
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
        const endDate = new Date(policy.end_date);
        const daysRemaining = Math.ceil((endDate - new Date()) / (1000 * 60 * 60 * 24));
        const isExpiringSoon = daysRemaining < 60 && daysRemaining > 0;
        const isExpired = daysRemaining <= 0;

        const typeIcons = {
            health: '<path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>',
            life: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>',
            vehicle: '<path d="M5 17h14v2H5v-2zm0-4h14v2H5v-2zm0-4h14v2H5V9z"></path>',
            home: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>',
            travel: '<circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>'
        };

        return `
            <div class="card policy-card ${isExpired ? 'expired' : ''}" data-policy-id="${policy.id}">
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
                        <div class="dropdown">
                            <button class="icon-btn" onclick="togglePolicyMenu('${policy.id}')">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="1"></circle>
                                    <circle cx="12" cy="5" r="1"></circle>
                                    <circle cx="12" cy="19" r="1"></circle>
                                </svg>
                            </button>
                            <div id="menu-${policy.id}" class="dropdown-menu" style="display: none;">
                                <button onclick="editPolicy('${policy.id}')">Edit</button>
                                <button onclick="deletePolicy('${policy.id}')" style="color: var(--danger);">Delete</button>
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
                            <span class="detail-value">${endDate.toLocaleDateString('en-IN')}</span>
                        </div>
                    </div>

                    ${isExpiringSoon ? `
                        <div class="alert alert-warning" style="margin-top: 1rem; padding: 0.5rem; font-size: 0.75rem;">
                            ⚠️ Expires in ${daysRemaining} days
                        </div>
                    ` : ''}
                    ${isExpired ? `
                        <div class="alert alert-danger" style="margin-top: 1rem; padding: 0.5rem; font-size: 0.75rem;">
                            ❌ Policy expired
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

async function loadLatestAssessment(userId) {
    try {
        // Try API first, fallback to localStorage
        try {
            const res = await fetch(`${API_BASE}/insurance/assessment/${userId}/latest`);
            if (res.ok) {
                const assessment = await res.json();
                renderAssessment(assessment);
                return;
            }
        } catch (apiError) {
            console.log('Assessment API not available, using localStorage');
        }
        
        // Fallback to localStorage
        const stored = getStorageData(STORAGE_KEYS.assessments);
        const userAssessments = stored.filter(a => a.user_id === userId);
        if (userAssessments.length > 0) {
            const latest = userAssessments.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0];
            renderAssessment(latest);
        }
    } catch (err) {
        console.error('Error loading assessment:', err);
    }
}

let currentAssessment = null; // Store current assessment for printing

function renderAssessment(assessment) {
    currentAssessment = assessment; // Store for printing
    const content = document.getElementById('assessment-content');
    
    // Show print button
    const printBtn = document.getElementById('btn-print-assessment');
    if (printBtn) printBtn.style.display = 'flex';
    
    const riskColors = {
        low: '#10b981',
        moderate: '#f59e0b',
        high: '#ef4444'
    };

    const riskColor = riskColors[assessment.risk_level] || riskColors.moderate;

    content.innerHTML = `
        <div class="assessment-summary">
            <div style="background: var(--card-bg); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem; border-left: 3px solid var(--primary);">
                <p style="font-size: 0.875rem; color: var(--text-secondary); margin: 0;">
                    <strong>✓ Real Data Calculation</strong><br>
                    Based on: Age ${assessment.age}, ${assessment.dependents} dependents, ₹${assessment.annual_income.toLocaleString('en-IN')} annual income, 
                    ${assessment.health_conditions.length} health condition(s), ${assessment.lifestyle_factors.smoking ? 'Smoker' : 'Non-smoker'}, 
                    ${assessment.lifestyle_factors.city_tier} city
                </p>
            </div>

            <div class="risk-score-circle" style="--risk-color: ${riskColor};">
                <div class="score-value">${assessment.risk_score}</div>
                <div class="score-label">${assessment.risk_level.toUpperCase()} RISK</div>
            </div>

            <div class="coverage-grid">
                <div class="coverage-item">
                    <h4>Life Insurance</h4>
                    <div class="coverage-bar">
                        <div class="coverage-progress" style="width: ${Math.min(100, (assessment.current_life_coverage / assessment.recommended_life_coverage) * 100)}%"></div>
                    </div>
                    <p class="coverage-text">
                        Current: ₹${assessment.current_life_coverage.toLocaleString('en-IN')}<br>
                        Recommended: ₹${assessment.recommended_life_coverage.toLocaleString('en-IN')}
                    </p>
                    ${assessment.coverage_gap_life > 0 ? `
                        <p class="gap-text">Gap: ₹${assessment.coverage_gap_life.toLocaleString('en-IN')}</p>
                    ` : '<p class="gap-text" style="color: var(--success);">✓ Adequate coverage</p>'}
                </div>

                <div class="coverage-item">
                    <h4>Health Insurance</h4>
                    <div class="coverage-bar">
                        <div class="coverage-progress" style="width: ${Math.min(100, (assessment.current_health_coverage / assessment.recommended_health_coverage) * 100)}%"></div>
                    </div>
                    <p class="coverage-text">
                        Current: ₹${assessment.current_health_coverage.toLocaleString('en-IN')}<br>
                        Recommended: ₹${assessment.recommended_health_coverage.toLocaleString('en-IN')}
                    </p>
                    ${assessment.coverage_gap_health > 0 ? `
                        <p class="gap-text">Gap: ₹${assessment.coverage_gap_health.toLocaleString('en-IN')}</p>
                    ` : '<p class="gap-text" style="color: var(--success);">✓ Adequate coverage</p>'}
                </div>
            </div>

            <div class="recommendations">
                <h4>Personalized Recommendations</h4>
                <ul>
                    ${assessment.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>

            <p style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 1rem;">
                Last updated: ${new Date(assessment.updated_at).toLocaleDateString('en-IN')} • 
                Calculated using industry-standard formulas based on your profile
            </p>
        </div>
    `;
}

function openPolicyModal(policyId = null) {
    const modal = document.getElementById('policy-modal');
    const form = document.getElementById('policy-form');
    form.reset();

    if (policyId) {
        const policy = allPolicies.find(p => p.id === policyId);
        if (policy) {
            document.getElementById('modal-title').textContent = 'Edit Insurance Policy';
            document.getElementById('policy-id').value = policy.id;
            document.getElementById('policy-type').value = policy.policy_type;
            document.getElementById('provider').value = policy.provider;
            document.getElementById('policy-number').value = policy.policy_number;
            document.getElementById('coverage-amount').value = policy.coverage_amount;
            document.getElementById('premium-amount').value = policy.premium_amount;
            document.getElementById('premium-frequency').value = policy.premium_frequency;
            document.getElementById('start-date').value = policy.start_date.split('T')[0];
            document.getElementById('end-date').value = policy.end_date.split('T')[0];
            document.getElementById('notes').value = policy.notes;
        }
    } else {
        document.getElementById('modal-title').textContent = 'Add Insurance Policy';
    }

    modal.style.display = 'flex';
}

async function savePolicyForm(userId) {
    const policyId = document.getElementById('policy-id').value;
    const data = {
        id: policyId || generateId(),
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
        created_at: policyId ? undefined : new Date().toISOString(),
        updated_at: new Date().toISOString()
    };

    try {
        // Try API first, fallback to localStorage
        try {
            const url = policyId 
                ? `${API_BASE}/insurance/policies/${policyId}`
                : `${API_BASE}/insurance/policies`;
            
            const res = await fetch(url, {
                method: policyId ? 'PUT' : 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (res.ok) {
                document.getElementById('policy-modal').style.display = 'none';
                await loadPolicies(userId);
                showToast(policyId ? 'Policy updated successfully' : 'Policy added successfully', 'success');
                return;
            }
        } catch (apiError) {
            console.log('API not available, using localStorage');
        }

        // Fallback to localStorage
        const stored = getStorageData(STORAGE_KEYS.policies);
        if (policyId) {
            const index = stored.findIndex(p => p.id === policyId);
            if (index >= 0) stored[index] = data;
        } else {
            stored.push(data);
        }
        setStorageData(STORAGE_KEYS.policies, stored);

        document.getElementById('policy-modal').style.display = 'none';
        await loadPolicies(userId);
        showToast(policyId ? 'Policy updated successfully' : 'Policy added successfully', 'success');
    } catch (err) {
        console.error('Error saving policy:', err);
        showToast('Failed to save policy', 'error');
    }
}

function generateId() {
    return 'policy_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function openAssessmentModal() {
    const { user } = authState.get();
    const modal = document.getElementById('assessment-modal');
    
    // Pre-fill with user data
    document.getElementById('annual-income').value = user.income * 12 || '';
    
    modal.style.display = 'flex';
}

async function runAssessment(userId) {
    const healthConditionsStr = document.getElementById('health-conditions').value;
    const healthConditions = healthConditionsStr 
        ? healthConditionsStr.split(',').map(s => s.trim()).filter(Boolean)
        : [];

    // Only send fields expected by the API schema
    const assessmentData = {
        user_id: userId,
        age: parseInt(document.getElementById('age').value),
        dependents: parseInt(document.getElementById('dependents').value),
        annual_income: parseFloat(document.getElementById('annual-income').value),
        monthly_expenses: parseFloat(document.getElementById('monthly-expenses').value),
        existing_loans: parseFloat(document.getElementById('existing-loans').value) || 0,
        health_conditions: healthConditions,
        lifestyle_factors: {
            smoking: document.getElementById('smoking').checked,
            city_tier: document.getElementById('city-tier').value
        }
    };

    console.log('Submitting assessment:', assessmentData);

    try {
        // Try API first
        console.log('Calling API:', `${API_BASE}/insurance/assessment`);
        const res = await fetch(`${API_BASE}/insurance/assessment`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(assessmentData)
        });

        console.log('API Response status:', res.status);

        if (res.ok) {
            const assessment = await res.json();
            console.log('Assessment saved successfully:', assessment);
            document.getElementById('assessment-modal').style.display = 'none';
            renderAssessment(assessment);
            showToast('✅ Assessment saved to database!', 'success');
            return;
        } else {
            const error = await res.json();
            console.error('API error response:', error);
            throw new Error(error.detail || 'Failed to save assessment');
        }
    } catch (apiError) {
        console.error('Error saving assessment to API:', apiError);
        
        // Fallback to localStorage
        console.log('Falling back to localStorage');
        const calculated = calculateInsuranceNeeds(assessmentData);
        const localData = {
            id: 'assessment_' + Date.now(),
            ...assessmentData,
            ...calculated,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        };
        
        const stored = getStorageData(STORAGE_KEYS.assessments);
        stored.push(localData);
        setStorageData(STORAGE_KEYS.assessments, stored);

        document.getElementById('assessment-modal').style.display = 'none';
        renderAssessment(localData);
        showToast('⚠️ Assessment saved locally (API unavailable)', 'warning');
    }
}

function calculateInsuranceNeeds(assessmentData) {
    // Life Insurance Calculation
    const baseLifeCoverage = assessmentData.annual_income * 12; // 12x annual income
    let lifeCoverage = baseLifeCoverage + assessmentData.existing_loans;
    lifeCoverage += assessmentData.dependents * 500000; // 5 lakh per dependent
    
    // Age adjustment
    let ageFactor = 1.0;
    if (assessmentData.age > 50) ageFactor = 0.7;
    else if (assessmentData.age > 40) ageFactor = 0.85;
    else if (assessmentData.age < 30) ageFactor = 1.2;
    
    lifeCoverage *= ageFactor;
    
    // Health Insurance Calculation
    let baseHealthCoverage = 500000; // 5 lakh base
    
    if (assessmentData.age > 30) {
        baseHealthCoverage += (assessmentData.age - 30) * 50000;
    }
    
    baseHealthCoverage += assessmentData.dependents * 300000;
    baseHealthCoverage += assessmentData.health_conditions.length * 200000;
    
    if (assessmentData.lifestyle_factors.smoking) {
        baseHealthCoverage *= 1.3;
    }
    if (assessmentData.lifestyle_factors.city_tier === "metro") {
        baseHealthCoverage *= 1.5;
    }
    
    // Get current coverage from policies
    const currentPolicies = allPolicies.filter(p => p.status === 'active');
    const currentLife = currentPolicies
        .filter(p => p.policy_type === 'life')
        .reduce((sum, p) => sum + p.coverage_amount, 0);
    const currentHealth = currentPolicies
        .filter(p => p.policy_type === 'health')
        .reduce((sum, p) => sum + p.coverage_amount, 0);
    
    const lifeGap = Math.max(0, lifeCoverage - currentLife);
    const healthGap = Math.max(0, baseHealthCoverage - currentHealth);
    
    // Risk scoring
    let riskScore = 50;
    if (lifeGap > lifeCoverage * 0.5) riskScore += 20;
    else if (lifeGap > lifeCoverage * 0.25) riskScore += 10;
    
    if (healthGap > baseHealthCoverage * 0.5) riskScore += 20;
    else if (healthGap > baseHealthCoverage * 0.25) riskScore += 10;
    
    riskScore += Math.min(20, assessmentData.health_conditions.length * 5);
    
    if (assessmentData.dependents > 0 && currentLife < assessmentData.annual_income * 5) {
        riskScore += 15;
    }
    
    riskScore = Math.min(100, riskScore);
    
    const riskLevel = riskScore < 40 ? "low" : riskScore < 70 ? "moderate" : "high";
    
    // Generate recommendations
    const recommendations = [];
    
    if (lifeGap > 0) {
        recommendations.push(`Increase life insurance coverage by ₹${lifeGap.toLocaleString('en-IN')} to adequately protect your dependents.`);
    } else {
        recommendations.push("Your life insurance coverage is adequate for your current needs.");
    }
    
    if (healthGap > 0) {
        recommendations.push(`Increase health insurance coverage by ₹${healthGap.toLocaleString('en-IN')} to cover potential medical expenses.`);
    } else {
        recommendations.push("Your health insurance coverage meets recommended levels.");
    }
    
    if (assessmentData.dependents > 0 && currentLife === 0) {
        recommendations.push("Critical: You have dependents but no life insurance. Consider getting term insurance immediately.");
    }
    
    if (assessmentData.health_conditions.length > 0 && currentHealth < 500000) {
        recommendations.push("With existing health conditions, consider increasing health coverage to at least ₹5 lakhs.");
    }
    
    if (assessmentData.age > 45 && currentHealth < 1000000) {
        recommendations.push("At your age, medical expenses tend to increase. Consider coverage of at least ₹10 lakhs.");
    }
    
    return {
        recommended_life_coverage: Math.round(lifeCoverage),
        recommended_health_coverage: Math.round(baseHealthCoverage),
        current_life_coverage: currentLife,
        current_health_coverage: currentHealth,
        coverage_gap_life: Math.round(lifeGap),
        coverage_gap_health: Math.round(healthGap),
        risk_score: riskScore,
        risk_level: riskLevel,
        recommendations: recommendations
    };
}

window.togglePolicyMenu = function(policyId) {
    const menu = document.getElementById(`menu-${policyId}`);
    document.querySelectorAll('.dropdown-menu').forEach(m => {
        if (m.id !== `menu-${policyId}`) m.style.display = 'none';
    });
    menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
};

window.editPolicy = function(policyId) {
    openPolicyModal(policyId);
};

window.deletePolicy = async function(policyId) {
    if (!confirm('Are you sure you want to delete this policy?')) return;

    try {
        // Try API first, fallback to localStorage
        try {
            const res = await fetch(`${API_BASE}/insurance/policies/${policyId}`, {
                method: 'DELETE'
            });

            if (res.ok) {
                const { user } = authState.get();
                await loadPolicies(user.id);
                showToast('Policy deleted successfully', 'success');
                return;
            }
        } catch (apiError) {
            console.log('API not available, using localStorage');
        }

        // Fallback to localStorage
        const stored = getStorageData(STORAGE_KEYS.policies);
        const filtered = stored.filter(p => p.id !== policyId);
        setStorageData(STORAGE_KEYS.policies, filtered);

        const { user } = authState.get();
        await loadPolicies(user.id);
        showToast('Policy deleted successfully', 'success');
    } catch (err) {
        console.error('Error deleting policy:', err);
        showToast('Failed to delete policy', 'error');
    }
};

function showToast(message, type = 'info') {
    // Simple toast notification
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

function printAssessmentReport() {
    if (!currentAssessment) {
        showToast('No assessment data available', 'error');
        return;
    }

    const { user } = authState.get();
    const assessment = currentAssessment;
    
    // Create print window content
    const printContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Insurance Assessment Report</title>
            <style>
                @media print {
                    @page { margin: 1cm; }
                    body { margin: 0; }
                }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    text-align: center;
                    border-bottom: 3px solid #3b82f6;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }
                .header h1 {
                    margin: 0;
                    color: #1e40af;
                    font-size: 28px;
                }
                .header p {
                    margin: 5px 0;
                    color: #666;
                }
                .section {
                    margin-bottom: 30px;
                    page-break-inside: avoid;
                }
                .section h2 {
                    color: #1e40af;
                    border-bottom: 2px solid #e5e7eb;
                    padding-bottom: 10px;
                    margin-bottom: 15px;
                }
                .info-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-bottom: 20px;
                }
                .info-item {
                    padding: 10px;
                    background: #f9fafb;
                    border-radius: 5px;
                }
                .info-item label {
                    font-weight: 600;
                    color: #4b5563;
                    display: block;
                    margin-bottom: 5px;
                }
                .info-item value {
                    color: #111827;
                    font-size: 16px;
                }
                .risk-score {
                    text-align: center;
                    padding: 20px;
                    background: ${assessment.risk_level === 'low' ? '#d1fae5' : assessment.risk_level === 'moderate' ? '#fef3c7' : '#fee2e2'};
                    border-radius: 10px;
                    margin: 20px 0;
                }
                .risk-score .score {
                    font-size: 48px;
                    font-weight: bold;
                    color: ${assessment.risk_level === 'low' ? '#059669' : assessment.risk_level === 'moderate' ? '#d97706' : '#dc2626'};
                }
                .risk-score .label {
                    font-size: 18px;
                    font-weight: 600;
                    color: #374151;
                    text-transform: uppercase;
                }
                .coverage-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }
                .coverage-table th,
                .coverage-table td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #e5e7eb;
                }
                .coverage-table th {
                    background: #f3f4f6;
                    font-weight: 600;
                    color: #374151;
                }
                .coverage-table .amount {
                    font-weight: 600;
                    color: #1e40af;
                }
                .coverage-table .gap {
                    color: #dc2626;
                    font-weight: 600;
                }
                .coverage-table .adequate {
                    color: #059669;
                    font-weight: 600;
                }
                .recommendations {
                    background: #eff6ff;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 4px solid #3b82f6;
                }
                .recommendations h3 {
                    margin-top: 0;
                    color: #1e40af;
                }
                .recommendations ul {
                    margin: 10px 0;
                    padding-left: 20px;
                }
                .recommendations li {
                    margin-bottom: 10px;
                }
                .footer {
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 2px solid #e5e7eb;
                    text-align: center;
                    color: #6b7280;
                    font-size: 12px;
                }
                .disclaimer {
                    background: #fef3c7;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    border-left: 4px solid #f59e0b;
                }
                .disclaimer p {
                    margin: 0;
                    font-size: 13px;
                    color: #92400e;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Insurance Risk Assessment Report</h1>
                <p>Generated on ${new Date().toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
                <p>User: ${user?.name || 'N/A'}</p>
            </div>

            <div class="section">
                <h2>Personal Information</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <label>Age</label>
                        <value>${assessment.age} years</value>
                    </div>
                    <div class="info-item">
                        <label>Number of Dependents</label>
                        <value>${assessment.dependents}</value>
                    </div>
                    <div class="info-item">
                        <label>Annual Income</label>
                        <value>₹${assessment.annual_income.toLocaleString('en-IN')}</value>
                    </div>
                    <div class="info-item">
                        <label>Monthly Expenses</label>
                        <value>₹${assessment.monthly_expenses.toLocaleString('en-IN')}</value>
                    </div>
                    <div class="info-item">
                        <label>Existing Loans</label>
                        <value>₹${assessment.existing_loans.toLocaleString('en-IN')}</value>
                    </div>
                    <div class="info-item">
                        <label>City Tier</label>
                        <value>${assessment.lifestyle_factors.city_tier.charAt(0).toUpperCase() + assessment.lifestyle_factors.city_tier.slice(1)}</value>
                    </div>
                </div>
                ${assessment.health_conditions.length > 0 ? `
                    <div class="info-item" style="margin-top: 10px;">
                        <label>Health Conditions</label>
                        <value>${assessment.health_conditions.join(', ')}</value>
                    </div>
                ` : ''}
                ${assessment.lifestyle_factors.smoking ? `
                    <div class="info-item" style="margin-top: 10px; background: #fee2e2;">
                        <label>Lifestyle Factor</label>
                        <value>Smoker</value>
                    </div>
                ` : ''}
            </div>

            <div class="section">
                <h2>Risk Assessment</h2>
                <div class="risk-score">
                    <div class="score">${assessment.risk_score}</div>
                    <div class="label">${assessment.risk_level} Risk</div>
                </div>
            </div>

            <div class="section">
                <h2>Coverage Analysis</h2>
                <table class="coverage-table">
                    <thead>
                        <tr>
                            <th>Insurance Type</th>
                            <th>Current Coverage</th>
                            <th>Recommended Coverage</th>
                            <th>Gap</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Life Insurance</strong></td>
                            <td class="amount">₹${assessment.current_life_coverage.toLocaleString('en-IN')}</td>
                            <td class="amount">₹${assessment.recommended_life_coverage.toLocaleString('en-IN')}</td>
                            <td class="${assessment.coverage_gap_life > 0 ? 'gap' : 'adequate'}">
                                ${assessment.coverage_gap_life > 0 
                                    ? '₹' + assessment.coverage_gap_life.toLocaleString('en-IN') 
                                    : '✓ Adequate'}
                            </td>
                        </tr>
                        <tr>
                            <td><strong>Health Insurance</strong></td>
                            <td class="amount">₹${assessment.current_health_coverage.toLocaleString('en-IN')}</td>
                            <td class="amount">₹${assessment.recommended_health_coverage.toLocaleString('en-IN')}</td>
                            <td class="${assessment.coverage_gap_health > 0 ? 'gap' : 'adequate'}">
                                ${assessment.coverage_gap_health > 0 
                                    ? '₹' + assessment.coverage_gap_health.toLocaleString('en-IN') 
                                    : '✓ Adequate'}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="section">
                <div class="recommendations">
                    <h3>Personalized Recommendations</h3>
                    <ul>
                        ${assessment.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>

            <div class="section">
                <h2>Estimated Premium Budget</h2>
                <div class="info-item">
                    <label>Recommended Annual Premium Budget</label>
                    <value>₹${Math.round(assessment.annual_income * 0.12).toLocaleString('en-IN')} (12% of annual income)</value>
                </div>
                <p style="margin-top: 15px; color: #6b7280; font-size: 14px;">
                    This is a general guideline. Actual premiums will vary based on policy type, coverage amount, 
                    age, health conditions, and insurance provider.
                </p>
            </div>

            <div class="disclaimer">
                <p><strong>Disclaimer:</strong> This assessment is for informational purposes only and should not be considered as financial or insurance advice. 
                Please consult with a certified insurance advisor or financial planner before making any insurance decisions. 
                Coverage recommendations are based on industry standards and may not reflect your specific needs.</p>
            </div>

            <div class="footer">
                <p>FinA - Personal Finance Advisor</p>
                <p>Report generated on ${new Date().toLocaleString('en-IN')}</p>
                <p>This is a computer-generated report and does not require a signature.</p>
            </div>
        </body>
        </html>
    `;

    // Open print window
    const printWindow = window.open('', '_blank', 'width=800,height=600');
    if (printWindow) {
        printWindow.document.write(printContent);
        printWindow.document.close();
        
        // Wait for content to load, then print
        printWindow.onload = function() {
            printWindow.focus();
            printWindow.print();
        };
    } else {
        showToast('Please allow popups to print the report', 'error');
    }
}
