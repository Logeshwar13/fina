import { Store, apiFetch } from './utils.js';

// Supabase Configuration - Using your existing credentials
const SUPABASE_URL = "https://tvxstddevrwdllswrxog.supabase.co";
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2eHN0ZGRldnJ3ZGxsc3dyeG9nIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcwMjQ1OTYsImV4cCI6MjA5MjYwMDU5Nn0.pRx97SPnkm5exZ4ECrqn3aEhooJIlLkrsH5z2Y8bW00";

export const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

export const authState = new Store({ user: null, loading: true });

// Fetch profile from backend users table
async function fetchProfile(authUser) {
    try {
        return await apiFetch(`/users/${authUser.id}`);
    } catch (error) {
        console.warn('Profile fetch failed:', error.message);
        // Return a basic profile if fetch fails
        return {
            id: authUser.id,
            email: authUser.email,
            name: authUser.email.split('@')[0],
            income: 0,
            goals_json: []
        };
    }
}

// Create profile row in backend users table
async function createProfile(authUser, name) {
    try {
        return await apiFetch('/users/', {
            method: 'POST',
            body: JSON.stringify({
                id: authUser.id,
                name: name || authUser.email.split('@')[0],
                email: authUser.email,
                income: 0,
                goals_json: []
            })
        });
    } catch (error) {
        console.warn('Profile creation failed:', error.message);
        // Return a basic profile if creation fails
        return {
            id: authUser.id,
            email: authUser.email,
            name: name || authUser.email.split('@')[0],
            income: 0,
            goals_json: []
        };
    }
}

// Init auth listener
export function initAuth() {
    // Initial Session Check
    supabase.auth.getSession().then(async ({ data: { session } }) => {
        if (session?.user) {
            const profile = await fetchProfile(session.user);
            authState.set({ 
                user: profile || { 
                    id: session.user.id, 
                    email: session.user.email, 
                    name: session.user.email 
                }, 
                loading: false 
            });
        } else {
            authState.set({ user: null, loading: false });
        }
    });

    // Listen to state changes
    supabase.auth.onAuthStateChange(async (event, session) => {
        if (session?.user) {
            const profile = await fetchProfile(session.user);
            authState.set({ user: profile, loading: false });
        } else {
            authState.set({ user: null, loading: false });
        }
    });
}

// Login
export async function login(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw new Error(error.message);
    const profile = await fetchProfile(data.user);
    authState.set({ user: profile || { id: data.user.id, email, name: email } });
    return profile;
}

// Register
export async function register(name, email, password) {
    const { data, error } = await supabase.auth.signUp({ email, password });
    if (error) throw new Error(error.message);
    const profile = await createProfile(data.user, name);
    authState.set({ user: profile || { id: data.user.id, email, name } });
    return profile;
}

// Logout
export async function logout() {
    await supabase.auth.signOut();
    authState.set({ user: null });
}

// Update Profile
export async function updateProfileInfo(updates) {
    const current = authState.get().user;
    if (!current?.id) return;
    try {
        const updated = await apiFetch(`/users/${current.id}`, {
            method: 'PUT',
            body: JSON.stringify({ ...current, ...updates })
        });
        authState.set({ user: updated });
        return updated;
    } catch (e) {
        console.error('Profile update failed:', e);
    }
}
