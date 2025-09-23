/**
 * ClaimAI Pro - Main JavaScript Application
 * Handles all frontend functionality and API communication
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global state
let dashboardData = {
    stats: null,
    metrics: null,
    claims: [],
    activities: []
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 ClaimAI Pro Frontend Initialized');
    initializeApp();
});

/**
 * Initialize the application
 */
async function initializeApp() {
    try {
        showLoading(true);
        
        // Load dashboard data
        await loadDashboardData();
        
        // Render dashboard
        renderDashboard();
        
        console.log('✅ Dashboard loaded successfully');
    } catch (error) {
        console.error('❌ Failed to load dashboard:', error);
        showError('Failed to load dashboard data. Please check if the backend is running.');
    } finally {
        showLoading(false);
    }
}

/**
 * Load all dashboard data from API
 */
async function loadDashboardData() {
    try {
        // Load stats and metrics in parallel
        const [stats, metrics, recentClaims] = await Promise.all([
            fetchData('/api/dashboard/stats'),
            fetchData('/api/dashboard/metrics'),
            fetchData('/api/dashboard/recent-claims?limit=5')
        ]);
        
        dashboardData.stats = stats;
        dashboardData.metrics = metrics;
        dashboardData.claims = recentClaims.recent_claims || [];
        
        // Generate sample activities
        dashboardData.activities = generateSampleActivities();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        throw error;
    }
}

/**
 * Render the dashboard with loaded data
 */
function renderDashboard() {
    renderStats();
    renderClaims();
    renderActivities();
}

/**
 * Render statistics cards
 */
function renderStats() {
    if (!dashboardData.stats) return;
    
    const stats = dashboardData.stats;
    
    // Update stat cards
    updateElement('total-claims', stats.total_claims.toLocaleString());
    updateElement('pending-claims', stats.pending_claims);
    updateElement('approved-claims', stats.approved_claims);
    updateElement('rejected-claims', stats.rejected_claims);
}

/**
 * Render claims list
 */
function renderClaims() {
    const claimsList = document.getElementById('claims-list');
    if (!claimsList || !dashboardData.claims) return;
    
    claimsList.innerHTML = '';
    
    dashboardData.claims.forEach(claim => {
        const claimElement = createClaimElement(claim);
        claimsList.appendChild(claimElement);
    });
}

/**
 * Create a claim list item element
 */
function createClaimElement(claim) {
    const div = document.createElement('div');
    div.className = 'claim-item';
    
    const statusClass = `status-${claim.status.replace('_', '-')}`;
    
    div.innerHTML = `
        <div class="claim-header">
            <span class="claim-id">${claim.id}</span>
            <span class="claim-status ${statusClass}">${claim.status.replace('_', ' ').toUpperCase()}</span>
        </div>
        <div class="claim-details">
            <strong>${claim.claimant_name}</strong> - $${claim.claim_amount.toLocaleString()}
            <br>
            <small>${claim.incident_type} • Processed in ${claim.processing_time}</small>
        </div>
    `;
    
    return div;
}

/**
 * Render activities list
 */
function renderActivities() {
    const activityList = document.getElementById('activity-list');
    if (!activityList || !dashboardData.activities) return;
    
    activityList.innerHTML = '';
    
    dashboardData.activities.forEach(activity => {
        const activityElement = createActivityElement(activity);
        activityList.appendChild(activityElement);
    });
}

/**
 * Create an activity list item element
 */
function createActivityElement(activity) {
    const div = document.createElement('div');
    div.className = 'activity-item';
    
    div.innerHTML = `
        <div class="activity-icon ${activity.type}">
            <i class="fas ${activity.icon}"></i>
        </div>
        <div class="activity-content">
            <div class="activity-title">${activity.title}</div>
            <div class="activity-time">${activity.time}</div>
        </div>
    `;
    
    return div;
}

/**
 * Generate sample activities for demo
 */
function generateSampleActivities() {
    return [
        {
            type: 'success',
            icon: 'fa-check-circle',
            title: 'Claim #claim-001 approved by AI',
            time: '2 minutes ago'
        },
        {
            type: 'warning',
            icon: 'fa-exclamation-triangle',
            title: 'High-value claim requires review',
            time: '15 minutes ago'
        },
        {
            type: 'info',
            icon: 'fa-robot',
            title: 'AI processing queue updated',
            time: '1 hour ago'
        },
        {
            type: 'success',
            icon: 'fa-shield-alt',
            title: 'Fraud detection model updated',
            time: '2 hours ago'
        }
    ];
}

