import { authState } from '../auth.js';
import { API_URL, apiFetch, showConfirm } from '../utils.js';

// VERSION CHECK - Beautiful Insurance UI v31
console.log('🎨 Insurance View v31 loaded - BEAUTIFUL UI with full calculator');

export default async function renderInsurance() {
    const { user } = authState.get();
    if (!user) return '<div>Please log in</div>';

    // Initialize the page
    setTimeout(() => {
        initInsurancePage();
    }, 100);

    return `
        <div class="insurance-container">
            <!-- Header Section -->
            <div class="insurance-header">
                <div class="header-content">
                    <div class="header-text">
                        <h1 class="insurance-title">Insurance Management</h1>
                        <p class="insurance-subtitle">Comprehensive insurance planning and policy management for your financial security</p>
                    </div>
                    <div class="header-actions">
                        <button id="btn-load-demo" class="btn btn-secondary">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                <polyline points="14,2 14,8 20,8"></polyline>
                            </svg>
                            Load Demo Data
                        </button>
                        <button id="btn-add-policy" class="btn btn-primary">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="12" y1="5" x2="12" y2="19"></line>
                                <line x1="5" y1="12" x2="19" y2="12"></line>
                            </svg>
                            Add New Policy
                        </button>
                    </div>
                </div>
            </div>

            <!-- Insurance Education Section -->
            <div class="insurance-education">
                <div class="education-grid">
                    <div class="education-card">
                        <div class="education-icon health">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                            </svg>
                        </div>
                        <h3>Health Insurance</h3>
                        <p>Covers medical expenses, hospitalization, and treatments. Recommended: ₹5-10 lakhs minimum coverage.</p>
                    </div>
                    <div class="education-card">
                        <div class="education-icon life">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                            </svg>
                        </div>
                        <h3>Life Insurance</h3>
                        <p>Financial protection for your family. Recommended: 10-15 times your annual income for adequate coverage.</p>
                    </div>
                    <div class="education-card">
                        <div class="education-icon vehicle">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M7 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"></path>
                                <path d="M17 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"></path>
                                <path d="M5 17h-2v-6l2-5h9l4 5h1a2 2 0 0 1 2 2v4h-2"></path>
                            </svg>
                        </div>
                        <h3>Vehicle Insurance</h3>
                        <p>Mandatory for all vehicles. Comprehensive coverage protects against accidents, theft, and natural disasters.</p>
                    </div>
                </div>
            </div>

            <!-- Insurance Calculator Section -->
            <div class="calculator-section">
                <div class="calculator-header">
                    <h2>Insurance Needs Calculator</h2>
                    <p>Get personalized insurance recommendations based on your financial profile and life situation</p>
                </div>
                <div class="calculator-form">
                    <div class="form-section">
                        <h3 class="section-title">Personal Information</h3>
                        <div class="form-grid">
                            <div class="form-group">
                                <label class="form-label">Age</label>
                                <input type="number" id="calc-age" class="form-input" placeholder="Your current age" min="18" max="80" value="30">
                                <small class="form-help">Age affects insurance premiums and coverage needs</small>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Gender</label>
                                <select id="calc-gender" class="form-input">
                                    <option value="male">Male</option>
                                    <option value="female">Female</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Marital Status</label>
                                <select id="calc-marital" class="form-input">
                                    <option value="single">Single</option>
                                    <option value="married">Married</option>
                                    <option value="divorced">Divorced</option>
                                    <option value="widowed">Widowed</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Number of Dependents</label>
                                <input type="number" id="calc-dependents" class="form-input" placeholder="Children, parents, etc." min="0" max="10" value="0">
                                <small class="form-help">Include children, elderly parents, or other dependents</small>
                            </div>
                        </div>
                    </div>

                    <div class="form-section">
                        <h3 class="section-title">Financial Information</h3>
                        <div class="form-grid">
                            <div class="form-group">
                                <label class="form-label">Annual Income (₹)</label>
                                <input type="number" id="calc-income" class="form-input" placeholder="Your yearly income" min="0" value="${user.income || ''}">
                                <small class="form-help">Include salary, business income, and other sources</small>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Monthly Expenses (₹)</label>
                                <input type="number" id="calc-expenses" class="form-input" placeholder="Monthly household expenses" min="0">
                                <small class="form-help">Include rent, utilities, food, and other regular expenses</small>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Existing Loans (₹)</label>
                                <input type="number" id="calc-debt" class="form-input" placeholder="Home loan, car loan, etc." min="0" value="0">
                                <small class="form-help">Outstanding amount on all loans</small>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Current Savings (₹)</label>
                                <input type="number" id="calc-savings" class="form-input" placeholder="Emergency fund, investments" min="0">
                                <small class="form-help">Liquid savings and investments</small>
                            </div>
                        </div>
                    </div>

                    <div class="form-section">
                        <h3 class="section-title">Lifestyle & Health</h3>
                        <div class="form-grid">
                            <div class="form-group">
                                <label class="form-label">Smoking Status</label>
                                <select id="calc-smoking" class="form-input">
                                    <option value="never">Never smoked</option>
                                    <option value="former">Former smoker</option>
                                    <option value="current">Current smoker</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Exercise Frequency</label>
                                <select id="calc-exercise" class="form-input">
                                    <option value="regular">Regular (3+ times/week)</option>
                                    <option value="moderate">Moderate (1-2 times/week)</option>
                                    <option value="minimal">Minimal exercise</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">City Type</label>
                                <select id="calc-city" class="form-input">
                                    <option value="metro">Metro (Mumbai, Delhi, Bangalore)</option>
                                    <option value="tier1">Tier 1 (Pune, Hyderabad, Chennai)</option>
                                    <option value="tier2">Tier 2 (Indore, Kochi, Jaipur)</option>
                                    <option value="tier3">Tier 3 & smaller cities</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Occupation Risk</label>
                                <select id="calc-occupation" class="form-input">
                                    <option value="low">Low risk (Office job, IT, Finance)</option>
                                    <option value="medium">Medium risk (Sales, Travel)</option>
                                    <option value="high">High risk (Construction, Mining)</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="form-section">
                        <h3 class="section-title">Health Conditions</h3>
                        <div class="health-conditions">
                            <label class="checkbox-group">
                                <input type="checkbox" id="condition-diabetes" value="diabetes">
                                <span class="checkmark"></span>
                                Diabetes
                            </label>
                            <label class="checkbox-group">
                                <input type="checkbox" id="condition-hypertension" value="hypertension">
                                <span class="checkmark"></span>
                                High Blood Pressure
                            </label>
                            <label class="checkbox-group">
                                <input type="checkbox" id="condition-heart" value="heart">
                                <span class="checkmark"></span>
                                Heart Disease
                            </label>
                            <label class="checkbox-group">
                                <input type="checkbox" id="condition-asthma" value="asthma">
                                <span class="checkmark"></span>
                                Asthma
                            </label>
                            <label class="checkbox-group">
                                <input type="checkbox" id="condition-cancer" value="cancer">
                                <span class="checkmark"></span>
                                Cancer History
                            </label>
                            <label class="checkbox-group">
                                <input type="checkbox" id="condition-none" value="none">
                                <span class="checkmark"></span>
                                No major health conditions
                            </label>
                        </div>
                    </div>

                    <div class="calculator-actions">
                        <button id="btn-calculate-coverage" class="btn btn-primary btn-large">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M9 11H5a2 2 0 0 0-2 2v3c0 1.1.9 2 2 2h4m6-6h4a2 2 0 0 1 2 2v3c0 1.1-.9 2-2 2h-4m-6 0V9a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2z"></path>
                            </svg>
                            Calculate My Insurance Needs
                        </button>
                        <button id="btn-reset-calculator" class="btn btn-secondary">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 12a9 9 0 11-6.219-8.56"></path>
                            </svg>
                            Reset Form
                        </button>
                    </div>
                </div>

                <div id="coverage-results" class="coverage-results" style="display: none;"></div>
            </div>

            <!-- Current Policies Section -->
            <div class="policies-section">
                <div class="policies-header">
                    <h2>Your Insurance Policies</h2>
                    <p>Manage and track all your insurance policies in one place</p>
                    <button id="btn-refresh-policies" class="btn btn-secondary btn-sm">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 12a9 9 0 11-6.219-8.56"></path>
                        </svg>
                        Refresh
                    </button>
                </div>
                <div id="policies-container" class="policies-container">
                    <div class="empty-state">
                        <div class="empty-icon">
                            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                            </svg>
                        </div>
                        <h3>No Insurance Policies Found</h3>
                        <p>Start by adding your first insurance policy or load demo data to explore the features</p>
                        <div class="empty-actions">
                            <button onclick="document.getElementById('btn-add-policy').click()" class="btn btn-primary">Add Your First Policy</button>
                            <button onclick="document.getElementById('btn-load-demo').click()" class="btn btn-secondary">Load Demo Data</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <!-- Add Policy Modal -->
        <div id="add-policy-modal" class="modal" style="display: none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Add New Insurance Policy</h3>
                    <button id="close-policy-modal" class="btn-close">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="add-policy-form">
                        <div class="form-grid" style="gap: 0.75rem;">
                            <div class="form-group" style="margin-bottom: 0.75rem;">
                                <label class="form-label">Policy Type *</label>
                                <select id="policy-type" name="policy-type" class="form-input" required>
                                    <option value="">Select policy type</option>
                                    <option value="health">Health Insurance</option>
                                    <option value="life">Life Insurance</option>
                                    <option value="vehicle">Vehicle Insurance</option>
                                    <option value="home">Home Insurance</option>
                                    <option value="travel">Travel Insurance</option>
                                </select>
                            </div>
                            <div class="form-group" style="margin-bottom: 0.75rem;">
                                <label class="form-label">Insurance Provider *</label>
                                <input type="text" id="policy-provider" name="policy-provider" class="form-input" placeholder="e.g., HDFC ERGO, LIC, Star Health" required>
                            </div>
                        </div>
                        <div class="form-grid" style="gap: 0.75rem;">
                            <div class="form-group" style="margin-bottom: 0.75rem;">
                                <label class="form-label">Policy Number *</label>
                                <input type="text" id="policy-number" name="policy-number" class="form-input" placeholder="Policy number from your documents" required>
                            </div>
                            <div class="form-group" style="margin-bottom: 0.75rem;">
                                <label class="form-label">Coverage Amount (₹) *</label>
                                <input type="number" id="policy-coverage" name="policy-coverage" class="form-input" placeholder="Total coverage amount" min="0" required>
                            </div>
                        </div>
                        <div class="form-grid" style="gap: 0.75rem;">
                            <div class="form-group" style="margin-bottom: 0.75rem;">
                                <label class="form-label">Premium Amount (₹) *</label>
                                <input type="number" id="policy-premium" name="policy-premium" class="form-input" placeholder="Premium amount" min="0" required>
                            </div>
                            <div class="form-group" style="margin-bottom: 0.75rem;">
                                <label class="form-label">Premium Frequency</label>
                                <select id="policy-frequency" name="policy-frequency" class="form-input">
                                    <option value="annual">Annual</option>
                                    <option value="monthly">Monthly</option>
                                    <option value="quarterly">Quarterly</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-grid" style="gap: 0.75rem;">
                            <div class="form-group" style="margin-bottom: 0.75rem;">
                                <label class="form-label">Policy Start Date *</label>
                                <input type="date" id="policy-start" name="policy-start" class="form-input" required>
                            </div>
                            <div class="form-group" style="margin-bottom: 0.75rem;">
                                <label class="form-label">Policy End Date *</label>
                                <input type="date" id="policy-end" name="policy-end" class="form-input" required>
                            </div>
                        </div>
                        <div class="form-group" style="margin-bottom: 0.75rem;">
                            <label class="form-label">Additional Notes</label>
                            <textarea id="policy-notes" name="policy-notes" class="form-input" rows="2" placeholder="Any additional information about this policy (optional)"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" id="cancel-policy" class="btn btn-secondary">Cancel</button>
                    <button type="submit" form="add-policy-form" class="btn btn-primary">Add Policy</button>
                </div>
            </div>
        </div>
    `;
}

