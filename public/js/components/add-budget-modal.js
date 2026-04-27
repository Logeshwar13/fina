import { apiFetch } from '../utils.js';
import { authState } from '../auth.js';
import { navigateTo } from '../utils.js';

export function showAddBudgetModal(onSuccess) {
    const { user } = authState.get();

    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 400px;">
            <div class="modal-header">
                <h2 class="modal-title">Add Budget</h2>
                <button class="modal-close" id="close-budget-modal">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="modal-body">
                <form id="add-budget-form">
                    <div class="form-group">
                        <label class="form-label">Category</label>
                        <select id="budget-category" class="form-input" required>
                            <option value="">Select a category</option>
                            <option value="Food & Dining">Food & Dining</option>
                            <option value="Transportation">Transportation</option>
                            <option value="Shopping">Shopping</option>
                            <option value="Entertainment">Entertainment</option>
                            <option value="Healthcare">Healthcare</option>
                            <option value="Utilities">Utilities</option>
                            <option value="Housing">Housing</option>
                            <option value="Travel">Travel</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Monthly Limit (₹)</label>
                        <input type="number" id="budget-limit" class="form-input" placeholder="5000" min="1" step="1" required autofocus>
                    </div>

                    <div style="display: flex; gap: 0.75rem; margin-top: 1.5rem;">
                        <button type="button" class="btn" id="cancel-budget-btn" style="flex: 1;">Cancel</button>
                        <button type="submit" class="btn btn-primary" id="submit-budget-btn" style="flex: 1;">Add Budget</button>
                    </div>
                </form>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    const closeModal = () => modal.remove();
    document.getElementById('close-budget-modal').addEventListener('click', closeModal);
    document.getElementById('cancel-budget-btn').addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });

    document.getElementById('add-budget-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('submit-budget-btn');
        btn.disabled = true;
        btn.textContent = 'Saving...';

        try {
            await apiFetch('/budgets/', {
                method: 'POST',
                body: JSON.stringify({
                    category: document.getElementById('budget-category').value,
                    limit_amount: parseFloat(document.getElementById('budget-limit').value),
                    user_id: user.id
                })
            });
            window.showToast('Budget added successfully!', 'success');
            closeModal();
            if (onSuccess) onSuccess();
        } catch (error) {
            window.showToast('Failed to add budget check console', 'warning');
            console.error(error);
            btn.disabled = false;
            btn.textContent = 'Add Budget';
        }
    });
}
