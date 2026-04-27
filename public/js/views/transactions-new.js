import { apiFetch, navigateTo } from '../utils.js';
import { authState } from '../auth.js';
import { showAddTransactionModal } from '../components/add-transaction-modal.js';
import { showEditTransactionModal } from '../components/edit-transaction-modal.js';
import '../components/toast.js';

window.openEditModal = (txId) => {
    try {
        const tx = txns.find(t => t.id === txId);
        if (!tx) return;
        showEditTransactionModal(tx, () => {
            // Just reload transactions page
            setTimeout(() => navigateTo('transactions'), 100);
        });
    } catch (e) {
        console.error(e);
    }
};

const CAT_COLORS = {
    'Food & Dining': 'badge-warning',
    'Transportation': 'badge-info',
    'Shopping': 'badge-danger',
    'Entertainment': 'badge-success',
    'Healthcare': 'badge-danger',
    'Utilities': 'badge-warning',
    'Housing': 'badge-info',
    'Education': 'badge-success',
    'Travel': 'badge-info',
    'Income': 'badge-success',
    'Other': 'badge-info'
};

let txns = [];

export default async function TransactionsView() {
    const { user } = authState.get();

    try {
        txns = await apiFetch(`/transactions/?user_id=${user.id}&limit=500`);
    } catch {
        txns = [];
    }

    const sorted = [...txns].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    setTimeout(() => {
        const searchInput = document.getElementById('txn-search');
        const monthFilter = document.getElementById('month-filter');
        const tableBody = document.getElementById('txn-table-body');
        const countEl = document.getElementById('txn-count');
        const addBtn = document.getElementById('add-txn-btn');

        // Populate month filter options
        const months = [...new Set(sorted.map(tx => {
            const date = new Date(tx.timestamp);
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        }))].sort().reverse();

        monthFilter.innerHTML = '<option value="">All months</option>' + 
            months.map(monthKey => {
                const [year, month] = monthKey.split('-');
                const date = new Date(year, month - 1);
                const label = date.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' });
                return `<option value="${monthKey}">${label}</option>`;
            }).join('');

        addBtn?.addEventListener('click', () => {
            showAddTransactionModal(() => {
                // Reload page after successful add
                navigateTo('transactions');
            });
        });

        function renderTable(searchQuery = '', selectedMonth = '') {
            const q = searchQuery.toLowerCase();
            let filtered = sorted.filter(t => {
                const matchesSearch = !q || 
                    t.description?.toLowerCase().includes(q) ||
                    t.category?.toLowerCase().includes(q);
                
                const matchesMonth = !selectedMonth || (() => {
                    const date = new Date(t.timestamp);
                    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
                    return monthKey === selectedMonth;
                })();
                
                return matchesSearch && matchesMonth;
            });

            countEl.textContent = `${filtered.length} of ${txns.length} transactions`;

            if (filtered.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="6">
                            <div class="empty-state">
                                <div class="empty-state-icon">
                                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <circle cx="11" cy="11" r="8"></circle>
                                        <path d="m21 21-4.35-4.35"></path>
                                    </svg>
                                </div>
                                <p class="empty-state-title">No transactions found</p>
                                <p class="empty-state-text">${selectedMonth ? 'No transactions for selected month' : 'Try adjusting your search'}</p>
                            </div>
                        </td>
                    </tr>`;
                return;
            }

            // Group transactions by month
            const groupedByMonth = {};
            filtered.forEach(tx => {
                const date = new Date(tx.timestamp);
                const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
                const monthLabel = date.toLocaleDateString('en-IN', { 
                    month: 'long', 
                    year: 'numeric' 
                });
                
                if (!groupedByMonth[monthKey]) {
                    groupedByMonth[monthKey] = {
                        label: monthLabel,
                        transactions: [],
                        date: date
                    };
                }
                groupedByMonth[monthKey].transactions.push(tx);
            });

            // Sort months in descending order (newest first)
            const sortedMonths = Object.entries(groupedByMonth)
                .sort(([a], [b]) => b.localeCompare(a));

            let html = '';
            
            sortedMonths.forEach(([monthKey, monthData], monthIndex) => {
                // Add month separator (only if not filtering by specific month)
                if (!selectedMonth) {
                    html += `
                        <tr class="month-separator">
                            <td colspan="6">
                                <div class="month-divider">
                                    <div class="month-line"></div>
                                    <div class="month-label">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                                            <line x1="16" y1="2" x2="16" y2="6"></line>
                                            <line x1="8" y1="2" x2="8" y2="6"></line>
                                            <line x1="3" y1="10" x2="21" y2="10"></line>
                                        </svg>
                                        ${monthData.label}
                                        <span class="month-count">${monthData.transactions.length} transactions</span>
                                    </div>
                                    <div class="month-line"></div>
                                </div>
                            </td>
                        </tr>
                    `;
                }

                // Add transactions for this month
                monthData.transactions.forEach(tx => {
                    const catClass = CAT_COLORS[tx.category] || 'badge-info';
                    const isIncome = tx.type === 'income';

                    // Highlight search terms
                    let description = tx.description;
                    if (q && description.toLowerCase().includes(q)) {
                        const regex = new RegExp(`(${q})`, 'gi');
                        description = description.replace(regex, '<span class="search-highlight">$1</span>');
                    }

                    html += `
                        <tr class="transaction-row">
                            <td>
                                <div style="display: flex; align-items: center; gap: 0.75rem;">
                                    <div style="width: 40px; height: 40px; border-radius: 0.75rem; background: ${isIncome ? '#d1fae5' : '#f3f4f6'}; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="${isIncome ? '#10b981' : '#6b7280'}" stroke-width="2">
                                            ${isIncome ?
                            '<line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline>' :
                            '<line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline>'
                        }
                                        </svg>
                                    </div>
                                    <div>
                                        <div style="font-weight: 600; color: #111827; margin-bottom: 0.125rem;">${description}</div>
                                        <div style="font-size: 0.75rem; color: #9ca3af;">
                                            ${new Date(tx.timestamp).toLocaleDateString('en-IN', {
                            day: 'numeric',
                            month: 'short',
                            hour: '2-digit',
                            minute: '2-digit'
                        })}
                                        </div>
                                    </div>
                                </div>
                            </td>
                            <td><span class="badge ${catClass}">${tx.category}</span></td>
                            <td style="font-weight: 700; font-size: 1rem; color: ${isIncome ? '#10b981' : '#111827'};">
                                ${isIncome ? '+' : '-'}₹${tx.amount.toLocaleString()}
                            </td>
                            <td>${tx.location || '-'}</td>
                            <td>
                                <span class="badge ${tx.is_fraud ? 'badge-danger' : 'badge-success'}">
                                    ${tx.is_fraud ? 'Flagged' : 'Safe'}
                                </span>
                            </td>
                            <td>
                                <button class="icon-btn" style="width: 32px; height: 32px;" onclick="window.openEditModal('${tx.id}')">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                                    </svg>
                                </button>
                            </td>
                        </tr>
                    `;
                });
            });

            tableBody.innerHTML = html;
        }

        renderTable();
        searchInput?.addEventListener('input', (e) => renderTable(e.target.value, monthFilter.value));
        monthFilter?.addEventListener('change', (e) => renderTable(searchInput.value, e.target.value));
    }, 50);

    return `
        <div class="fade-in">
            <div class="flex items-center justify-between mb-xl">
                <div>
                    <h1 style="font-size: 1.75rem; font-weight: 700; color: #111827; margin-bottom: 0.25rem;">Transactions</h1>
                    <p id="txn-count" style="font-size: 0.875rem; color: #6b7280;">${txns.length} transactions</p>
                </div>
                <button class="btn btn-primary" id="add-txn-btn">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    Add Transaction
                </button>
            </div>

            <div class="grid grid-cols-4 mb-xl">
                <div class="stat-card">
                    <div class="stat-label">Total Transactions</div>
                    <div class="stat-value">${txns.length}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">This Month</div>
                    <div class="stat-value">${txns.filter(t => {
        const date = new Date(t.timestamp);
        const now = new Date();
        return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
    }).length}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Income</div>
                    <div class="stat-value" style="color: #10b981;">
                        ₹${txns.filter(t => t.type === 'income').reduce((sum, t) => sum + t.amount, 0).toLocaleString()}
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Expenses</div>
                    <div class="stat-value" style="color: #ef4444;">
                        ₹${txns.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0).toLocaleString()}
                    </div>
                </div>
            </div>

            <div class="card mb-lg">
                <div class="card-header">
                    <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                        <div class="search-bar" style="flex: 1; min-width: 300px;">
                            <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="11" cy="11" r="8"></circle>
                                <path d="m21 21-4.35-4.35"></path>
                            </svg>
                            <input type="text" id="txn-search" placeholder="Search by description or category..." class="search-input">
                        </div>
                        <div style="display: flex; gap: 0.5rem; align-items: center;">
                            <label for="month-filter" style="font-size: 0.875rem; color: var(--gray-600); white-space: nowrap;">Filter by month:</label>
                            <select id="month-filter" class="form-input" style="min-width: 150px; padding: 0.5rem;">
                                <option value="">All months</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Transaction</th>
                            <th>Category</th>
                            <th>Amount</th>
                            <th>Location</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="txn-table-body">
                        <tr><td colspan="6" style="text-align: center; padding: 2rem;">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;
}