function initInsurancePage() {
    const { user } = authState.get();
    if (!user) return;

    // Load existing policies
    loadPolicies();

    // Event listeners
    document.getElementById('btn-calculate-coverage')?.addEventListener('click', calculateCoverage);
    document.getElementById('btn-reset-calculator')?.addEventListener('click', resetCalculator);
    document.getElementById('btn-load-demo')?.addEventListener('click', loadDemoData);
    document.getElementById('btn-add-policy')?.addEventListener('click', showAddPolicyModal);
    document.getElementById('btn-refresh-policies')?.addEventListener('click', loadPolicies);
    
    // Modal events
    document.getElementById('close-policy-modal')?.addEventListener('click', hideAddPolicyModal);
    document.getElementById('cancel-policy')?.addEventListener('click', hideAddPolicyModal);
    document.getElementById('add-policy-form')?.addEventListener('submit', handleAddPolicy);
    
    // Health condition checkboxes
    document.getElementById('condition-none')?.addEventListener('change', function() {
        if (this.checked) {
            document.querySelectorAll('input[type="checkbox"][id^="condition-"]:not(#condition-none)').forEach(cb => {
                cb.checked = false;
            });
        }
    });
    
    document.querySelectorAll('input[type="checkbox"][id^="condition-"]:not(#condition-none)').forEach(cb => {
        cb.addEventListener('change', function() {
            if (this.checked) {
                document.getElementById('condition-none').checked = false;
            }
        });
    });
    
    // Close modal on outside click
    document.getElementById('add-policy-modal')?.addEventListener('click', (e) => {
        if (e.target.id === 'add-policy-modal') {
            hideAddPolicyModal();
        }
    });
}