/**
 * Show/hide loading overlay
 */
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.toggle('show', show);
    }
}

/**
 * Show error message
 */
function showError(message) {
    // Create error notification
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #fee2e2;
        color: #991b1b;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        max-width: 400px;
    `;
    errorDiv.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(errorDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}

/**
 * Update element text content
 */
function updateElement(id, text) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = text;
    }
}

/**
 * Fetch data from API
 */
async function fetchData(endpoint) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API request failed for ${endpoint}:`, error);
        throw error;
    }
}

/**
 * Action button handlers
 */
function refreshClaims() {
    console.log('🔄 Refreshing claims...');
    showLoading(true);
    
    // Simulate refresh
    setTimeout(() => {
        loadDashboardData().then(() => {
            renderDashboard();
            showLoading(false);
            console.log('✅ Claims refreshed');
        });
    }, 1000);
}

function createNewClaim() {
    console.log('➕ Creating new claim...');
    alert('New Claim functionality would open a form here.\n\nIn a full implementation, this would:\n- Open a claim submission form\n- Allow document upload\n- Process with AI\n- Show real-time status updates');
}

function runAIDemo() {
    console.log('🤖 Running AI demo...');
    
    // Open AI demo in new tab
    window.open(`${API_BASE_URL}/api/ai/demo`, '_blank');
    
    // Also show local demo
    showAIDemo();
}

function showAIDemo() {
    const demoData = {
        message: "🚀 AI Processing Demo - ClaimAI Pro",
        demo_data: [
            {
                claim_id: "demo-001",
                claimant_name: "John Smith",
                claim_amount: 2500.00,
                status: "approved",
                processing_time: "2.3 seconds",
                ai_confidence: 0.92
            },
            {
                claim_id: "demo-002", 
                claimant_name: "Jane Doe",
                claim_amount: 1500.00,
                status: "under_review",
                processing_time: "1.8 seconds",
                ai_confidence: 0.89
            }
        ],
        processing_metrics: {
            claims_processed_today: 1247,
            average_processing_time: "2.3 seconds",
            ai_accuracy_rate: 0.95,
            fraud_detection_rate: 0.94,
            system_uptime: "99.97%"
        }
    };
    
    // Show demo in modal or alert
    const demoText = `
🤖 AI Processing Demo Results:

📊 Processing Metrics:
• Claims Processed Today: ${demoData.processing_metrics.claims_processed_today}
• Average Processing Time: ${demoData.processing_metrics.average_processing_time}
• AI Accuracy Rate: ${(demoData.processing_metrics.ai_accuracy_rate * 100).toFixed(1)}%
• Fraud Detection Rate: ${(demoData.processing_metrics.fraud_detection_rate * 100).toFixed(1)}%
• System Uptime: ${demoData.processing_metrics.system_uptime}

📋 Recent Claims:
${demoData.demo_data.map(claim => 
    `• ${claim.claimant_name}: $${claim.claim_amount} (${claim.status}) - ${claim.processing_time}`
).join('\n')}

🎯 This demonstrates the power of AI-driven claims processing!
    `;
    
    alert(demoText);
}

function viewAnalytics() {
    console.log('📊 Opening analytics...');
    window.open(`${API_BASE_URL}/api/dashboard/analytics/trends`, '_blank');
}

function openAdmin() {
    console.log('⚙️ Opening admin panel...');
    alert('Admin Panel functionality would open here.\n\nIn a full implementation, this would:\n- Show admin dashboard\n- Allow claim review and approval\n- Display system metrics\n- Manage user roles and permissions');
}

function openAPIDocs() {
    console.log('📚 Opening API documentation...');
    window.open(`${API_BASE_URL}/docs`, '_blank');
}

// Export functions for global access
window.refreshClaims = refreshClaims;
window.createNewClaim = createNewClaim;
window.runAIDemo = runAIDemo;
window.viewAnalytics = viewAnalytics;
window.openAdmin = openAdmin;
window.openAPIDocs = openAPIDocs;
