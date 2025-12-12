// Sidebar Component for HUMANERGY Portal
// This file provides a unified navigation sidebar for all pages

// Insert sidebar HTML into the page
function initializeSidebar() {
    const sidebarHTML = `
    <!-- Sidebar Menu -->
    <div id="sidebar" class="sidebar">
        <div class="sidebar-header">
            <h3>Menu</h3>
            <button onclick="toggleSidebar()" class="close-btn">&times;</button>
        </div>
        <div class="sidebar-content">
            <!-- Public Pages (Always Visible) -->
            <div class="sidebar-section">
                <div class="sidebar-section-title">Information</div>
                <a href="/about.html" class="sidebar-link">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <path d="M12 16v-4"></path>
                        <path d="M12 8h.01"></path>
                    </svg>
                    About
                </a>
                <a href="/iso50001.html" class="sidebar-link">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                    </svg>
                    ISO 50001
                </a>
                <a href="/contact.html" class="sidebar-link">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    Contact
                </a>
            </div>
            
            <!-- Dashboard Links (Only for Authenticated Users) -->
            <div id="dashboard-section" class="sidebar-section" style="display: none;">
                <div class="sidebar-divider"></div>
                <div class="sidebar-section-title">Dashboard</div>
                <a href="/" class="sidebar-link">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="7" height="7"></rect>
                        <rect x="14" y="3" width="7" height="7"></rect>
                        <rect x="14" y="14" width="7" height="7"></rect>
                        <rect x="3" y="14" width="7" height="7"></rect>
                    </svg>
                    Dashboard
                </a>
                <a href="/api/analytics/ui/" class="sidebar-link">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="20" x2="18" y2="10"></line>
                        <line x1="12" y1="20" x2="12" y2="4"></line>
                        <line x1="6" y1="20" x2="6" y2="14"></line>
                    </svg>
                    Analytics
                </a>
                <a href="/reports.html" class="sidebar-link">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                    Reports
                </a>
                <a href="/grafana/" class="sidebar-link">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="20" x2="12" y2="10"></line>
                        <line x1="18" y1="20" x2="18" y2="4"></line>
                        <line x1="6" y1="20" x2="6" y2="16"></line>
                    </svg>
                    Grafana
                </a>
                <a href="/nodered/" class="sidebar-link">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                    </svg>
                    Node-RED
                </a>
                <a href="/api/simulator/docs" class="sidebar-link" target="_blank">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polygon points="10 8 16 12 10 16 10 8"></polygon>
                    </svg>
                    Simulator
                </a>
            </div>
            
            <div class="sidebar-divider"></div>
            
            <!-- Authentication Link (Only for Non-Authenticated Users) -->
            <a id="sidebar-auth-btn" href="/auth.html" class="sidebar-link" style="display: none;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
                    <polyline points="10 17 15 12 10 7"></polyline>
                    <line x1="15" y1="12" x2="3" y2="12"></line>
                </svg>
                Sign In
            </a>
            
            <!-- Admin Dashboard (Only for Admins) -->
            <a id="sidebar-admin-btn" href="/admin/dashboard.html" class="sidebar-link admin-link" style="display: none;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="8.5" cy="7" r="4"></circle>
                    <polyline points="17 11 19 13 23 9"></polyline>
                </svg>
                Admin Dashboard
            </a>
            
            <!-- Logout (Only for Authenticated Users) -->
            <a id="sidebar-logout-btn" href="#" onclick="logout(); return false;" class="sidebar-link logout-link" style="display: none;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                    <polyline points="16 17 21 12 16 7"></polyline>
                    <line x1="21" y1="12" x2="9" y2="12"></line>
                </svg>
                Logout
            </a>
        </div>
    </div>

    <!-- Sidebar Overlay -->
    <div id="sidebar-overlay" class="sidebar-overlay" onclick="toggleSidebar()"></div>
    `;
    
    // Insert sidebar at the beginning of body
    document.body.insertAdjacentHTML('afterbegin', sidebarHTML);
    
    // Apply conditional display based on authentication status
    updateSidebarVisibility();
}

// Update sidebar visibility based on authentication status
function updateSidebarVisibility() {
    const token = localStorage.getItem('auth_token');
    const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
    const isAuthenticated = token && userData.email;
    
    // Dashboard section - only for authenticated users
    const dashboardSection = document.getElementById('dashboard-section');
    if (dashboardSection) {
        dashboardSection.style.display = isAuthenticated ? 'block' : 'none';
    }
    
    // Auth button - only for non-authenticated users
    const authBtn = document.getElementById('sidebar-auth-btn');
    if (authBtn) {
        authBtn.style.display = isAuthenticated ? 'none' : 'flex';
    }
    
    // Admin button - only for authenticated admin users
    const adminBtn = document.getElementById('sidebar-admin-btn');
    if (adminBtn && userData.role === 'admin') {
        adminBtn.style.display = 'flex';
    }
    
    // Logout button - only for authenticated users
    const logoutBtn = document.getElementById('sidebar-logout-btn');
    if (logoutBtn) {
        logoutBtn.style.display = isAuthenticated ? 'flex' : 'none';
    }
}

// Toggle sidebar function
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (sidebar && overlay) {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('show');
    }
}

// Logout function
function logout() {
    // Call logout API
    const token = localStorage.getItem('auth_token');
    if (token) {
        fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        }).catch(err => console.error('Logout error:', err));
    }
    
    // Clear local storage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    
    // Redirect to auth page
    window.location.href = '/auth.html';
}

// Initialize sidebar when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSidebar);
} else {
    initializeSidebar();
}