async function calculateCoverage() {
    // Get form values
    const age = parseInt(document.getElementById('calc-age').value) || 30;
    const gender = document.getElementById('calc-gender').value;
    const maritalStatus = document.getElementById('calc-marital').value;
    const dependents = parseInt(document.getElementById('calc-dependents').value) || 0;
    const income = parseFloat(document.getElementById('calc-income').value) || 0;
    const expenses = parseFloat(document.getElementById('calc-expenses').value) || 0;
    const debt = parseFloat(document.getElementById('calc-debt').value) || 0;
    const savings = parseFloat(document.getElementById('calc-savings').value) || 0;
    const smoking = document.getElementById('calc-smoking').value;
    const exercise = document.getElementById('calc-exercise').value;
    const cityType = document.getElementById('calc-city').value;
    const occupationRisk = document.getElementById('calc-occupation').value;

    // Get health conditions
    const healthConditions = [];
    document.querySelectorAll('input[type="checkbox"][id^="condition-"]:checked').forEach(cb => {
        if (cb.value !== 'none') {
            healthConditions.push(cb.value);
        }
    });

    if (income <= 0) {
        showToast('Please enter a valid annual income', 'error');
        return;
    }

    // Show loading
    const resultsDiv = document.getElementById('coverage-results');
    resultsDiv.innerHTML = `
        <div class="loading-state">
            <div class="loading-spinner"></div>
            <p>Calculating your personalized insurance recommendations...</p>
        </div>
    `;
    resultsDiv.style.display = 'block';

    // Simulate calculation delay for better UX
    setTimeout(() => {
        const results = performInsuranceCalculation({
            age, gender, maritalStatus, dependents, income, expenses, debt, savings,
            smoking, exercise, cityType, occupationRisk, healthConditions
        });
        
        displayCalculationResults(results);
    }, 2000);
}

function performInsuranceCalculation(data) {
    const { age, dependents, income, expenses, debt, savings, smoking, cityType, healthConditions } = data;
    
    // Life Insurance Calculation
    let lifeInsurance = income * 10; // Base: 10x annual income
    lifeInsurance += debt; // Add outstanding debt
    lifeInsurance += dependents * 500000; // 5 lakh per dependent
    
    // Age adjustment
    if (age > 50) lifeInsurance *= 0.8;
    else if (age < 30) lifeInsurance *= 1.2;
    
    // Dependent adjustment
    if (dependents > 2) lifeInsurance *= 1.3;
    
    // Health Insurance Calculation
    let healthInsurance = 500000; // Base 5 lakh
    
    // Age factor
    if (age > 45) healthInsurance += 500000;
    else if (age > 35) healthInsurance += 300000;
    
    // City factor
    const cityMultiplier = {
        'metro': 1.8,
        'tier1': 1.5,
        'tier2': 1.2,
        'tier3': 1.0
    };
    healthInsurance *= cityMultiplier[cityType] || 1.0;
    
    // Dependents
    healthInsurance += dependents * 200000;
    
    // Health conditions
    healthInsurance += healthConditions.length * 300000;
    
    // Smoking penalty
    if (smoking === 'current') {
        healthInsurance *= 1.5;
        lifeInsurance *= 1.3;
    }
    
    // Vehicle Insurance (if applicable)
    const vehicleInsurance = income > 500000 ? 50000 : 25000;
    
    // Home Insurance
    const homeInsurance = Math.max(1000000, income * 0.5);
    
    // Calculate risk score
    let riskScore = 30; // Base score
    
    if (age > 45) riskScore += 15;
    if (smoking === 'current') riskScore += 20;
    if (healthConditions.length > 0) riskScore += healthConditions.length * 10;
    if (dependents > 0 && lifeInsurance < income * 5) riskScore += 20;
    if (debt > income) riskScore += 15;
    
    riskScore = Math.min(100, riskScore);
    
    const riskLevel = riskScore < 40 ? 'Low' : riskScore < 70 ? 'Moderate' : 'High';
    
    return {
        lifeInsurance: Math.round(lifeInsurance),
        healthInsurance: Math.round(healthInsurance),
        vehicleInsurance,
        homeInsurance: Math.round(homeInsurance),
        riskScore,
        riskLevel,
        monthlyPremiumEstimate: Math.round((lifeInsurance * 0.01 + healthInsurance * 0.04) / 12),
        recommendations: generateRecommendations(data, { lifeInsurance, healthInsurance, riskScore })
    };
}
function generateRecommendations(data, results) {
    const recommendations = [];
    const { age, dependents, income, healthConditions, smoking } = data;
    const { lifeInsurance, healthInsurance, riskScore } = results;
    
    // Life insurance recommendations
    if (dependents > 0) {
        recommendations.push({
            type: 'critical',
            title: 'Life Insurance Priority',
            message: `With ${dependents} dependent(s), life insurance is crucial. Consider term insurance for maximum coverage at low cost.`
        });
    }
    
    // Health insurance recommendations
    if (age > 40 || healthConditions.length > 0) {
        recommendations.push({
            type: 'important',
            title: 'Health Insurance Focus',
            message: 'Given your age/health profile, prioritize comprehensive health coverage with good hospital network.'
        });
    }
    
    // Smoking recommendations
    if (smoking === 'current') {
        recommendations.push({
            type: 'warning',
            title: 'Smoking Impact',
            message: 'Smoking significantly increases premiums. Consider quitting to reduce insurance costs and health risks.'
        });
    }
    
    // Income-based recommendations
    if (income > 1000000) {
        recommendations.push({
            type: 'info',
            title: 'Tax Benefits',
            message: 'Maximize tax deductions under Section 80C (life insurance) and 80D (health insurance).'
        });
    }
    
    return recommendations;
}

