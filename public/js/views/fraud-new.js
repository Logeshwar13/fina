import { apiFetch, showConfirm } from '../utils.js';
import { authState } from '../auth.js';
import '../components/toast.js';

export default async function FraudView() {
    const { user } = authState.get();
    let txns = [];

    window.markSafe = async (id) => {
        const confirmed = await showConfirm('This will mark the transaction as safe and remove it from the fraud list.', 'Mark as Safe?');
        if (!confirmed) return;
        
        try {
            await apiFetch(`/transactions/${id}`, {
                method: 'PUT',
                body: JSON.stringify({ is_fraud: false, fraud_score: 0 })
            });
            window.showToast('Transaction marked safe', 'success');
            // Reload fraud page
            const { navigateTo } = await import('../utils.js');
            setTimeout(() => navigateTo('fraud'), 100);
        } catch (e) {
            window.showToast('Error marking as safe', 'warning');
        }
    };

    try {
        txns = await apiFetch(`/transactions?user_id=${user.id}&limit=500`);
    } catch (e) {
        console.error('Fraud data fetch error:', e);
    }

    const fraudTxns = txns.filter(t => t.is_fraud);
    const safetyScore = txns.length ? Math.round(((txns.length - fraudTxns.length) / txns.length) * 100) : 100;

    return `
        <div class="fade-in">
            <div class="flex items-center justify-between mb-xl">
                <div>
                    <h1 style="font-size: 1.75rem; font-weight: 700; color: #111827; margin-bottom: 0.25rem;">Fraud Detection</h1>
                    <p style="font-size: 0.875rem; color: #6b7280;">Anomaly detection using Isolation Forest</p>
                </div>
            </div>

            <div class="grid grid-cols-3 mb-xl">
                <div class="stat-card" style="border-left: 3px solid #ef4444;">
                    <div class="stat-label">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line>
                            <line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>
                        Flagged Transactions
                    </div>
                    <div class="stat-value" style="color: #ef4444;">${fraudTxns.length}</div>
                    <div style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">
                        ${fraudTxns.length > 0 ? 'Requires attention' : 'All clear'}
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                        </svg>
                        Total Scanned
                    </div>
                    <div class="stat-value">${txns.length}</div>
                    <div style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">
                        Transactions analyzed
                    </div>
                </div>

                <div class="stat-card" style="border-left: 3px solid #10b981;">
                    <div class="stat-label">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                        Safety Score
                    </div>
                    <div class="stat-value" style="color: #10b981;">${safetyScore}%</div>
                    <div class="badge badge-success" style="margin-top: 0.5rem;">
                        ${safetyScore >= 95 ? 'Excellent' : safetyScore >= 85 ? 'Good' : 'Fair'}
                    </div>
                </div>
            </div>

            <div class="card mb-xl" style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-color: #3b82f6;">
                <div class="card-body">
                    <div style="display: flex; align-items: start; gap: 1rem;">
                        <div style="width: 48px; height: 48px; background: white; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                                <path d="M9 12l2 2 4-4"></path>
                            </svg>
                        </div>
                        <div style="flex: 1;">
                            <h3 style="font-size: 1rem; font-weight: 600; color: #1e40af; margin-bottom: 0.5rem;">
                                How Fraud Detection Works
                            </h3>
                            <p style="font-size: 0.875rem; color: #1e40af; line-height: 1.6; margin-bottom: 0.75rem;">
                                Our AI model uses Isolation Forest algorithm to detect anomalies in transaction patterns. 
                                It analyzes amount, time, location, and spending behavior to identify suspicious activity.
                            </p>
                            <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.8125rem; color: #1e40af;">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                                    </svg>
                                    Real-time Analysis
                                </div>
                                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.8125rem; color: #1e40af;">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <circle cx="12" cy="12" r="10"></circle>
                                        <polyline points="12 6 12 12 16 14"></polyline>
                                    </svg>
                                    24/7 Monitoring
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title" style="display: flex; align-items: center; gap: 0.5rem;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line>
                            <line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>
                        Flagged Transactions
                    </h2>
                </div>
                <div class="card-body" style="padding: 0;">
                    ${fraudTxns.length === 0 ? `
                        <div class="empty-state">
                            <div class="empty-state-icon" style="background: #d1fae5; color: #10b981;">
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                                    <path d="M9 12l2 2 4-4"></path>
                                </svg>
                            </div>
                            <p class="empty-state-title">Your account is secure</p>
                            <p class="empty-state-text">No suspicious transactions detected by our AI model</p>
                        </div>
                    ` : `
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Transaction</th>
                                    <th>Amount</th>
                                    <th>Risk Score</th>
                                    <th>Date</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${fraudTxns.map(tx => `
                                    <tr style="background: #fef2f2;">
                                        <td>
                                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                                <div style="width: 40px; height: 40px; background: #fee2e2; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center;">
                                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2">
                                                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                                                        <line x1="12" y1="9" x2="12" y2="13"></line>
                                                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                                                    </svg>
                                                </div>
                                                <div>
                                                    <div style="font-weight: 600; color: #111827;">${tx.description}</div>
                                                    <div style="font-size: 0.75rem; color: #6b7280;">${tx.category}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td style="font-weight: 700; font-size: 1rem; color: #ef4444;">
                                            ₹${tx.amount.toLocaleString()}
                                        </td>
                                        <td>
                                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                                <div style="flex: 1; height: 6px; background: #fee2e2; border-radius: 999px; overflow: hidden;">
                                                    <div style="height: 100%; background: #ef4444; width: ${(tx.fraud_score * 100).toFixed(0)}%;"></div>
                                                </div>
                                                <span style="font-size: 0.75rem; font-weight: 600; color: #ef4444;">
                                                    ${(tx.fraud_score * 100).toFixed(0)}%
                                                </span>
                                            </div>
                                        </td>
                                        <td style="color: #6b7280; font-size: 0.875rem;">
                                            ${new Date(tx.timestamp).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
    })}
                                        </td>
                                        <td>
                                            <button class="btn btn-secondary" style="padding: 0.5rem 1rem; font-size: 0.8125rem;" onclick="window.markSafe('${tx.id}')">
                                                Mark Safe
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `}
                </div>
            </div>
        </div>
    `;
}
