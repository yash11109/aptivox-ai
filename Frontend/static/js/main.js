/* ==========================================================================
   AI INTERVIEW PREPARATION PORTAL - MAIN CORE JS
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initUserSession();
    highlightActiveNav();
});

// Toast Notification Helper
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '⚠️';

    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'scale(0.9)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

window.currentUser = null;

// User Session Management
async function initUserSession() {
    const userBtn = document.getElementById('user-profile-btn');
    try {
        const response = await fetch('/api/auth/current-user');
        const data = await response.json();
        if (data.success && data.authenticated && data.user) {
            window.currentUser = data.user;
            if (userBtn) {
                const initial = (data.user.full_name || 'U').charAt(0).toUpperCase();
                userBtn.removeAttribute('onclick');
                userBtn.innerHTML = `
                    <div class="avatar">${initial}</div>
                    <span style="font-weight:600; font-size:0.9rem;">${data.user.full_name}</span>
                `;
                userBtn.onclick = (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    showProfileModal(data.user);
                };
            }
        } else {
            window.currentUser = null;
            if (userBtn) {
                userBtn.removeAttribute('onclick');
                userBtn.innerHTML = `
                    <div class="avatar" style="background:rgba(255,255,255,0.08); font-size:0.85rem;">👤</div>
                    <span style="font-weight:600; font-size:0.9rem;">Sign In</span>
                `;
                userBtn.onclick = (e) => {
                    e.preventDefault();
                    window.location.href = '/login';
                };
            }
        }
    } catch (err) {
        console.warn('Session fetch failed:', err);
    }
}

// Profile Modal Creation & Rendering
function showProfileModal(user) {
    let overlay = document.getElementById('profile-modal-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'profile-modal-overlay';
        overlay.className = 'modal-overlay';
        document.body.appendChild(overlay);
    }

    const initial = (user.full_name || 'U').charAt(0).toUpperCase();
    const role = user.target_role || 'Full Stack Engineer';
    const level = user.target_level || 'Senior';

    overlay.innerHTML = `
        <div class="modal-content profile-modal-card" style="max-width:420px; text-align:center; padding:32px; position:relative;">
            <button type="button" class="profile-modal-close" onclick="closeProfileModal()">&times;</button>

            <div class="profile-avatar-lg">
                <span>${initial}</span>
            </div>

            <h3 style="font-size:1.35rem; font-weight:700; margin-bottom:4px; color:var(--text-main);">${user.full_name}</h3>
            <p style="font-size:0.9rem; color:var(--text-muted); margin-bottom:16px;">${user.email}</p>

            <div style="display:flex; justify-content:center; gap:8px; margin-bottom:24px; flex-wrap:wrap;">
                <span class="profile-tag tag-role">🎯 ${role}</span>
                <span class="profile-tag tag-level">⚡ ${level}</span>
            </div>

            <div style="background:rgba(255,255,255,0.03); border:1px solid var(--border-light); border-radius:var(--radius-md); padding:16px; margin-bottom:24px; text-align:left; font-size:0.88rem;">
                <div style="display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:8px;">
                    <span style="color:var(--text-muted);">Session Status</span>
                    <span style="color:var(--success); font-weight:600;">● Active</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:var(--text-muted);">Database Sync</span>
                    <span style="color:var(--secondary); font-weight:600;">Connected</span>
                </div>
            </div>

            <div style="display:flex; flex-direction:column; gap:10px;">
                <a href="/dashboard" class="btn btn-primary" style="width:100%; text-align:center; justify-content:center;">📊 Candidate Analytics</a>
                <button type="button" class="btn btn-secondary" onclick="handleLogout()" style="width:100%; background:rgba(239, 68, 68, 0.15); color:var(--danger); border-color:rgba(239, 68, 68, 0.3); justify-content:center;">🚪 Log Out</button>
            </div>
        </div>
    `;

    overlay.classList.add('active');

    overlay.onclick = (e) => {
        if (e.target === overlay) {
            closeProfileModal();
        }
    };
}

function closeProfileModal() {
    const overlay = document.getElementById('profile-modal-overlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

async function handleLogout() {
    try {
        const res = await fetch('/api/auth/logout', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            closeProfileModal();
            showToast('Logged out successfully', 'info');
            await initUserSession();
            if (window.location.pathname === '/dashboard') {
                window.location.href = '/login';
            }
        }
    } catch (err) {
        showToast('Logout error', 'error');
    }
}


// Highlight Active Nav Item
function highlightActiveNav() {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.nav-link');
    links.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Password Visibility Toggle Helper
function togglePasswordVisibility(inputId, btnEl) {
    const input = document.getElementById(inputId);
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        btnEl.innerText = '🔒';
    } else {
        input.type = 'password';
        btnEl.innerText = '👁️';
    }
}

