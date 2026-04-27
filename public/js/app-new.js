import { initAuth, authState, logout } from './auth.js';
import { navigateTo } from './utils.js';
import { initAIAssistant } from './components/ai-assistant.js';

// DOM Elements
const eAuthView = document.getElementById('auth-view');
const eMainApp = document.getElementById('main-app');
const eRouterView = document.getElementById('router-view');
const eSidebar = document.getElementById('sidebar');
const eSidebarToggle = document.getElementById('sidebar-toggle');
const eSidebarClose = document.getElementById('sidebar-close');
const eLogoutBtn = document.getElementById('btn-logout');
const eNavMenu = document.getElementById('nav-menu');
const eBottomNav = document.getElementById('bottom-nav');

// Navigation Items
const navItems = [
    { to: 'dashboard', icon: 'layout', label: 'Dashboard' },
    { to: 'transactions', icon: 'repeat', label: 'Transactions' },
    { to: 'budget', icon: 'pie-chart', label: 'Budget' },
    { to: 'fraud', icon: 'shield', label: 'Fraud Detection' },
    { to: 'risk', icon: 'bar-chart-2', label: 'Risk Analysis' },
    { to: 'insurance', icon: 'shield-check', label: 'Insurance' },
    { to: 'investments', icon: 'trending-up', label: 'Investments' },
    { to: 'ai-chat', icon: 'message-circle', label: 'AI Chat' },
    { to: 'profile', icon: 'user', label: 'Profile' }
];

// SVG Icons Map
const icons = {
    'layout': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>',
    'repeat': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>',
    'pie-chart': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path></svg>',
    'shield': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
    'bar-chart-2': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>',
    'shield-check': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><polyline points="9 12 11 14 15 10"></polyline></svg>',
    'trending-up': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>',
    'message-circle': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>',
    'user': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'
};

function renderNav(currentPath) {
    eNavMenu.innerHTML = navItems.map(item => `
        <a href="#${item.to}" class="nav-item ${currentPath === item.to ? 'active' : ''}">
            ${icons[item.icon]}
            <span>${item.label}</span>
        </a>
    `).join('');
}

// Router with optimized loading and debugging
const routes = {
    'login': () => {
        console.log('Loading login view...');
        return import('./views/login-new.js?v=4').then(m => m.default());
    },
    'onboarding': () => {
        console.log('Loading onboarding view...');
        return import('./views/onboarding-new.js?v=4').then(m => m.default());
    },
    'dashboard': () => {
        console.log('Loading dashboard view...');
        return import('./views/dashboard-new.js?v=4').then(m => m.default());
    },
    'transactions': () => {
        console.log('Loading transactions view...');
        return import('./views/transactions-new.js?v=4').then(m => m.default());
    },
    'budget': () => {
        console.log('Loading budget view...');
        return import('./views/budget-new.js?v=4').then(m => m.default());
    },
    'fraud': () => {
        console.log('Loading fraud view...');
        return import('./views/fraud-new.js?v=4').then(m => m.default());
    },
    'risk': () => {
        console.log('Loading risk view...');
        return import('./views/risk-new.js?v=4').then(m => m.default());
    },
    'insurance': () => {
        console.log('Loading insurance view...');
        return import('./views/insurance-redesigned.js?v=31').then(m => m.default());
    },
    'investments': () => {
        console.log('Loading investments view...');
        return import('./views/investments-new.js?v=4').then(m => m.default());
    },
    'ai-chat': () => {
        console.log('Loading AI chat view...');
        return import('./views/ai-chat-new.js?v=18').then(m => m.default());
    },
    'profile': () => {
        console.log('Loading profile view...');
        return import('./views/profile-new.js?v=4').then(m => m.default());
    },
};

let currentRouteId = 0;
let routeCache = new Map(); // Cache rendered routes to prevent unnecessary re-renders

