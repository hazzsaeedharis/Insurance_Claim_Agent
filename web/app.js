// App State
let claimsCounter = 247;
let approvedCounter = 198;
let pendingCounter = 32;
let rejectedCounter = 17;

// Smooth scroll function
function scrollToSection(sectionId) {
    document.getElementById(sectionId).scrollIntoView({ behavior: 'smooth' });
}

// Show demo section
function showDemo() {
    scrollToSection('demo');
}

// Login modal functions
function showLogin() {
    document.getElementById('loginModal').classList.add('show');
}

function closeLogin() {
    document.getElementById('loginModal').classList.remove('show');
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('loginModal');
    if (event.target === modal) {
        modal.classList.remove('show');
    }
}

// Login form submission
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Login functionality would connect to Keycloak JWT authentication');
    closeLogin();
});

// Claim form submission with animated pipeline
document.getElementById('claimForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Get form values
    const policyNumber = document.getElementById('policyNumber').value;
    const claimType = document.getElementById('claimType').value;
    const amount = document.getElementById('amount').value;
    
    // Reset pipeline
    const steps = document.querySelectorAll('.pipeline-step');
    steps.forEach(step => {
        step.classList.remove('active', 'completed');
    });
    
    // Hide result panel
    document.getElementById('resultPanel').classList.remove('show');
    
    // Animate through pipeline steps
    const animateStep = async (stepNumber) => {
        const step = document.getElementById(`step-${stepNumber}`);
        step.classList.add('active');
        await new Promise(resolve => setTimeout(resolve, 1500));
        step.classList.remove('active');
        step.classList.add('completed');
    };
    
    // Run pipeline animation
    for (let i = 1; i <= 5; i++) {
        await animateStep(i);
    }
    
    // Generate claim ID
    const claimId = `CLM-${new Date().getFullYear()}-${Math.floor(Math.random() * 10000).toString().padStart(4, '0')}`;
    
    // Calculate settlement (mock)
    const deductible = 50;
    const coverageRate = 0.8;
    const settlement = Math.max(0, (parseFloat(amount) - deductible) * coverageRate);
    
    // Determine status (mock - random for demo)
    const statuses = ['APPROVED', 'APPROVED', 'APPROVED', 'PENDING', 'REJECTED'];
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    
    // Update counters
    claimsCounter++;
    document.getElementById('totalClaims').textContent = claimsCounter;
    
    if (status === 'APPROVED') {
        approvedCounter++;
        document.getElementById('approved').textContent = approvedCounter;
    } else if (status === 'PENDING') {
        pendingCounter++;
        document.getElementById('pending').textContent = pendingCounter;
    } else if (status === 'REJECTED') {
        rejectedCounter++;
        document.getElementById('rejected').textContent = rejectedCounter;
    }
    
    // Show results
    document.getElementById('claimId').textContent = claimId;
    document.getElementById('status').textContent = status;
    document.getElementById('status').className = status === 'APPROVED' ? 'status-approved' : '';
    document.getElementById('settlement').textContent = status === 'APPROVED' ? `€${settlement.toFixed(2)}` : '€0.00';
    document.getElementById('processingTime').textContent = '28.3s';
    
    // Show result panel
    document.getElementById('resultPanel').classList.add('show');
    
    // Add to recent claims list (prepend)
    const claimsList = document.querySelector('.claims-list');
    const newClaim = document.createElement('div');
    newClaim.className = 'claim-item';
    newClaim.innerHTML = `
        <div class="claim-info">
            <span class="claim-id">${claimId}</span>
            <span class="claim-type">${claimType.charAt(0).toUpperCase() + claimType.slice(1)}</span>
        </div>
        <span class="claim-amount">€${amount}</span>
        <span class="badge badge-${status.toLowerCase()}">${status.charAt(0) + status.slice(1).toLowerCase()}</span>
    `;
    
    // Remove last item if list is too long
    if (claimsList.children.length >= 3) {
        claimsList.removeChild(claimsList.lastChild);
    }
    
    // Add new claim to top
    claimsList.insertBefore(newClaim, claimsList.firstChild);
    
    // Update chart
    updateChart();
});

