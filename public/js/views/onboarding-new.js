import { updateProfileInfo, authState } from '../auth.js';
import { navigateTo } from '../utils.js';

export default async function OnboardingView() {
    const { user } = authState.get();

    setTimeout(() => {
        const form = document.getElementById('onboarding-form');
        
        form?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const income = parseFloat(document.getElementById('income').value);
            const submitBtn = document.getElementById('submit-btn');
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Setting up...';

            try {
                await updateProfileInfo({ income });
                navigateTo('dashboard');
            } catch (error) {
                alert('Failed to save income. Please try again.');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Continue';
            }
        });
    }, 50);

    return `
        <div class="auth-card" style="max-width: 500px;">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="width: 56px; height: 56px; margin: 0 auto 1rem; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 1rem; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 16px rgba(16, 185, 129, 0.3);">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
                        <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                </div>
                <h1 style="font-size: 1.5rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem;">Welcome, ${user.name?.split(' ')[0] || 'User'}!</h1>
                <p style="font-size: 0.875rem; color: #6b7280;">Let's set up your financial profile</p>
            </div>

            <form id="onboarding-form">
                <div class="form-group">
                    <label class="form-label">Monthly Income (₹)</label>
                    <input type="number" id="income" class="form-input" placeholder="50000" min="0" step="1000" required autofocus>
                    <p style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">
                        This helps us provide personalized financial insights and recommendations
                    </p>
                </div>

                <button type="submit" id="submit-btn" class="btn btn-primary" style="width: 100%; margin-top: 1.5rem;">
                    Continue
                </button>
            </form>

            <div style="margin-top: 2rem; padding: 1rem; background: #f0fdf4; border-radius: 0.75rem; border: 1px solid #bbf7d0;">
                <div style="display: flex; gap: 0.75rem;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" style="flex-shrink: 0;">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                    </svg>
                    <div style="font-size: 0.8125rem; color: #166534; line-height: 1.5;">
                        <strong style="display: block; margin-bottom: 0.25rem;">Your data is secure</strong>
                        All information is encrypted and stored securely. We never share your data with third parties.
                    </div>
                </div>
            </div>
        </div>
    `;
}
