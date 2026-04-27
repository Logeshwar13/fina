import { apiFetch } from '../utils.js';
import { authState } from '../auth.js';

export default async function InvestmentsView() {
    const { user } = authState.get();
    let insightsData = [];
    let loadingError = false;

    try {
        const response = await apiFetch('/ai/insights', {
            method: 'POST',
            body: JSON.stringify({ user_id: user.id, context: "Focus on investments and savings." })
        });
        if (response && response.insights) {
            insightsData = response.insights;
        }
    } catch (e) {
        console.warn('AI insights failed, trying standard insights', e);
        try {
            const fallback = await apiFetch(`/insights?user_id=${user.id}`);
            if (fallback && fallback.insights) {
                insightsData = fallback.insights;
            }
        } catch (e2) {
            loadingError = true;
        }
    }

    return `
        <div class="fade-in">
            <div class="flex items-center justify-between mb-xl">
                <div>
                    <h1 style="font-size: 1.75rem; font-weight: 700; color: #111827; margin-bottom: 0.25rem;">Investment Insights</h1>
                    <p style="font-size: 0.875rem; color: #6b7280;">Investment recommendations</p>
                </div>
            </div>

            <div class="card">
                <div class="card-body">
                    ${insightsData.length > 0 ? `
                        <div class="grid" style="gap: 1rem;">
                            ${insightsData.map(i => `
                                <div class="card" style="border-left: 4px solid ${i.type === 'positive' ? '#10b981' : i.type === 'warning' ? '#f59e0b' : '#3b82f6'};">
                                    <div class="card-body" style="padding: 1.25rem; display: flex; gap: 1rem; align-items: flex-start;">
                                        <div style="font-size: 1.5rem;">${i.icon || '💡'}</div>
                                        <div>
                                            <h3 style="font-size: 1rem; font-weight: 600; color: #111827; margin-bottom: 0.25rem;">${i.title}</h3>
                                            <p style="font-size: 0.875rem; color: #4b5563;">${i.message}</p>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : `
                        <div class="empty-state">
                            <div class="empty-state-icon">
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                                    <polyline points="17 6 23 6 23 12"></polyline>
                                </svg>
                            </div>
                            <p class="empty-state-title">No investment insights available right now</p>
                            <p class="empty-state-text">Check back later once you add more transactions</p>
                        </div>
                    `}
                </div>
            </div>
        </div>
    `;
}
