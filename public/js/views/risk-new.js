import { apiFetch } from '../utils.js';
import { authState } from '../auth.js';

let radarChart = null;

export default async function RiskView() {
    const { user } = authState.get();
    let risk = { score: 0, grade: 'F', label: 'Poor', breakdown: {} };

    try {
        risk = await apiFetch(`/risk/score?user_id=${user.id}`);
    } catch (e) {
        console.error('Risk data fetch error:', e);
    }

    const { score, grade, label, breakdown } = risk;
    
    const gradeConfig = {
        'A': { color: '#10b981', bg: '#d1fae5', label: 'Excellent' },
        'B': { color: '#3b82f6', bg: '#dbeafe', label: 'Good' },
        'C': { color: '#f59e0b', bg: '#fef3c7', label: 'Average' },
        'D': { color: '#ef4444', bg: '#fee2e2', label: 'At Risk' },
        'F': { color: '#991b1b', bg: '#fecaca', label: 'Poor' }
    };

    const config = gradeConfig[grade] || gradeConfig['F'];

    setTimeout(() => {
        const canvas = document.getElementById('radar-chart');
        if (canvas && window.Chart) {
            if (radarChart) radarChart.destroy();
            
            const ctx = canvas.getContext('2d');
            const factors = Object.entries(breakdown).map(([key, value]) => ({
                label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                value: Math.max(0, value)
            }));

            radarChart = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: factors.map(f => f.label),
                    datasets: [{
                        label: 'Your Score',
                        data: factors.map(f => f.value),
                        backgroundColor: 'rgba(37, 99, 235, 0.2)',
                        borderColor: '#2563eb',
                        borderWidth: 2,
                        pointBackgroundColor: '#2563eb',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            min: 0,
                            max: 100,
                            ticks: {
                                stepSize: 20,
                                font: { size: 10 }
                            },
                            grid: { color: '#e5e7eb' },
                            angleLines: { color: '#e5e7eb' },
                            pointLabels: {
                                font: { size: 11, weight: '600' }
                            }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
    }, 100);

    return `
        <div class="fade-in">
            <div class="flex items-center justify-between mb-xl">
                <div>
                    <h1 style="font-size: 1.75rem; font-weight: 700; color: #111827; margin-bottom: 0.25rem;">Risk Analysis</h1>
                    <p style="font-size: 0.875rem; color: #6b7280;">Comprehensive financial health assessment</p>
                </div>
                <div class="status-badge">
                    <span class="status-dot"></span>
                    Real-time Analysis
                </div>
            </div>

            <div class="grid" style="grid-template-columns: 1fr 2fr; gap: 1.5rem; margin-bottom: 2rem;">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Health Score</h2>
                    </div>
                    <div class="card-body" style="text-align: center; padding: 2rem;">
                        <div style="position: relative; width: 200px; height: 200px; margin: 0 auto 2rem;">
                            <svg viewBox="0 0 200 200" style="transform: rotate(-90deg);">
                                <circle cx="100" cy="100" r="80" fill="none" stroke="#f3f4f6" stroke-width="20"></circle>
                                <circle cx="100" cy="100" r="80" fill="none" stroke="${config.color}" stroke-width="20" 
                                    stroke-dasharray="${(score / 100) * 502.65} 502.65" 
                                    stroke-linecap="round"
                                    style="transition: stroke-dasharray 1s ease;">
                                </circle>
                            </svg>
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                                <div style="font-size: 3rem; font-weight: 700; color: ${config.color}; line-height: 1;">${score}</div>
                                <div style="font-size: 0.875rem; color: #6b7280; margin-top: 0.25rem;">out of 100</div>
                            </div>
                        </div>

                        <div class="card" style="background: ${config.bg}; border-color: ${config.color};">
                            <div class="card-body" style="padding: 1.5rem; text-align: center;">
                                <div style="font-size: 2.5rem; font-weight: 700; color: ${config.color}; margin-bottom: 0.5rem;">
                                    ${grade}
                                </div>
                                <div style="font-size: 0.875rem; font-weight: 600; color: ${config.color}; text-transform: uppercase; letter-spacing: 0.05em;">
                                    ${label}
                                </div>
                            </div>
                        </div>

                        <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #e5e7eb;">
                            <div style="font-size: 0.75rem; color: #6b7280; margin-bottom: 0.5rem;">Last Updated</div>
                            <div style="font-size: 0.875rem; font-weight: 600; color: #111827;">
                                ${new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                            </div>
                        </div>
                    </div>
                </div>

                <div style="display: flex; flex-direction: column; gap: 1.5rem;">
                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">Health Factors</h2>
                        </div>
                        <div class="card-body" style="height: 300px;">
                            <canvas id="radar-chart"></canvas>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">Factor Breakdown</h2>
                        </div>
                        <div class="card-body">
                            ${Object.entries(breakdown).map(([key, value]) => {
                                const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                                const score = Math.max(0, value);
                                const color = score >= 70 ? '#10b981' : score >= 40 ? '#f59e0b' : '#ef4444';
                                
                                return `
                                    <div style="margin-bottom: 1.5rem;">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                            <span style="font-size: 0.875rem; font-weight: 600; color: #374151;">${label}</span>
                                            <span style="font-size: 0.875rem; font-weight: 700; color: ${color};">${score.toFixed(0)}%</span>
                                        </div>
                                        <div style="height: 8px; background: #f3f4f6; border-radius: 999px; overflow: hidden;">
                                            <div style="height: 100%; background: ${color}; width: ${score}%; transition: width 1s ease; border-radius: 999px;"></div>
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-3 mb-xl">
                <div class="card" style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-color: #10b981;">
                    <div class="card-body">
                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                            <div style="width: 48px; height: 48px; background: white; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
                                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                                </svg>
                            </div>
                            <div>
                                <div style="font-size: 0.75rem; font-weight: 600; color: #065f46; text-transform: uppercase; letter-spacing: 0.05em;">Strengths</div>
                                <div style="font-size: 1.25rem; font-weight: 700; color: #065f46;">
                                    ${Object.entries(breakdown).filter(([k, v]) => v >= 70).length}
                                </div>
                            </div>
                        </div>
                        <p style="font-size: 0.8125rem; color: #065f46;">
                            Areas where you're performing well
                        </p>
                    </div>
                </div>

                <div class="card" style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-color: #f59e0b;">
                    <div class="card-body">
                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                            <div style="width: 48px; height: 48px; background: white; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2">
                                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                                    <line x1="12" y1="9" x2="12" y2="13"></line>
                                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                                </svg>
                            </div>
                            <div>
                                <div style="font-size: 0.75rem; font-weight: 600; color: #92400e; text-transform: uppercase; letter-spacing: 0.05em;">Needs Attention</div>
                                <div style="font-size: 1.25rem; font-weight: 700; color: #92400e;">
                                    ${Object.entries(breakdown).filter(([k, v]) => v >= 40 && v < 70).length}
                                </div>
                            </div>
                        </div>
                        <p style="font-size: 0.8125rem; color: #92400e;">
                            Areas that need improvement
                        </p>
                    </div>
                </div>

                <div class="card" style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); border-color: #ef4444;">
                    <div class="card-body">
                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                            <div style="width: 48px; height: 48px; background: white; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2">
                                    <circle cx="12" cy="12" r="10"></circle>
                                    <line x1="15" y1="9" x2="9" y2="15"></line>
                                    <line x1="9" y1="9" x2="15" y2="15"></line>
                                </svg>
                            </div>
                            <div>
                                <div style="font-size: 0.75rem; font-weight: 600; color: #991b1b; text-transform: uppercase; letter-spacing: 0.05em;">Critical</div>
                                <div style="font-size: 1.25rem; font-weight: 700; color: #991b1b;">
                                    ${Object.entries(breakdown).filter(([k, v]) => v < 40).length}
                                </div>
                            </div>
                        </div>
                        <p style="font-size: 0.8125rem; color: #991b1b;">
                            Areas requiring immediate action
                        </p>
                    </div>
                </div>
            </div>

            <div class="card" style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-color: #3b82f6;">
                <div class="card-body">
                    <h3 style="font-size: 1rem; font-weight: 600; color: #1e40af; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                            <line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>
                        How Risk Score is Calculated
                    </h3>
                    <p style="font-size: 0.875rem; color: #1e40af; line-height: 1.6;">
                        Your risk score is computed from 5 weighted factors: Savings Rate (25%), Budget Adherence (20%), 
                        Spending Consistency (20%), Fraud Exposure (20%), and Emergency Fund (15%). Each factor is analyzed 
                        from your real transaction data and financial behavior patterns.
                    </p>
                </div>
            </div>
        </div>
    `;
}
