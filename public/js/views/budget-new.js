import { apiFetch } from '../utils.js';
import { authState } from '../auth.js';
import { showAddBudgetModal } from '../components/add-budget-modal.js';
import '../components/toast.js';

export default async function BudgetView() {
    const { user } = authState.get();
    let budgets = [];
    let transactions = [];

    window.openAddBudget = () => {
        showAddBudgetModal(async () => {
            const { navigateTo } = await import('../utils.js');
            navigateTo('dashboard');
            setTimeout(() => navigateTo('budget'), 50);
        });
    };

    try {
        // Fetch both budgets and transactions
        [budgets, transactions] = await Promise.all([
            apiFetch(`/budgets?user_id=${user.id}`),
            apiFetch(`/transactions?user_id=${user.id}`)
        ]);
    } catch (e) {
        console.error('Budget fetch error:', e);
    }

    // Calculate spending per category for current month
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();
    
    const spendingByCategory = {};
    
    transactions.forEach(txn => {
        // Handle both 'date' and 'timestamp' fields
        const txnDate = new Date(txn.timestamp || txn.date);
        if (txnDate.getMonth() === currentMonth && txnDate.getFullYear() === currentYear && txn.type === 'expense') {
            const category = txn.category || 'Other';
            spendingByCategory[category] = (spendingByCategory[category] || 0) + Math.abs(txn.amount);
        }
    });
    
    console.log('Budget calculations:', { spendingByCategory, transactions: transactions.length });

    return `
        <div class="fade-in">
            <div class="flex items-center justify-between mb-xl">
                <div>
                    <h1 style="font-size: 1.75rem; font-weight: 700; color: #111827; margin-bottom: 0.25rem;">Budget Management</h1>
                    <p style="font-size: 0.875rem; color: #6b7280;">Track and manage your spending limits</p>
                </div>
                <button class="btn btn-primary" onclick="window.openAddBudget()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    Add Budget
                </button>
            </div>

            ${budgets.length === 0 ? `
                <div class="card">
                    <div class="card-body">
                        <div class="empty-state">
                            <div class="empty-state-icon">
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
                                    <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
                                </svg>
                            </div>
                            <p class="empty-state-title">No budgets set</p>
                            <p class="empty-state-text">Create your first budget to start tracking spending</p>
                            <button class="btn btn-primary" style="margin-top: 1.5rem;" onclick="window.openAddBudget()">
                                Create Budget
                            </button>
                        </div>
                    </div>
                </div>
            ` : `
                <div class="grid grid-cols-2">
                    ${budgets.map(budget => {
                        const spent = spendingByCategory[budget.category] || 0;
                        const limit = budget.limit_amount;
                        const percentage = limit > 0 ? Math.min(100, (spent / limit) * 100) : 0;
                        const isOverBudget = percentage > 100;
                        const isWarning = percentage > 80 && percentage <= 100;
                        
                        let barColor = '#3b82f6'; // blue
                        if (isOverBudget) barColor = '#ef4444'; // red
                        else if (isWarning) barColor = '#f59e0b'; // orange
                        
                        return `
                        <div class="card">
                            <div class="card-body">
                                <h3 style="font-size: 1rem; font-weight: 600; color: #111827; margin-bottom: 1rem;">${budget.category}</h3>
                                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem;">
                                    <div style="font-size: 1.5rem; font-weight: 700; color: #111827;">
                                        ₹${limit.toLocaleString()}
                                    </div>
                                    <div style="font-size: 0.875rem; color: #6b7280;">
                                        ₹${spent.toLocaleString()} spent
                                    </div>
                                </div>
                                <div style="height: 8px; background: #f3f4f6; border-radius: 999px; overflow: hidden; margin-bottom: 0.5rem;">
                                    <div style="height: 100%; background: ${barColor}; width: ${percentage}%; border-radius: 999px; transition: width 0.3s ease;"></div>
                                </div>
                                <div style="font-size: 0.75rem; color: ${isOverBudget ? '#ef4444' : isWarning ? '#f59e0b' : '#6b7280'}; font-weight: ${isOverBudget || isWarning ? '600' : '400'};">
                                    ${percentage.toFixed(1)}% used ${isOverBudget ? '(Over budget!)' : isWarning ? '(Warning)' : ''}
                                </div>
                            </div>
                        </div>
                    `;
                    }).join('')}
                </div>
            `}
        </div>
    `;
}