function displayCalculationResults(results) {
    const resultsDiv = document.getElementById('coverage-results');
    
    const riskColor = results.riskLevel === 'Low' ? 'success' : 
                     results.riskLevel === 'Moderate' ? 'warning' : 'danger';
    
    resultsDiv.innerHTML = `
        <div class="results-container">
            <div class="results-header">
                <h3>Your Personalized Insurance Recommendations</h3>
                <div class="risk-indicator ${riskColor}">
                    <span class="risk-score">${results.riskScore}</span>
                    <span class="risk-label">${results.riskLevel} Risk</span>
                </div>
            </div>
            
            <div class="coverage-grid">
                <div class="coverage-card life">
                    <div class="coverage-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                        </svg>
                    </div>
                    <div class="coverage-details">
                        <h4>Life Insurance</h4>
                        <div class="coverage-amount">₹${formatCurrency(results.lifeInsurance)}</div>
                        <p>Recommended coverage to protect your family's financial future</p>
                    </div>
                </div>
                
                <div class="coverage-card health">
                    <div class="coverage-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                        </svg>
                    </div>
                    <div class="coverage-details">
                        <h4>Health Insurance</h4>
                        <div class="coverage-amount">₹${formatCurrency(results.healthInsurance)}</div>
                        <p>Comprehensive health coverage for medical emergencies</p>
                    </div>
                </div>
                
                <div class="coverage-card vehicle">
                    <div class="coverage-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M7 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"></path>
                            <path d="M17 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"></path>
                            <path d="M5 17h-2v-6l2-5h9l4 5h1a2 2 0 0 1 2 2v4h-2"></path>
                        </svg>
                    </div>
                    <div class="coverage-details">
                        <h4>Vehicle Insurance</h4>
                        <div class="coverage-amount">₹${formatCurrency(results.vehicleInsurance)}</div>
                        <p>Comprehensive coverage for your vehicle</p>
                    </div>
                </div>
                
                <div class="coverage-card home">
                    <div class="coverage-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                            <polyline points="9,22 9,12 15,12 15,22"></polyline>
                        </svg>
                    </div>
                    <div class="coverage-details">
                        <h4>Home Insurance</h4>
                        <div class="coverage-amount">₹${formatCurrency(results.homeInsurance)}</div>
                        <p>Protection for your home and belongings</p>
                    </div>
                </div>
            </div>
            
            <div class="premium-estimate">
                <h4>Estimated Monthly Premium</h4>
                <div class="premium-amount">₹${formatCurrency(results.monthlyPremiumEstimate)}</div>
                <p>Approximate monthly cost for recommended coverage</p>
            </div>
            
            <div class="recommendations-section">
                <h4>Personalized Recommendations</h4>
                <div class="recommendations-list">
                    ${results.recommendations.map(rec => `
                        <div class="recommendation-item ${rec.type}">
                            <div class="rec-icon">
                                ${rec.type === 'critical' ? '⚠️' : 
                                  rec.type === 'important' ? '💡' : 
                                  rec.type === 'warning' ? '⚡' : 'ℹ️'}
                            </div>
                            <div class="rec-content">
                                <h5>${rec.title}</h5>
                                <p>${rec.message}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="results-actions">
                <button onclick="window.print()" class="btn btn-secondary">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="6,9 6,2 18,2 18,9"></polyline>
                        <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
                        <rect x="6" y="14" width="12" height="8"></rect>
                    </svg>
                    Print Report
                </button>
                <button id="btn-save-assessment" class="btn btn-primary">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                        <polyline points="17,21 17,13 7,13 7,21"></polyline>
                        <polyline points="7,3 7,8 15,8"></polyline>
                    </svg>
                    Save Assessment
                </button>
            </div>
        </div>
    `;
    
    // Add event listener for save assessment
    document.getElementById('btn-save-assessment')?.addEventListener('click', () => saveAssessment(results));
}

function resetCalculator() {
    // Reset all form fields to default values
    document.getElementById('calc-age').value = '30';
    document.getElementById('calc-gender').value = 'male';
    document.getElementById('calc-marital').value = 'single';
    document.getElementById('calc-dependents').value = '0';
    document.getElementById('calc-expenses').value = '';
    document.getElementById('calc-debt').value = '0';
    document.getElementById('calc-savings').value = '';
    document.getElementById('calc-smoking').value = 'never';
    document.getElementById('calc-exercise').value = 'regular';
    document.getElementById('calc-city').value = 'metro';
    document.getElementById('calc-occupation').value = 'low';
    
    // Reset checkboxes
    document.querySelectorAll('input[type="checkbox"][id^="condition-"]').forEach(cb => {
        cb.checked = false;
    });
    document.getElementById('condition-none').checked = true;
    
    // Hide results
    document.getElementById('coverage-results').style.display = 'none';
    
    showToast('Calculator reset successfully', 'success');
}

async function loadDemoData() {
    const { user } = authState.get();
    
    if (!user || !user.id) {
        showToast('Please log in to load demo data', 'error');
        return;
    }

    const demoData = [
        {
            user_id: user.id,
            policy_type: 'health',
            provider: 'Star Health Insurance',
            policy_number: 'SH2024001',
            coverage_amount: 1000000,
            premium_amount: 25000,
            premium_frequency: 'annual',
            start_date: '2024-01-01',
            end_date: '2024-12-31',
            notes: 'Family floater policy covering spouse and 2 children with cashless facility at 500+ hospitals'
        },
        {
            user_id: user.id,
            policy_type: 'life',
            provider: 'LIC of India',
            policy_number: 'LIC2024002',
            coverage_amount: 5000000,
            premium_amount: 60000,
            premium_frequency: 'annual',
            start_date: '2024-01-15',
            end_date: '2044-01-15',
            notes: 'Term life insurance with 20-year coverage period, includes accidental death benefit'
        },
        {
            user_id: user.id,
            policy_type: 'vehicle',
            provider: 'HDFC ERGO',
            policy_number: 'VH2024003',
            coverage_amount: 500000,
            premium_amount: 15000,
            premium_frequency: 'annual',
            start_date: '2024-03-01',
            end_date: '2025-02-28',
            notes: 'Comprehensive coverage for Honda City including zero depreciation and roadside assistance'
        },
        {
            user_id: user.id,
            policy_type: 'home',
            provider: 'Bajaj Allianz',
            policy_number: 'HM2024004',
            coverage_amount: 2000000,
            premium_amount: 8000,
            premium_frequency: 'annual',
            start_date: '2024-04-01',
            end_date: '2025-03-31',
            notes: 'Home insurance covering structure, contents, and personal liability up to ₹20 lakhs'
        }
    ];

    try {
        showToast('Loading demo insurance policies...', 'info');
        
        // First, clean up any existing demo policies to avoid duplicates
        const existingPolicies = await apiFetch(`/insurance/policies/${user.id}`);
        const demoPolicyNumbers = ['SH2024001', 'LIC2024002', 'VH2024003', 'HM2024004'];
        
        for (const policy of existingPolicies) {
            if (demoPolicyNumbers.includes(policy.policy_number)) {
                try {
                    await apiFetch(`/insurance/policies/${policy.id}`, {
                        method: 'DELETE'
                    });
                } catch (deleteError) {
                    console.warn('Could not delete existing demo policy:', deleteError);
                }
            }
        }
        
        // Create new demo policies
        let successCount = 0;
        for (const policy of demoData) {
            try {
                await apiFetch('/insurance/policies', {
                    method: 'POST',
                    body: JSON.stringify(policy)
                });
                successCount++;
            } catch (policyError) {
                console.error('Error creating policy:', policyError);
                showToast(`Failed to create ${policy.policy_type} policy: ${policyError.message}`, 'warning');
            }
        }
        
        if (successCount > 0) {
            showToast(`Demo data loaded successfully! ${successCount} policies added.`, 'success');
            loadPolicies();
        } else {
            showToast('Failed to load any demo policies. Please try again.', 'error');
        }
        
    } catch (error) {
        console.error('Error loading demo data:', error);
        showToast(`Failed to load demo data: ${error.message || 'Unknown error'}`, 'error');
    }
}
async function loadPolicies() {
    const { user } = authState.get();
    const container = document.getElementById('policies-container');
    
    try {
        const policies = await apiFetch(`/insurance/policies/${user.id}`);
        
        if (!policies || policies.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">
                        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                        </svg>
                    </div>
                    <h3>No Insurance Policies Found</h3>
                    <p>Start by adding your first insurance policy or load demo data to explore the features</p>
                    <div class="empty-actions">
                        <button onclick="document.getElementById('btn-add-policy').click()" class="btn btn-primary">Add Your First Policy</button>
                        <button onclick="document.getElementById('btn-load-demo').click()" class="btn btn-secondary">Load Demo Data</button>
                    </div>
                </div>
            `;
            return;
        }

        // Group policies by type
        const groupedPolicies = policies.reduce((acc, policy) => {
            if (!acc[policy.policy_type]) {
                acc[policy.policy_type] = [];
            }
            acc[policy.policy_type].push(policy);
            return acc;
        }, {});

        container.innerHTML = `
            <div class="policies-grid">
                ${Object.entries(groupedPolicies).map(([type, typePolicies]) => `
                    <div class="policy-type-section">
                        <div class="policy-type-header">
                            <div class="policy-type-icon ${type}">
                                ${getPolicyTypeIcon(type)}
                            </div>
                            <div class="policy-type-info">
                                <h3>${capitalizeFirst(type)} Insurance</h3>
                                <p>${typePolicies.length} ${typePolicies.length === 1 ? 'policy' : 'policies'}</p>
                            </div>
                            <div class="policy-type-summary">
                                <div class="total-coverage">₹${formatCurrency(typePolicies.reduce((sum, p) => sum + p.coverage_amount, 0))}</div>
                                <div class="coverage-label">Total Coverage</div>
                            </div>
                        </div>
                        <div class="policy-cards">
                            ${typePolicies.map(policy => `
                                <div class="policy-card">
                                    <div class="policy-card-header">
                                        <div class="policy-provider">${policy.provider}</div>
                                        <div class="policy-status ${getPolicyStatusClass(policy)}">
                                            ${getPolicyStatus(policy)}
                                        </div>
                                    </div>
                                    <div class="policy-card-body">
                                        <div class="policy-number">Policy: ${policy.policy_number}</div>
                                        <div class="policy-details-grid">
                                            <div class="policy-detail">
                                                <span class="detail-label">Coverage</span>
                                                <span class="detail-value">₹${formatCurrency(policy.coverage_amount)}</span>
                                            </div>
                                            <div class="policy-detail">
                                                <span class="detail-label">Premium</span>
                                                <span class="detail-value">₹${formatCurrency(policy.premium_amount)}/${policy.premium_frequency || 'annual'}</span>
                                            </div>
                                            <div class="policy-detail">
                                                <span class="detail-label">Expires</span>
                                                <span class="detail-value">${formatDate(policy.end_date)}</span>
                                            </div>
                                            <div class="policy-detail">
                                                <span class="detail-label">Days Left</span>
                                                <span class="detail-value ${getDaysLeftClass(policy)}">${getDaysLeft(policy)} days</span>
                                            </div>
                                        </div>
                                        ${policy.notes ? `<div class="policy-notes">${policy.notes}</div>` : ''}
                                    </div>
                                    <div class="policy-card-actions">
                                        <button onclick="editPolicy('${policy.id}')" class="btn btn-sm btn-secondary">
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                                            </svg>
                                            Edit
                                        </button>
                                        <button onclick="deletePolicy('${policy.id}')" class="btn btn-sm btn-danger">
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                <polyline points="3,6 5,6 21,6"></polyline>
                                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                            </svg>
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading policies:', error);
        container.innerHTML = `
            <div class="error-state">
                <div class="error-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="15" y1="9" x2="9" y2="15"></line>
                        <line x1="9" y1="9" x2="15" y2="15"></line>
                    </svg>
                </div>
                <h3>Failed to Load Policies</h3>
                <p>There was an error loading your insurance policies. Please try again.</p>
                <button onclick="loadPolicies()" class="btn btn-primary">Retry</button>
            </div>
        `;
    }
}

function showAddPolicyModal() {
    document.getElementById('add-policy-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
    
    // Set default dates
    const today = new Date().toISOString().split('T')[0];
    const nextYear = new Date();
    nextYear.setFullYear(nextYear.getFullYear() + 1);
    
    document.getElementById('policy-start').value = today;
    document.getElementById('policy-end').value = nextYear.toISOString().split('T')[0];
    
    // Add real-time validation
    setTimeout(() => {
        addFormValidation();
    }, 100);
}

function addFormValidation() {
    const form = document.getElementById('add-policy-form');
    if (!form) return;
    
    const fields = [
        { id: 'policy-type', required: true, type: 'select' },
        { id: 'policy-provider', required: true, type: 'text', minLength: 2 },
        { id: 'policy-number', required: true, type: 'text', minLength: 3 },
        { id: 'policy-coverage', required: true, type: 'number', min: 1000 },
        { id: 'policy-premium', required: true, type: 'number', min: 100 },
        { id: 'policy-start', required: true, type: 'date' },
        { id: 'policy-end', required: true, type: 'date' }
    ];
    
    fields.forEach(field => {
        const element = document.getElementById(field.id);
        if (!element) return;
        
        element.addEventListener('blur', () => validateField(field, element));
        element.addEventListener('input', () => {
            // Clear error state on input
            clearFieldError(element);
        });
    });
    
    // Date range validation
    const startDate = document.getElementById('policy-start');
    const endDate = document.getElementById('policy-end');
    
    [startDate, endDate].forEach(el => {
        el?.addEventListener('change', () => validateDateRange());
    });
}

function validateField(fieldConfig, element) {
    const value = element.value.trim();
    const group = element.closest('.form-group');
    
    // Clear previous validation
    clearFieldError(element);
    
    // Required validation
    if (fieldConfig.required && !value) {
        showFieldError(element, 'This field is required');
        return false;
    }
    
    // Type-specific validation
    switch (fieldConfig.type) {
        case 'text':
            if (fieldConfig.minLength && value.length < fieldConfig.minLength) {
                showFieldError(element, `Minimum ${fieldConfig.minLength} characters required`);
                return false;
            }
            break;
            
        case 'number':
            const num = parseFloat(value);
            if (isNaN(num) || num <= 0) {
                showFieldError(element, 'Please enter a valid positive number');
                return false;
            }
            if (fieldConfig.min && num < fieldConfig.min) {
                showFieldError(element, `Minimum value is ${fieldConfig.min}`);
                return false;
            }
            break;
            
        case 'date':
            if (value && !isValidDate(value)) {
                showFieldError(element, 'Please enter a valid date');
                return false;
            }
            break;
    }
    
    // Show success state
    showFieldSuccess(element);
    return true;
}

function validateDateRange() {
    const startDate = document.getElementById('policy-start');
    const endDate = document.getElementById('policy-end');
    
    if (!startDate.value || !endDate.value) return;
    
    const start = new Date(startDate.value);
    const end = new Date(endDate.value);
    
    clearFieldError(endDate);
    
    if (end <= start) {
        showFieldError(endDate, 'End date must be after start date');
        return false;
    }
    
    // Check if dates are reasonable (not too far in past/future)
    const today = new Date();
    const maxFuture = new Date();
    maxFuture.setFullYear(maxFuture.getFullYear() + 50);
    
    if (start > maxFuture || end > maxFuture) {
        showFieldError(endDate, 'Policy dates seem too far in the future');
        return false;
    }
    
    showFieldSuccess(endDate);
    return true;
}

function showFieldError(element, message) {
    const group = element.closest('.form-group');
    group.classList.add('has-error');
    group.classList.remove('has-success');
    
    element.classList.add('error');
    element.classList.remove('success');
    
    // Remove existing error message
    const existingError = group.querySelector('.form-error');
    if (existingError) existingError.remove();
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
        </svg>
        ${message}
    `;
    element.parentNode.appendChild(errorDiv);
}

function showFieldSuccess(element) {
    const group = element.closest('.form-group');
    group.classList.remove('has-error');
    group.classList.add('has-success');
    
    element.classList.remove('error');
    element.classList.add('success');
    
    // Remove error message
    const existingError = group.querySelector('.form-error');
    if (existingError) existingError.remove();
}

function clearFieldError(element) {
    const group = element.closest('.form-group');
    group.classList.remove('has-error', 'has-success');
    
    element.classList.remove('error', 'success');
    
    // Remove error/success messages
    const existingError = group.querySelector('.form-error');
    const existingSuccess = group.querySelector('.form-success');
    if (existingError) existingError.remove();
    if (existingSuccess) existingSuccess.remove();
}

function isValidDate(dateString) {
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date);
}

