// ScaleX Ventures Portfolio Monitor - Main JavaScript

// Global variables
let refreshInterval;
let isMonitoring = false;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('ScaleX Ventures Portfolio Monitor initialized');
    
    // Set up auto-refresh every 30 seconds
    startAutoRefresh();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize charts if on dashboard
    if (document.getElementById('companyChart')) {
        initializeCharts();
    }
});

// Auto-refresh functionality
function startAutoRefresh() {
    refreshInterval = setInterval(() => {
        refreshStats();
    }, 30000); // Refresh every 30 seconds
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

// Refresh stats data
async function refreshStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        // Update stats cards
        updateStatsCards(data);
        
        // Update charts
        updateCharts(data);
        
        console.log('Stats refreshed successfully');
    } catch (error) {
        console.error('Error refreshing stats:', error);
    }
}

// Update stats cards
function updateStatsCards(data) {
    // Update total mentions
    const totalMentions = document.querySelector('.card.bg-primary .card-title');
    if (totalMentions) {
        totalMentions.textContent = data.total_mentions;
    }
    
    // Update recent mentions
    const recentMentions = document.querySelector('.card.bg-success .card-title');
    if (recentMentions) {
        recentMentions.textContent = data.recent_mentions;
    }
    
    // Update active companies
    const activeCompanies = document.querySelector('.card.bg-warning .card-title');
    if (activeCompanies) {
        activeCompanies.textContent = data.company_mentions.length;
    }
}

// Update charts
function updateCharts(data) {
    // Update company chart
    if (window.companyChart) {
        window.companyChart.data.labels = data.company_mentions.slice(0, 10).map(item => item.company_name);
        window.companyChart.data.datasets[0].data = data.company_mentions.slice(0, 10).map(item => item.count);
        window.companyChart.update();
    }
    
    // Update source chart
    if (window.sourceChart) {
        window.sourceChart.data.labels = data.source_mentions.slice(0, 8).map(item => item.source);
        window.sourceChart.data.datasets[0].data = data.source_mentions.slice(0, 8).map(item => item.count);
        window.sourceChart.update();
    }
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize charts
function initializeCharts() {
    // This will be handled by the template-specific JavaScript
    console.log('Charts initialized');
}

// Show alert notification
function showAlert(type, message, duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    alertDiv.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, duration);
}

// Get alert icon based on type
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle',
        'primary': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Run monitoring function
async function runMonitoring() {
    if (isMonitoring) {
        showAlert('warning', 'Monitoring is already running...');
        return;
    }
    
    isMonitoring = true;
    const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
    modal.show();
    
    try {
        const response = await fetch('/api/run-monitoring');
        const data = await response.json();
        
        modal.hide();
        
        if (data.success) {
            showAlert('success', 'Monitoring completed successfully! Found new mentions.');
            // Refresh the page after a short delay
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            showAlert('danger', 'Error: ' + data.message);
        }
    } catch (error) {
        modal.hide();
        showAlert('danger', 'Error running monitoring: ' + error.message);
    } finally {
        isMonitoring = false;
    }
}

// Refresh data function
function refreshData() {
    showAlert('info', 'Refreshing data...');
    location.reload();
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function formatNumber(number) {
    return new Intl.NumberFormat().format(number);
}

function getSentimentClass(score) {
    if (score > 0.1) return 'positive';
    if (score < -0.1) return 'negative';
    return 'neutral';
}

function getSentimentBadge(score) {
    if (score > 0.1) return '<span class="badge bg-success">Positive</span>';
    if (score < -0.1) return '<span class="badge bg-danger">Negative</span>';
    return '<span class="badge bg-secondary">Neutral</span>';
}

// Export functions for global use
window.runMonitoring = runMonitoring;
window.refreshData = refreshData;
window.showAlert = showAlert;
