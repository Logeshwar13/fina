import { login, register } from '../auth.js';
import { navigateTo } from '../utils.js';

export default async function LoginView() {
    setTimeout(() => {
        const form = document.getElementById('login-form');
        const toggleBtn = document.getElementById('toggle-mode');
        const formTitle = document.getElementById('form-title');
        const formSubtitle = document.getElementById('form-subtitle');
        const submitBtn = document.getElementById('submit-btn');
        const nameGroup = document.getElementById('name-group');
        const confirmPasswordGroup = document.getElementById('confirm-password-group');
        const togglePassword = document.getElementById('toggle-password');
        const toggleConfirmPassword = document.getElementById('toggle-confirm-password');
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirm-password');
        
        let isLogin = true;

        // Password visibility toggles
        togglePassword?.addEventListener('click', () => {
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            togglePassword.innerHTML = type === 'password' 
                ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>'
                : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>';
        });

        toggleConfirmPassword?.addEventListener('click', () => {
            const type = confirmPasswordInput.type === 'password' ? 'text' : 'password';
            confirmPasswordInput.type = type;
            toggleConfirmPassword.innerHTML = type === 'password' 
                ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>'
                : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>';
        });

        toggleBtn?.addEventListener('click', () => {
            isLogin = !isLogin;
            if (isLogin) {
                formTitle.textContent = 'Welcome back';
                formSubtitle.textContent = 'Sign in to your account to continue';
                submitBtn.textContent = 'Sign In';
                toggleBtn.innerHTML = `Don't have an account? <strong>Sign up</strong>`;
                nameGroup.style.display = 'none';
                confirmPasswordGroup.style.display = 'none';
            } else {
                formTitle.textContent = 'Create account';
                formSubtitle.textContent = 'Start managing your finances today';
                submitBtn.textContent = 'Create Account';
                toggleBtn.innerHTML = `Already have an account? <strong>Sign in</strong>`;
                nameGroup.style.display = 'block';
                confirmPasswordGroup.style.display = 'block';
            }
        });

        form?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password')?.value;
            const name = document.getElementById('name')?.value;

            if (!isLogin && password !== confirmPassword) {
                alert('Passwords do not match');
                return;
            }

            if (!isLogin && password.length < 6) {
                alert('Password must be at least 6 characters');
                return;
            }

            submitBtn.disabled = true;
            submitBtn.textContent = isLogin ? 'Signing in...' : 'Creating account...';

            try {
                if (isLogin) {
                    await login(email, password);
                    navigateTo('dashboard');
                } else {
                    await register(name || email.split('@')[0], email, password);
                    // Redirect to onboarding for new users
                    navigateTo('onboarding');
                }
            } catch (error) {
                alert(error.message || 'Authentication failed');
                submitBtn.disabled = false;
                submitBtn.textContent = isLogin ? 'Sign In' : 'Create Account';
            }
        });
    }, 50);

    return `
        <div class="auth-card">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="width: 56px; height: 56px; margin: 0 auto 1rem; background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%); border-radius: 1rem; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 16px rgba(37, 99, 235, 0.3);">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
                        <line x1="12" y1="1" x2="12" y2="23"></line>
                        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                    </svg>
                </div>
                <h1 id="form-title" style="font-size: 1.5rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem;">Welcome back</h1>
                <p id="form-subtitle" style="font-size: 0.875rem; color: #6b7280;">Sign in to your account to continue</p>
            </div>

            <form id="login-form">
                <div id="name-group" class="form-group" style="display: none;">
                    <label class="form-label">Full Name</label>
                    <input type="text" id="name" class="form-input" placeholder="John Doe">
                </div>

                <div class="form-group">
                    <label class="form-label">Email</label>
                    <input type="email" id="email" class="form-input" placeholder="you@example.com" required>
                </div>

                <div class="form-group">
                    <label class="form-label">Password</label>
                    <div style="position: relative;">
                        <input type="password" id="password" class="form-input" placeholder="••••••••" required style="padding-right: 2.5rem;">
                        <button type="button" id="toggle-password" style="position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); background: none; border: none; color: #9ca3af; cursor: pointer; padding: 0.25rem; display: flex; align-items: center;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                <circle cx="12" cy="12" r="3"></circle>
                            </svg>
                        </button>
                    </div>
                </div>

                <div id="confirm-password-group" class="form-group" style="display: none;">
                    <label class="form-label">Confirm Password</label>
                    <div style="position: relative;">
                        <input type="password" id="confirm-password" class="form-input" placeholder="••••••••" style="padding-right: 2.5rem;">
                        <button type="button" id="toggle-confirm-password" style="position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); background: none; border: none; color: #9ca3af; cursor: pointer; padding: 0.25rem; display: flex; align-items: center;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                <circle cx="12" cy="12" r="3"></circle>
                            </svg>
                        </button>
                    </div>
                </div>

                <button type="submit" id="submit-btn" class="btn btn-primary" style="width: 100%; margin-top: 1.5rem;">
                    Sign In
                </button>
            </form>

            <div style="text-align: center; margin-top: 1.5rem; font-size: 0.875rem; color: #6b7280;">
                <button type="button" id="toggle-mode" style="background: none; border: none; color: #6b7280; cursor: pointer; font-size: 0.875rem;">
                    Don't have an account? <strong style="color: #2563eb;">Sign up</strong>
                </button>
            </div>
        </div>
    `;
}