// File upload handling
document.getElementById('document').addEventListener('change', function(e) {
    const fileName = e.target.files[0]?.name || 'Choose file or drag here';
    document.querySelector('.file-upload span').textContent = fileName;
});

// Initialize Chart.js
let chart;

function initChart() {
    const ctx = document.getElementById('metricsChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['9AM', '10AM', '11AM', '12PM', '1PM', '2PM', '3PM'],
            datasets: [{
                label: 'Claims Processed',
                data: [12, 19, 23, 35, 42, 38, 45],
                borderColor: '#4F46E5',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                tension: 0.4
            }, {
                label: 'Avg Processing Time (s)',
                data: [32, 28, 25, 27, 24, 29, 28],
                borderColor: '#10B981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateChart() {
    if (chart) {
        // Add new data point
        const newValue = Math.floor(Math.random() * 10) + 40;
        chart.data.datasets[0].data.push(newValue);
        chart.data.datasets[0].data.shift();
        
        const newTime = Math.floor(Math.random() * 10) + 25;
        chart.data.datasets[1].data.push(newTime);
        chart.data.datasets[1].data.shift();
        
        chart.update();
    }
}

// Initialize chart when page loads
window.addEventListener('DOMContentLoaded', function() {
    // Initialize chart if Chart.js is loaded
    if (typeof Chart !== 'undefined') {
        initChart();
    }
    
    // Simulate live updates
    setInterval(() => {
        // Random claim updates
        if (Math.random() > 0.7) {
            claimsCounter++;
            document.getElementById('totalClaims').textContent = claimsCounter;
            
            const rand = Math.random();
            if (rand < 0.7) {
                approvedCounter++;
                document.getElementById('approved').textContent = approvedCounter;
            } else if (rand < 0.9) {
                pendingCounter++;
                document.getElementById('pending').textContent = pendingCounter;
            } else {
                rejectedCounter++;
                document.getElementById('rejected').textContent = rejectedCounter;
            }
        }
        
        // Update chart
        updateChart();
    }, 5000);
    
    // Check system health periodically
    checkSystemHealth();
    setInterval(checkSystemHealth, 30000);
});

// System health check
async function checkSystemHealth() {
    // In a real app, this would call the backend health endpoints
    const healthItems = document.querySelectorAll('.health-status');
    
    // Simulate checking each service
    healthItems.forEach((item, index) => {
        setTimeout(() => {
            // Randomly set some services as degraded for demo
            if (Math.random() > 0.95) {
                item.textContent = 'Degraded';
                item.style.color = '#F59E0B';
            } else {
                item.textContent = index === 0 ? 'Healthy' : 
                               index === 1 ? 'Connected' :
                               index === 2 ? 'Running' : 'Active';
                item.style.color = '#10B981';
            }
        }, index * 200);
    });
}

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards for animation
document.querySelectorAll('.feature-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'all 0.6s ease';
    observer.observe(card);
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for quick search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        alert('Quick search would open here');
    }
    
    // ESC to close modal
    if (e.key === 'Escape') {
        closeLogin();
    }
});

// Demo API connection (mock)
async function testAPIConnection() {
    try {
        // In production, this would connect to http://localhost:8001/health
        const mockResponse = {
            status: 'healthy',
            version: '1.0.0',
            services: {
                database: 'connected',
                redis: 'connected',
                rabbitmq: 'connected',
                minio: 'connected',
                keycloak: 'connected'
            }
        };
        
        console.log('API Health Check:', mockResponse);
        return mockResponse;
    } catch (error) {
        console.error('API Connection Error:', error);
        return null;
    }
}

// Test connection on load
testAPIConnection();

// Add smooth page transitions
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Console welcome message
console.log('%c🚀 ClaimAI Pro - Insurance Claim Processing System', 'color: #4F46E5; font-size: 20px; font-weight: bold;');
console.log('%cBuilt with ❤️ for Hallesche Insurance', 'color: #10B981; font-size: 14px;');
console.log('%cBackend API: http://localhost:8001/docs', 'color: #6B7280; font-size: 12px;');
console.log('%cHealth Check: http://localhost:8000/health', 'color: #6B7280; font-size: 12px;');