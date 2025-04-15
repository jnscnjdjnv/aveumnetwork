// Update status indicators and badges
function updateStatusIndicator(elementId, isActive) {
    const indicator = document.getElementById(elementId);
    if (indicator) {
        indicator.className = 'status-indicator ' + (isActive ? 'status-active' : 'status-inactive');
    }
}

function updateStatusBadge(elementId, text, isActive) {
    const badge = document.getElementById(elementId);
    if (badge) {
        badge.textContent = text;
        badge.className = 'badge ' + (isActive ? 'bg-success' : 'bg-danger');
    }
}

// Format date/time
function formatDateTime(dateString) {
    if (!dateString || dateString === 'Never') return 'Never';
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Format number with commas
function formatNumber(num) {
    if (num === undefined || num === null) return '0';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

// Update dashboard data
async function updateDashboard() {
    try {
        const response = await fetch('/api/status');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        if (!data.success) {
            console.error('Error fetching status:', data.error);
            return;
        }
        
        // Update account status
        document.getElementById('aveum-email').textContent = data.aveum_email || 'Not set';
        updateStatusBadge('login-status', data.login_status ? 'Logged In' : 'Not Logged In', data.login_status);
        document.getElementById('device-id').textContent = data.device_id || 'Not set';
        document.getElementById('device-model').textContent = data.device_model || 'Not set';
        document.getElementById('platform-version').textContent = data.platform_version || 'Not set';
        
        // Update mode
        updateStatusBadge('current-mode', data.mining_active ? 'Mining' : 'Auto-Like', true);
        
        // Update mining status
        updateStatusBadge('mining-status', data.is_mining ? 'Active' : 'Inactive', data.is_mining);
        document.getElementById('current-balance').textContent = formatNumber(data.current_balance);
        document.getElementById('total-rewards').textContent = formatNumber(data.total_rewards);
        document.getElementById('mining-sessions').textContent = formatNumber(data.mining_sessions_completed);
        document.getElementById('mining-errors').textContent = formatNumber(data.mining_errors);
        
        // Update auto-like status
        updateStatusBadge('auto-like-status', data.auto_like_active ? 'Active' : 'Inactive', data.auto_like_active);
        document.getElementById('total-likes').textContent = formatNumber(data.total_likes);
        document.getElementById('daily-likes').textContent = formatNumber(data.daily_likes);
        document.getElementById('like-errors').textContent = formatNumber(data.like_errors);
        
        // Update ban status
        updateStatusBadge('ban-status', data.is_banned ? 'Banned' : 'Not Banned', !data.is_banned);
        document.getElementById('last-ban-check').textContent = formatDateTime(data.last_ban_check_time);
        
        // Update activity log
        const activityLog = document.getElementById('activity-log');
        if (activityLog && data.last_activity) {
            activityLog.textContent = data.last_activity;
            activityLog.scrollTop = activityLog.scrollHeight;
        }
        
        // Update button states
        const startMiningBtn = document.getElementById('start-mining');
        const stopMiningBtn = document.getElementById('stop-mining');
        const toggleAutoLikeBtn = document.getElementById('toggle-auto-like');
        
        if (startMiningBtn) startMiningBtn.disabled = data.is_mining;
        if (stopMiningBtn) stopMiningBtn.disabled = !data.is_mining;
        if (toggleAutoLikeBtn) toggleAutoLikeBtn.disabled = data.mining_active;
        
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

// Button click handlers
document.addEventListener('DOMContentLoaded', function() {
    // Refresh token
    const refreshTokenBtn = document.getElementById('refresh-token');
    if (refreshTokenBtn) {
        refreshTokenBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/refresh_token', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    showToast('Token refreshed successfully!', 'success');
                    updateDashboard();
                } else {
                    showToast(`Failed to refresh token: ${data.error}`, 'danger');
                }
            } catch (error) {
                console.error('Error refreshing token:', error);
                showToast('An error occurred while refreshing token', 'danger');
            }
        });
    }
    
    // Switch mode
    const switchModeBtn = document.getElementById('switch-mode');
    if (switchModeBtn) {
        switchModeBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/switch-mode', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    showToast('Mode switched successfully!', 'success');
                    updateDashboard();
                } else {
                    showToast(`Failed to switch mode: ${data.error}`, 'danger');
                }
            } catch (error) {
                console.error('Error switching mode:', error);
                showToast('An error occurred while switching mode', 'danger');
            }
        });
    }
    
    // Start mining
    const startMiningBtn = document.getElementById('start-mining');
    if (startMiningBtn) {
        startMiningBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/start-mining', { method: 'POST' });
                const data = await response.json();
                if (data.message) {
                    showToast('Mining started successfully!', 'success');
                    updateDashboard();
                } else {
                    showToast(`Failed to start mining: ${data.error}`, 'danger');
                }
            } catch (error) {
                console.error('Error starting mining:', error);
                showToast('An error occurred while starting mining', 'danger');
            }
        });
    }
    
    // Stop mining
    const stopMiningBtn = document.getElementById('stop-mining');
    if (stopMiningBtn) {
        stopMiningBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/stop-mining', { method: 'POST' });
                const data = await response.json();
                if (data.message) {
                    showToast('Mining stopped successfully!', 'success');
                    updateDashboard();
                } else {
                    showToast(`Failed to stop mining: ${data.error}`, 'danger');
                }
            } catch (error) {
                console.error('Error stopping mining:', error);
                showToast('An error occurred while stopping mining', 'danger');
            }
        });
    }
    
    // Toggle auto-like
    const toggleAutoLikeBtn = document.getElementById('toggle-auto-like');
    if (toggleAutoLikeBtn) {
        toggleAutoLikeBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/toggle_auto_like', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    showToast('Auto-like toggled successfully!', 'success');
                    updateDashboard();
                } else {
                    showToast(`Failed to toggle auto-like: ${data.error}`, 'danger');
                }
            } catch (error) {
                console.error('Error toggling auto-like:', error);
                showToast('An error occurred while toggling auto-like', 'danger');
            }
        });
    }
    
    // Check ban status
    const checkBanBtn = document.getElementById('check-ban');
    if (checkBanBtn) {
        checkBanBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/check-ban', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    showToast('Ban status checked successfully!', 'success');
                    updateDashboard();
                } else {
                    showToast(`Failed to check ban status: ${data.error}`, 'danger');
                }
            } catch (error) {
                console.error('Error checking ban status:', error);
                showToast('An error occurred while checking ban status', 'danger');
            }
        });
    }
    
    // Initial update and periodic refresh
    updateDashboard();
    setInterval(updateDashboard, 5000);
}); 