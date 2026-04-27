// Demo data for insurance feature
export function generateDemoInsuranceData(userId) {
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
        },
        {
            id: 'demo_vehicle_1',
            user_id: userId,
            policy_type: 'vehicle',
            provider: 'Bajaj Allianz',
            policy_number: 'BA456789123',
            coverage_amount: 800000,
            premium_amount: 8500,
            premium_frequency: 'annual',
            start_date: '2024-03-15T00:00:00Z',
            end_date: '2025-03-14T23:59:59Z',
            beneficiaries: [],
            status: 'active',
            notes: 'Comprehensive car insurance',
            created_at: '2024-03-15T00:00:00Z',
            updated_at: '2024-03-15T00:00:00Z'
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
            'Increase health insurance coverage by ₹7,00,000 to cover potential medical expenses.',
            'With existing health conditions, consider increasing health coverage to at least ₹5 lakhs.',
            'At your age, medical expenses tend to increase. Consider coverage of at least ₹10 lakhs.'
        ],
        created_at: '2024-04-20T10:30:00Z',
        updated_at: '2024-04-20T10:30:00Z'
    };

    // Store in localStorage
    localStorage.setItem('insurance_policies', JSON.stringify(demoPolicies));
    localStorage.setItem('insurance_assessments', JSON.stringify([demoAssessment]));

    return { policies: demoPolicies, assessment: demoAssessment };
}

// Add demo data button to insurance page
export function addDemoDataButton() {
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
            try {
                // Import authState dynamically to avoid circular imports
                import('./auth.js').then(({ authState }) => {
                    const { user } = authState.get();
                    if (user) {
                        generateDemoInsuranceData(user.id);
                        // Reload the insurance handlers instead of full page reload
                        if (window.location.hash === '#insurance') {
                            setTimeout(() => {
                                const event = new Event('hashchange');
                                window.dispatchEvent(event);
                            }, 100);
                        }
                    }
                });
            } catch (error) {
                console.error('Error loading demo data:', error);
            }
        });
        
        header.appendChild(demoBtn);
    }
}