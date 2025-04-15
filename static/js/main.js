// Utility function to format numbers
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Utility function to format time
function formatTime(date) {
    return date.toLocaleTimeString();
}

// Utility function to show notifications
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Function to update mining stats
function updateMiningStats(stats) {
    const totalRewards = document.getElementById('total-rewards');
    if (totalRewards) {
        totalRewards.textContent = `${formatNumber(stats.total_rewards)} AVEUM`;
    }
}

// Function to update auto-like stats
function updateAutoLikeStats(stats) {
    const totalLikes = document.getElementById('total-likes');
    if (totalLikes) {
        totalLikes.textContent = formatNumber(stats.total_likes);
    }
}

// Function to handle API errors
function handleApiError(error) {
    console.error('API Error:', error);
    showNotification('An error occurred. Please try again.', 'danger');
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}); 