function hideAddPolicyModal() {
    document.getElementById('add-policy-modal').style.display = 'none';
    document.body.style.overflow = 'auto';
    
    // Reset form
    const form = document.getElementById('add-policy-form');
    form.reset();
    
    // Reset modal state
    document.querySelector('#add-policy-modal .modal-header h3').textContent = 'Add New Insurance Policy';
    document.querySelector('#add-policy-modal .modal-footer .btn-primary').textContent = 'Add Policy';
    
    // Clear editing state
    delete form.dataset.editingId;
}

async function handleAddPolicy(e) {
    e.preventDefault();
    console.log('Form submission started');
    
    try {
        const { user } = authState.get();
        if (!user) {
            showToast('Please log in to add a policy', 'error');
            return;
        }
        
        // Get form elements safely
        const form = document.getElementById('add-policy-form');
        if (!form) {
            showToast('Form not found. Please refresh the page.', 'error');
            return;
        }
        
        // Check if we're editing or creating
        const editingId = form.dataset.editingId;
        const isEditing = !!editingId;
        
        const formData = new FormData(form);
        
        // Get values with fallback to direct element access
        const getValue = (name, elementId) => {
            return formData.get(name) || document.getElementById(elementId)?.value || '';
        };
        
        const policyData = {
            user_id: user.id,
            policy_type: getValue('policy-type', 'policy-type'),
            provider: getValue('policy-provider', 'policy-provider'),
            policy_number: getValue('policy-number', 'policy-number'),
            coverage_amount: parseFloat(getValue('policy-coverage', 'policy-coverage') || '0'),
            premium_amount: parseFloat(getValue('policy-premium', 'policy-premium') || '0'),
            premium_frequency: getValue('policy-frequency', 'policy-frequency') || 'annual',
            start_date: (getValue('policy-start', 'policy-start')) + 'T00:00:00Z',
            end_date: (getValue('policy-end', 'policy-end')) + 'T23:59:59Z',
            beneficiaries: [],
            notes: (getValue('policy-notes', 'policy-notes')).trim()
        };
        
        console.log('Policy data:', policyData);
        
        // Validate required fields
        if (!policyData.policy_type) {
            showToast('Please select a policy type', 'error');
            return;
        }
        if (!policyData.provider?.trim()) {
            showToast('Please enter the insurance provider', 'error');
            return;
        }
        if (!policyData.policy_number?.trim()) {
            showToast('Please enter the policy number', 'error');
            return;
        }
        if (policyData.coverage_amount <= 0) {
            showToast('Please enter a valid coverage amount', 'error');
            return;
        }
        if (policyData.premium_amount <= 0) {
            showToast('Please enter a valid premium amount', 'error');
            return;
        }
        
        // Disable form during submission
        const submitButtons = document.querySelectorAll('button[form="add-policy-form"], #add-policy-form button[type="submit"], .modal-footer button[type="submit"]');
        const originalStates = [];
        
        submitButtons.forEach((btn, index) => {
            if (btn && btn.textContent) {
                originalStates[index] = {
                    disabled: btn.disabled,
                    text: btn.textContent
                };
                btn.disabled = true;
                btn.textContent = isEditing ? 'Updating Policy...' : 'Adding Policy...';
            }
        });
        
        try {
            let response;
            if (isEditing) {
                // Update existing policy
                response = await apiFetch(`/insurance/policies/${editingId}`, {
                    method: 'PUT',
                    body: JSON.stringify(policyData)
                });
                showToast('Insurance policy updated successfully!', 'success');
            } else {
                // Create new policy
                response = await apiFetch('/insurance/policies', {
                    method: 'POST',
                    body: JSON.stringify(policyData)
                });
                showToast('Insurance policy added successfully!', 'success');
            }
            
            console.log('Policy operation completed:', response);
            hideAddPolicyModal();
            loadPolicies();
            
        } catch (error) {
            console.error('API Error:', error);
            let errorMessage = isEditing ? 'Failed to update policy. Please try again.' : 'Failed to add policy. Please try again.';
            
            if (error.message) {
                if (error.message.includes('foreign key')) {
                    errorMessage = 'User authentication error. Please refresh and try again.';
                } else if (error.message.includes('duplicate')) {
                    errorMessage = 'A policy with this number already exists.';
                } else if (error.message.includes('validation')) {
                    errorMessage = 'Please check all required fields and try again.';
                } else if (error.message.includes('not found')) {
                    errorMessage = 'Policy not found. It may have been deleted.';
                } else {
                    errorMessage = `Error: ${error.message}`;
                }
            }
            
            showToast(errorMessage, 'error');
        } finally {
            // Restore button states
            submitButtons.forEach((btn, index) => {
                if (btn && originalStates[index] && originalStates[index].text) {
                    btn.disabled = originalStates[index].disabled;
                    btn.textContent = originalStates[index].text;
                }
            });
        }
        
    } catch (error) {
        console.error('Form submission error:', error);
        showToast('An unexpected error occurred. Please try again.', 'error');
    }
}

