import { apiFetch } from '../utils.js';
import { authState } from '../auth.js';

let chartInstance = null;

export default async function DashboardView() {
    const { user } = authState.get();

    let stats = { balance: 0, income: 0, expenses: 0 };
    let txns = [];
    let insights = null;
    let userProfile = null;

    let riskData = null;

    try {
        const [statsRes, txnsRes, insightsRes, profileRes, riskRes] = await Promise.all([
            apiFetch(`/transactions/stats?user_id=${user.id}`).catch(() => stats),
            apiFetch(`/transactions?user_id=${user.id}&limit=500`).catch(() => []),
            apiFetch(`/insights?user_id=${user.id}`).catch(() => null),
            apiFetch(`/users/${user.id}`).catch(() => null),
            apiFetch(`/risk/score?user_id=${user.id}`).catch(() => null)
        ]);
        stats = statsRes;
        txns = txnsRes;
        insights = insightsRes;
        userProfile = profileRes;
        riskData = riskRes;
    } catch (e) {
        console.error('Dashboard data fetch error:', e);
    }

    const baseIncome = userProfile?.income || 0;
    const displayIncome = baseIncome + stats.income;
    const balance = displayIncome - stats.expenses;
    const hasFraud = txns.some(t => t.is_fraud);
    const recentTxns = txns.slice(0, 5);

    const now = new Date();
    const past6Months = Array.from({ length: 6 }, (_, i) => {
        const d = new Date(now.getFullYear(), now.getMonth() - (5 - i), 1);
        return { month: d.getMonth(), year: d.getFullYear(), label: d.toLocaleString('en-US', { month: 'short' }), income: baseIncome, expenses: 0 };
    });

    txns.forEach(t => {
        const d = new Date(t.timestamp);
        const m = past6Months.find(pm => pm.month === d.getMonth() && pm.year === d.getFullYear());
        if (m) {
            if (t.type === 'income') m.income += t.amount;
            else m.expenses += t.amount;
        }
    });

    const curr = past6Months[5];
    const prev = past6Months[4];

    // safe division helpers
    const getChange = (c, p) => p ? ((c - p) / p * 100).toFixed(1) : 0;
    const getChangePosNeg = (c, p) => p ? ((c - p) / Math.abs(p) * 100).toFixed(1) : 0;

    const incomeChange = getChange(curr.income, prev.income);
    const expensesChange = getChange(curr.expenses, prev.expenses);
    const balanceChange = getChangePosNeg(curr.income - curr.expenses, prev.income - prev.expenses);

    const labels = past6Months.map(m => m.label);
    const expensesData = past6Months.map(m => m.expenses);
    const incomeData = past6Months.map(m => m.income);

    setTimeout(() => {
        const canvas = document.getElementById('spending-chart');
        if (canvas && window.Chart) {
            if (chartInstance) chartInstance.destroy();

            const ctx = canvas.getContext('2d');
            const labels = ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr'];

            chartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels,
                    datasets: [
                        {
                            label: 'Expenses',
                            data: expensesData,
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            fill: true,
                            tension: 0.4,
                            borderWidth: 2
                        },
                        {
                            label: 'Income',
                            data: incomeData,
                            borderColor: '#10b981',
                            backgroundColor: 'transparent',
                            tension: 0.4,
                            borderWidth: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            align: 'end',
                            labels: {
                                boxWidth: 12,
                                boxHeight: 12,
                                padding: 15,
                                font: { size: 12, weight: '600' }
                            }
                        }
                    },
                    scales: {
                        y: {
                            border: { display: false },
                            grid: { color: '#f3f4f6' },
                            ticks: { font: { size: 11 } }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { font: { size: 11 } }
                        }
                    }
                }
            });
        }
    }, 100);

    return `
        <div class="fade-in">
            ${hasFraud ? `
                <div class="alert alert-danger">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <div>
                        <strong style="display: block; margin-bottom: 0.25rem;">Suspicious Activity Detected</strong>
                        <span style="font-size: 0.875rem;">AI fraud detection has flagged unusual transactions. Review immediately.</span>
                    </div>
                </div>
            ` : ''}

            <div class="flex items-center justify-between mb-xl">
                <div>
                    <h1 style="font-size: 1.75rem; font-weight: 700; color: #111827; margin-bottom: 0.25rem;">
                        ${(new Date().getHours() < 12) ? 'Good morning' : (new Date().getHours() < 18) ? 'Good afternoon' : 'Good evening'}, ${user.name?.split(' ')[0] || 'User'}
                    </h1>
                    <p style="font-size: 0.875rem; color: #6b7280;">${new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}</p>
                </div>
                <button class="icon-btn">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="23 4 23 10 17 10"></polyline>
                        <polyline points="1 20 1 14 7 14"></polyline>
                        <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                    </svg>
                </button>
            </div>

            <div class="grid grid-cols-4 mb-xl">
                <div class="stat-card">
                    <div class="stat-label">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
                            <line x1="1" y1="10" x2="23" y2="10"></line>
                        </svg>
                        Balance
                    </div>
                    <div class="stat-value">₹${balance.toLocaleString()}</div>
                    <div class="stat-change ${balanceChange >= 0 ? 'positive' : 'negative'}">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="23 ${balanceChange >= 0 ? '6 13.5 15.5 8.5 10.5 1 18' : '18 13.5 8.5 8.5 13.5 1 6'}"></polyline>
                        </svg>
                        ${balanceChange > 0 ? '+' : ''}${balanceChange}%
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                            <polyline points="17 6 23 6 23 12"></polyline>
                        </svg>
                        Income
                    </div>
                    <div class="stat-value">₹${displayIncome.toLocaleString()}</div>
                    <div class="stat-change ${incomeChange >= 0 ? 'positive' : 'negative'}">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="23 ${incomeChange >= 0 ? '6 13.5 15.5 8.5 10.5 1 18' : '18 13.5 8.5 8.5 13.5 1 6'}"></polyline>
                        </svg>
                        ${incomeChange > 0 ? '+' : ''}${incomeChange}%
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
                            <polyline points="17 18 23 18 23 12"></polyline>
                        </svg>
                        Expenses
                    </div>
                    <div class="stat-value">₹${stats.expenses.toLocaleString()}</div>
                    <div class="stat-change ${expensesChange <= 0 ? 'positive' : 'negative'}">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="23 ${expensesChange >= 0 ? '6 13.5 15.5 8.5 10.5 1 18' : '18 13.5 8.5 8.5 13.5 1 6'}"></polyline>
                        </svg>
                        ${expensesChange > 0 ? '+' : ''}${expensesChange}%
                    </div>
                </div>

                <div class="stat-card" style="border-left: 3px solid #10b981;">
                    <div class="stat-label">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                        </svg>
                        Risk Score
                    </div>
                    <div class="stat-value">${riskData ? riskData.score : '--'}/100</div>
                    <div class="badge badge-${riskData ? (riskData.score >= 75 ? 'success' : riskData.score >= 40 ? 'warning' : 'danger') : 'info'}" style="margin-top: 0.5rem;">${riskData ? riskData.grade : 'Loading...'}</div>
                </div>
            </div>

            <div class="grid" style="grid-template-columns: 2fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Spending Trend</h2>
                    </div>
                    <div class="card-body" style="height: 320px;">
                        <canvas id="spending-chart"></canvas>
                    </div>
                </div>

                <div class="card" style="border-top: 3px solid #f59e0b;">
                    <div class="card-header" style="background: linear-gradient(to right, #fef3c7, transparent);">
                        <h2 class="card-title" style="display: flex; align-items: center; gap: 0.5rem;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                            </svg>
                            AI Insights
                        </h2>
                    </div>
                    <div class="card-body" style="max-height: 320px; overflow-y: auto;">
                        ${insights && insights.insights?.length > 0 ? insights.insights.map(i => `
                            <div class="card" style="margin-bottom: 1rem; border-color: ${i.type === 'warning' ? '#f59e0b' : i.type === 'positive' ? '#10b981' : '#3b82f6'};">
                                <div class="card-body" style="padding: 1rem;">
                                    <div style="font-size: 1.25rem; margin-bottom: 0.5rem;">${i.icon}</div>
                                    <h3 style="font-size: 0.875rem; font-weight: 600; color: #111827; margin-bottom: 0.25rem;">${i.title}</h3>
                                    <p style="font-size: 0.8125rem; color: #6b7280; line-height: 1.5;">${i.message}</p>
                                </div>
                            </div>
                        `).join('') : `
                            <div class="empty-state">
                                <div class="empty-state-icon">
                                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <circle cx="12" cy="12" r="10"></circle>
                                        <line x1="12" y1="16" x2="12" y2="12"></line>
                                        <line x1="12" y1="8" x2="12.01" y2="8"></line>
                                    </svg>
                                </div>
                                <p class="empty-state-text">No insights available</p>
                            </div>
                        `}
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Recent Transactions</h2>
                </div>
                <div class="card-body" style="padding: 0;">
                    ${txns.length > 0 ? `
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Description</th>
                                    <th>Category</th>
                                    <th>Amount</th>
                                    <th>Date</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${recentTxns.map(tx => `
                                    <tr>
                                        <td style="font-weight: 600;">${tx.description}</td>
                                        <td><span class="badge badge-info">${tx.category}</span></td>
                                        <td style="font-weight: 700; color: ${tx.type === 'income' ? '#10b981' : '#111827'};">
                                            ${tx.type === 'income' ? '+' : '-'}₹${tx.amount.toLocaleString()}
                                        </td>
                                        <td style="color: #6b7280; font-size: 0.875rem;">
                                            ${new Date(tx.timestamp).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                                        </td>
                                        <td>
                                            <span class="badge ${tx.is_fraud ? 'badge-danger' : 'badge-success'}">
                                                ${tx.is_fraud ? 'Flagged' : 'Safe'}
                                            </span>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    ` : `
                        <div class="empty-state">
                            <div class="empty-state-icon">
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
                                    <line x1="1" y1="10" x2="23" y2="10"></line>
                                </svg>
                            </div>
                            <p class="empty-state-title">No transactions yet</p>
                            <p class="empty-state-text">Start by adding your first transaction</p>
                        </div>
                    `}
                </div>
            </div>
        </div>
    `;
}
