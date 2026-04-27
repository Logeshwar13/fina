import { apiFetch } from '../utils.js';
import { authState, updateProfileInfo, logout } from '../auth.js';
import { navigateTo } from '../utils.js';
import '../components/toast.js';

export default async function ProfileView() {
    const { user } = authState.get();

    setTimeout(() => {
        const incomeForm = document.getElementById('income-form');
        const logoutBtn = document.getElementById('logout-btn');

        incomeForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const income = parseFloat(document.getElementById('income-input').value);
            const submitBtn = e.target.querySelector('button[type="submit"]');

            submitBtn.disabled = true;
            submitBtn.textContent = 'Saving...';

            try {
                await updateProfileInfo({ income });
                window.showToast('Income updated successfully!', 'success');
                submitBtn.textContent = 'Save Changes';
            } catch (error) {
                window.showToast('Failed to update income', 'warning');
                submitBtn.textContent = 'Save Changes';
            } finally {
                submitBtn.disabled = false;
            }
        });

        logoutBtn?.addEventListener('click', async () => {
            await logout();
            navigateTo('login');
        });
    }, 50);

    return `
        <div class="fade-in">
            <div class="flex items-center justify-between mb-xl">
                <div>
                    <h1 style="font-size: 1.75rem; font-weight: 700; color: #111827; margin-bottom: 0.25rem;">Profile Settings</h1>
                    <p style="font-size: 0.875rem; color: #6b7280;">Manage your account and preferences</p>
                </div>
            </div>

            <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Personal Information</h2>
                    </div>
                    <div class="card-body">
                        <div class="form-group">
                            <label class="form-label">Name</label>
                            <input type="text" class="form-input" value="${user.name || ''}" readonly>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-input" value="${user.email || ''}" readonly>
                        </div>
                        <div class="form-group">
                            <label class="form-label">User ID</label>
                            <input type="text" class="form-input" value="${user.id}" readonly style="font-family: monospace; font-size: 0.75rem;">
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Financial Settings</h2>
                    </div>
                    <div class="card-body">
                        <form id="income-form">
                            <div class="form-group">
                                <label class="form-label">Monthly Income (₹)</label>
                                <input type="number" id="income-input" class="form-input" value="${user.income || 0}" min="0" step="1000" required>
                                <p style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">
                                    This helps us provide better financial insights
                                </p>
                            </div>
                            <button type="submit" class="btn btn-primary" style="width: 100%;">
                                Save Changes
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <div class="card" style="margin-top: 1.5rem; border-color: #ef4444;">
                <div class="card-header" style="background: #fef2f2;">
                    <h2 class="card-title" style="color: #ef4444;">Danger Zone</h2>
                </div>
                <div class="card-body">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div>
                            <h3 style="font-weight: 600; color: #111827; margin-bottom: 0.25rem;">Sign Out</h3>
                            <p style="font-size: 0.875rem; color: #6b7280;">Sign out of your account on this device</p>
                        </div>
                        <button id="logout-btn" class="btn" style="background: #ef4444; color: white; border-color: #ef4444;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                                <polyline points="16 17 21 12 16 7"></polyline>
                                <line x1="21" y1="12" x2="9" y2="12"></line>
                            </svg>
                            Sign Out
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}