async function editPolicy(policyId) {
    try {
        const { user } = authState.get();
        if (!user) {
            showToast('Please log in to edit policies', 'error');
            return;
        }

        // Get the policy data
        const policies = await apiFetch(`/insurance/policies/${user.id}`);
        const policy = policies.find(p => p.id === policyId);
        
        if (!policy) {
            showToast('Policy not found', 'error');
            return;
        }

        // Show the modal with pre-filled data
        document.getElementById('add-policy-modal').style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Change modal title
        document.querySelector('#add-policy-modal .modal-header h3').textContent = 'Edit Insurance Policy';
        
        // Pre-fill the form
        document.getElementById('policy-type').value = policy.policy_type;
        document.getElementById('policy-provider').value = policy.provider;
        document.getElementById('policy-number').value = policy.policy_number;
        document.getElementById('policy-coverage').value = policy.coverage_amount;
        document.getElementById('policy-premium').value = policy.premium_amount;
        document.getElementById('policy-frequency').value = policy.premium_frequency;
        
        // Format dates for input fields
        const startDate = new Date(policy.start_date).toISOString().split('T')[0];
        const endDate = new Date(policy.end_date).toISOString().split('T')[0];
        document.getElementById('policy-start').value = startDate;
        document.getElementById('policy-end').value = endDate;
        document.getElementById('policy-notes').value = policy.notes || '';
        
        // Change submit button text
        const submitBtn = document.querySelector('#add-policy-modal .modal-footer .btn-primary');
        submitBtn.textContent = 'Update Policy';
        
        // Store the policy ID for update
        document.getElementById('add-policy-form').dataset.editingId = policyId;
        
    } catch (error) {
        console.error('Error loading policy for edit:', error);
        showToast('Failed to load policy data', 'error');
    }
}

