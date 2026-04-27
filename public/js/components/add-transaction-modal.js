import { apiFetch } from '../utils.js';
import { authState } from '../auth.js';

const CATEGORIES = [
    'Food & Dining',
    'Transportation',
    'Shopping',
    'Entertainment',
    'Healthcare',
    'Utilities',
    'Housing',
    'Education',
    'Travel',
    'Income',
    'Other'
];

export function showAddTransactionModal(onSuccess) {
    const { user } = authState.get();
    
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h2 class="modal-title">Add Transaction</h2>
                <button class="modal-close" id="close-modal">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="modal-body">
                <form id="add-transaction-form">
                    <div class="form-group">
                        <label class="form-label">Type</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                            <label style="display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; border: 2px solid #e5e7eb; border-radius: 0.5rem; cursor: pointer; transition: all 0.2s;">
                                <input type="radio" name="type" value="expense" checked style="width: 16px; height: 16px;">
                                <span style="font-weight: 500;">Expense</span>
                            </label>
                            <label style="display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; border: 2px solid #e5e7eb; border-radius: 0.5rem; cursor: pointer; transition: all 0.2s;">
                                <input type="radio" name="type" value="income" style="width: 16px; height: 16px;">
                                <span style="font-weight: 500;">Income</span>
                            </label>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Amount (₹)</label>
                        <input type="number" id="amount" class="form-input" placeholder="1000" min="0" step="0.01" required autofocus>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Description</label>
                        <input type="text" id="description" class="form-input" placeholder="e.g., Grocery shopping at Reliance Fresh" required>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Category</label>
                        <select id="category" class="form-input">
                            <option value="">Auto-detect (AI)</option>
                            ${CATEGORIES.map(cat => `<option value="${cat}">${cat}</option>`).join('')}
                        </select>
                        <p style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">
                            Leave empty to let AI categorize automatically
                        </p>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Location (Optional)</label>
                        <input type="text" id="location" class="form-input" placeholder="e.g., Mumbai, India">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Date & Time</label>
                        <input type="datetime-local" id="timestamp" class="form-input" required>
                    </div>

                    <div style="display: flex; gap: 0.75rem; margin-top: 1.5rem;">
                        <button type="button" class="btn" id="cancel-btn" style="flex: 1;">Cancel</button>
                        <button type="submit" class="btn btn-primary" id="submit-btn" style="flex: 1;">Add Transaction</button>
                    </div>
                </form>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Set default timestamp to now
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('timestamp').value = now.toISOString().slice(0, 16);

    // Close handlers
    const closeModal = () => {
        modal.remove();
    };

    document.getElementById('close-modal').addEventListener('click', closeModal);
    document.getElementById('cancel-btn').addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Form submission
    document.getElementById('add-transaction-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = document.getElementById('submit-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Adding...';

        const formData = {
            user_id: user.id,
            type: document.querySelector('input[name="type"]:checked').value,
            amount: parseFloat(document.getElementById('amount').value),
            description: document.getElementById('description').value,
            category: document.getElementById('category').value || null,
            location: document.getElementById('location').value || '',
            timestamp: new Date(document.getElementById('timestamp').value).toISOString()
        };

        try {
            await apiFetch('/transactions/', {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            
            closeModal();
            if (onSuccess) onSuccess();
        } catch (error) {
            alert('Failed to add transaction: ' + error.message);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Add Transaction';
        }
    });
}
