import { apiFetch } from '../utils.js';
import { authState } from '../auth.js';
import { navigateTo } from '../utils.js';

const CATEGORIES = [
    'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
    'Healthcare', 'Utilities', 'Housing', 'Education', 'Travel', 'Income', 'Other'
];

export function showEditTransactionModal(transaction, onSuccess) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h2 class="modal-title">Edit Transaction</h2>
                <button class="modal-close" id="close-edit-modal">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="modal-body">
                <form id="edit-transaction-form">
                    <div class="form-group">
                        <label class="form-label">Type</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                            <label style="display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; border: 2px solid #e5e7eb; border-radius: 0.5rem; cursor: pointer;">
                                <input type="radio" name="edit-type" value="expense" ${transaction.type === 'expense' ? 'checked' : ''} style="width: 16px; height: 16px;">
                                <span style="font-weight: 500;">Expense</span>
                            </label>
                            <label style="display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; border: 2px solid #e5e7eb; border-radius: 0.5rem; cursor: pointer;">
                                <input type="radio" name="edit-type" value="income" ${transaction.type === 'income' ? 'checked' : ''} style="width: 16px; height: 16px;">
                                <span style="font-weight: 500;">Income</span>
                            </label>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Amount (₹)</label>
                        <input type="number" id="edit-amount" class="form-input" value="${transaction.amount}" min="0" step="0.01" required>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Description</label>
                        <input type="text" id="edit-description" class="form-input" value="${transaction.description}" required>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Category</label>
                        <select id="edit-category" class="form-input">
                            <option value="">Auto-detect (AI)</option>
                            ${CATEGORIES.map(cat => `<option value="${cat}" ${transaction.category === cat ? 'selected' : ''}>${cat}</option>`).join('')}
                        </select>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Location (Optional)</label>
                        <input type="text" id="edit-location" class="form-input" value="${transaction.location || ''}">
                    </div>

                    <div style="display: flex; gap: 0.75rem; margin-top: 1.5rem;">
                        <button type="button" class="btn" id="cancel-edit-btn" style="flex: 1;">Cancel</button>
                        <button type="submit" class="btn btn-primary" id="submit-edit-btn" style="flex: 1;">Save Changes</button>
                    </div>
                </form>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    const closeModal = () => modal.remove();
    document.getElementById('close-edit-modal').addEventListener('click', closeModal);
    document.getElementById('cancel-edit-btn').addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });

    document.getElementById('edit-transaction-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = document.getElementById('submit-edit-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Saving...';

        const formData = {
            type: document.querySelector('input[name="edit-type"]:checked').value,
            amount: parseFloat(document.getElementById('edit-amount').value),
            description: document.getElementById('edit-description').value,
            category: document.getElementById('edit-category').value || null,
            location: document.getElementById('edit-location').value || ''
        };

        try {
            await apiFetch(`/transactions/${transaction.id}`, {
                method: 'PUT',
                body: JSON.stringify(formData)
            });
            window.showToast('Transaction updated', 'success');
            closeModal();
            if (onSuccess) onSuccess();
        } catch (error) {
            window.showToast('Failed to update: ' + error.message, 'warning');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Save Changes';
        }
    });
}