async function deletePolicy(policyId) {
    const confirmed = await showConfirm('This action cannot be undone.', 'Delete Policy?');
    if (!confirmed) {
        return;
    }

    try {
        const { user } = authState.get();
        if (!user) {
            showToast('Please log in to delete policies', 'error');
            return;
        }

        showToast('Deleting policy...', 'info');
        
        await apiFetch(`/insurance/policies/${policyId}`, {
            method: 'DELETE'
        });
        
        showToast('Insurance policy deleted successfully!', 'success');
        loadPolicies(); // Refresh the policies list
        
    } catch (error) {
        console.error('Error deleting policy:', error);
        let errorMessage = 'Failed to delete policy. Please try again.';
        
        if (error.message) {
            if (error.message.includes('not found')) {
                errorMessage = 'Policy not found or already deleted.';
            } else {
                errorMessage = `Error: ${error.message}`;
            }
        }
        
        showToast(errorMessage, 'error');
    }
}

async function saveAssessment(results) {
    const { user } = authState.get();
    if (!user) {
        showToast('Please log in to save assessment', 'error');
        return;
    }

    // Prepare assessment data matching the backend schema
    const assessmentData = {
        user_id: user.id,
        age: parseInt(document.getElementById('calc-age').value),
        dependents: parseInt(document.getElementById('calc-dependents').value),
        annual_income: parseFloat(document.getElementById('calc-income').value),
        monthly_expenses: parseFloat(document.getElementById('calc-expenses').value),
        existing_loans: parseFloat(document.getElementById('calc-debt').value) || 0,
        health_conditions: getSelectedHealthConditions(),
        lifestyle_factors: {
            smoking: document.getElementById('calc-smoking').value === 'current',
            city_tier: document.getElementById('calc-city').value
        }
    };

    console.log('Saving assessment:', assessmentData);

    try {
        // Call backend API
        const response = await fetch(`${API_URL}/insurance/assessment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(assessmentData)
        });

        if (response.ok) {
            const savedAssessment = await response.json();
            console.log('Assessment saved successfully:', savedAssessment);
            showToast('✅ Assessment saved to database!', 'success');
        } else {
            const error = await response.json();
            console.error('Failed to save assessment:', error);
            showToast('Failed to save assessment: ' + (error.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error saving assessment:', error);
        showToast('Error saving assessment. Please try again.', 'error');
    }
}

function getSelectedHealthConditions() {
    const conditions = [];
    document.querySelectorAll('input[type="checkbox"][id^="condition-"]:checked').forEach(cb => {
        if (cb.value !== 'none') {
            conditions.push(cb.value);
        }
    });
    return conditions;
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        maximumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function getPolicyStatus(policy) {
    const endDate = new Date(policy.end_date);
    const today = new Date();
    const daysUntilExpiry = Math.ceil((endDate - today) / (1000 * 60 * 60 * 24));
    
    if (daysUntilExpiry < 0) return 'Expired';
    if (daysUntilExpiry <= 30) return 'Expiring Soon';
    return 'Active';
}

function getPolicyStatusClass(policy) {
    const status = getPolicyStatus(policy);
    switch (status) {
        case 'Active': return 'status-active';
        case 'Expiring Soon': return 'status-warning';
        case 'Expired': return 'status-expired';
        default: return 'status-unknown';
    }
}

function getDaysLeft(policy) {
    const endDate = new Date(policy.end_date);
    const today = new Date();
    return Math.ceil((endDate - today) / (1000 * 60 * 60 * 24));
}

function getDaysLeftClass(policy) {
    const days = getDaysLeft(policy);
    if (days < 0) return 'text-danger';
    if (days <= 30) return 'text-warning';
    return 'text-success';
}

function getPolicyTypeIcon(type) {
    const icons = {
        health: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>',
        life: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
        vehicle: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"></path><path d="M17 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"></path><path d="M5 17h-2v-6l2-5h9l4 5h1a2 2 0 0 1 2 2v4h-2"></path></svg>',
        home: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9,22 9,12 15,12 15,22"></polyline></svg>',
        travel: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>'
    };
    return icons[type] || icons.health;
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

// Make functions globally available
window.loadPolicies = loadPolicies;
window.editPolicy = editPolicy;
window.deletePolicy = deletePolicy;