async function handleRoute() {
    const routeId = ++currentRouteId;
    let path = window.location.hash.replace('#', '') || 'dashboard';
    const { user, loading } = authState.get();

    // Check if we're just switching back to the same route
    const currentPath = eRouterView?.getAttribute('data-current-path');
    if (currentPath === path && !loading && user) {
        console.log('Same route, skipping reload:', path);
        return;
    }

    // Show loading indicator immediately
    if (eRouterView) {
        eRouterView.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 200px; color: var(--text-secondary);">
                <div style="text-align: center;">
                    <div style="width: 32px; height: 32px; border: 3px solid var(--primary-100); border-top: 3px solid var(--primary); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem;"></div>
                    <p>Loading...</p>
                </div>
            </div>
        `;
    }

    if (loading) {
        eAuthView.classList.remove('hidden');
        eMainApp.classList.add('hidden');
        eBottomNav.classList.add('hidden');
        eAuthView.innerHTML = `
            <div style="text-align: center; color: white;">
                <div style="width: 48px; height: 48px; margin: 0 auto 1rem; background: rgba(255,255,255,0.2); border-radius: 1rem; display: flex; align-items: center; justify-content: center;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <line x1="12" y1="1" x2="12" y2="23"></line>
                        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                    </svg>
                </div>
                <p style="font-size: 0.875rem; font-weight: 500;">Loading FinA...</p>
            </div>`;
        return;
    }

    if (!user) {
        if (path !== 'login') return navigateTo('login');
        eMainApp.classList.add('hidden');
        eBottomNav.classList.add('hidden');
        eAuthView.classList.remove('hidden');
        try {
            const html = await routes[path]();
            if (routeId !== currentRouteId) return; // Route changed while loading
            eAuthView.innerHTML = html;
        } catch (e) {
            console.error("View render error:", e);
            eAuthView.innerHTML = `<div class="alert alert-danger">Error loading page. Please refresh.</div>`;
        }
        return;
    }

    // Onboarding check - redirect if income not set
    if (path !== 'onboarding' && path !== 'login' && (!user.income || user.income === 0)) {
        return navigateTo('onboarding');
    }

    // Handle onboarding route
    if (path === 'onboarding') {
        eMainApp.classList.add('hidden');
        eBottomNav.classList.add('hidden');
        eAuthView.classList.remove('hidden');
        try {
            const html = await routes[path]();
            if (routeId !== currentRouteId) return;
            eAuthView.innerHTML = html;
        } catch (e) {
            console.error("View render error:", e);
            eAuthView.innerHTML = `<div class="alert alert-danger">Error loading page. Please refresh.</div>`;
        }
        return;
    }

    if (path === 'login') return navigateTo('dashboard');

    eAuthView.classList.add('hidden');
    eMainApp.classList.remove('hidden');
    eBottomNav.classList.remove('hidden');

    renderNav(path);

    console.log('About to load route:', path);
    try {
        const routeFunction = routes[path] || routes['dashboard'];
        console.log('Route function found:', !!routeFunction);
        
        const html = await routeFunction();
        console.log('HTML generated, length:', html?.length);
        
        if (routeId !== currentRouteId) {
            console.log('Route changed while loading, aborting');
            return; // Route changed while loading
        }
        
        eRouterView.innerHTML = html;
        eRouterView.setAttribute('data-current-path', path); // Track current path
        eRouterView.classList.remove('fade-in');
        // Force reflow
        eRouterView.offsetHeight;
        eRouterView.classList.add('fade-in');
        console.log('Route loaded successfully:', path);
    } catch (e) {
        console.error("View load error for path:", path, e);
        eRouterView.innerHTML = `
            <div class="alert alert-danger" style="margin: 2rem;">
                <h3>Error Loading Page</h3>
                <p>Failed to load the ${path} page.</p>
                <details style="margin-top: 1rem;">
                    <summary>Error Details</summary>
                    <pre style="background: #f5f5f5; padding: 1rem; margin-top: 0.5rem; border-radius: 4px; overflow-x: auto;">${e.message}\n${e.stack}</pre>
                </details>
                <button onclick="location.reload()" class="btn btn-primary" style="margin-top: 1rem;">Refresh Page</button>
                <button onclick="window.location.hash = '#dashboard'" class="btn btn-secondary" style="margin-top: 1rem; margin-left: 0.5rem;">Go to Dashboard</button>
            </div>
        `;
    }
}

// Sidebar Toggle
eSidebarToggle?.addEventListener('click', () => {
    eSidebar.classList.add('open');
});

eSidebarClose?.addEventListener('click', () => {
    eSidebar.classList.remove('open');
});

// Close sidebar on navigation (mobile)
eNavMenu?.addEventListener('click', (e) => {
    if (e.target.closest('.nav-item')) {
        eSidebar.classList.remove('open');
    }
});

// Logout
eLogoutBtn?.addEventListener('click', () => {
    logout().then(() => navigateTo('login'));
});

// Initialize
export function mountApp() {
    initAuth();
    initAIAssistant(); // Now just logs a message, doesn't create UI

    authState.subscribe(({ user }) => {
        if (user) {
            document.getElementById('user-name').textContent = user.name || 'User';
            document.getElementById('user-email').textContent = user.email || '';
            const initials = user.name ? user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) : 'U';
            document.getElementById('user-avatar').textContent = initials;
        }
        handleRoute();
    });

    window.addEventListener('hashchange', () => {
        eSidebar.classList.remove('open');
        handleRoute();
    });

    // Prevent page reload on tab switching and handle visibility changes
    let isPageVisible = true;
    
    document.addEventListener('visibilitychange', () => {
        isPageVisible = !document.hidden;
        
        if (isPageVisible) {
            // Page became visible again - don't reload, just refresh auth state if needed
            console.log('Page became visible - checking auth state');
            const { user } = authState.get();
            if (user) {
                // Just update the UI elements, don't reload the entire page
                document.getElementById('user-name').textContent = user.name || 'User';
                document.getElementById('user-email').textContent = user.email || '';
                const initials = user.name ? user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) : 'U';
                document.getElementById('user-avatar').textContent = initials;
            }
        }
    });

    // Prevent beforeunload unless user is actually navigating away
    let isInternalNavigation = false;
    
    // Track internal navigation
    const originalNavigateTo = window.navigateTo;
    if (originalNavigateTo) {
        window.navigateTo = function(path) {
            isInternalNavigation = true;
            setTimeout(() => { isInternalNavigation = false; }, 100);
            return originalNavigateTo(path);
        };
    }

    // Prevent accidental page reloads
    window.addEventListener('beforeunload', (e) => {
        // Only show warning if user is actually trying to leave the site
        if (!isInternalNavigation && isPageVisible) {
            // Don't show warning for tab switches or app switches
            return;
        }
    });

    // Handle page focus/blur to maintain state
    window.addEventListener('focus', () => {
        console.log('Window focused - maintaining current state');
    });

    window.addEventListener('blur', () => {
        console.log('Window blurred - preserving state');
    });
}

mountApp();
