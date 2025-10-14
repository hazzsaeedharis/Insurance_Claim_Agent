// API Configuration
const API_BASE_URL = 'http://localhost:8005';

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

// UPDATED: Claim form submission with REAL API
document.getElementById('claimForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Get form values
    const policyNumber = document.getElementById('policyNumber').value;
    const claimType = document.getElementById('claimType').value;
    const fileInput = document.getElementById('document');
    
    if (!fileInput.files[0]) {
        alert('Please upload a document');
        return;
    }
    
    // Reset pipeline
    const steps = document.querySelectorAll('.pipeline-step');
    steps.forEach(step => {
        step.classList.remove('active', 'completed');
    });
    
    // Hide result panel
    document.getElementById('resultPanel').classList.remove('show');
    
    // Process with REAL API
    const startTime = Date.now();
    await processClaimWithRealAPI(fileInput.files[0], policyNumber, startTime);
});

// NEW: Process claim with real AI backend
async function processClaimWithRealAPI(file, policyNumber, startTime) {
    try {
        // Generate a single claim ID to use throughout the process
        const claimId = 'CLAIM-' + Date.now();
        
        // Step 1: Document Received
        await animateStep(1);
        
        // Step 2: OCR Processing - Extract document
        const step2 = document.getElementById('step-2');
        step2.querySelector('p').textContent = 'Extracting data with AI...';
        await animateStep(2);
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('claim_id', claimId); // Use the same claim ID
        formData.append('document_type_hint', 'medical_invoice');
        
        const extractResponse = await fetch(`${API_BASE_URL}/documents/extract`, {
            method: 'POST',
            body: formData
        });
        
        if (!extractResponse.ok) {
            throw new Error('Document extraction failed');
        }
        
        const extractedData = await extractResponse.json();
        step2.querySelector('p').textContent = `Extracted €${extractedData.extracted_data.summary?.totalAmount || 0}`;
        
        // Step 3: AI Analysis - Analyze claim
        const step3 = document.getElementById('step-3');
        step3.querySelector('p').textContent = 'Matching against policy...';
        await animateStep(3);
        
        const analysisResponse = await fetch(`${API_BASE_URL}/claims/analyze/${claimId}`, { // Use the same claim ID
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                policy_id: 'HALLESCHE_NK_SELECT_S',
                customer_id: 'DEMO-CUSTOMER'
            })
        });
        
        if (!analysisResponse.ok) {
            throw new Error('Claim analysis failed');
        }
        
        const analysisData = await analysisResponse.json();
        step3.querySelector('p').textContent = `Calculated ${analysisData.approval_rate.toFixed(1)}% coverage`;
        
        // Step 4: Fraud Check (simulated)
        const step4 = document.getElementById('step-4');
        step4.querySelector('p').textContent = 'No fraud detected';
        await animateStep(4);
        
        // Step 5: Settlement
        const step5 = document.getElementById('step-5');
        step5.querySelector('p').textContent = `Approved: €${analysisData.total_approved.toFixed(2)}`;
        await animateStep(5);
        
        // Show results with REAL data
        const processingTime = ((Date.now() - startTime) / 1000).toFixed(1);
        showRealResults(analysisData, processingTime, extractedData, claimId);
        
        // Update counters
        claimsCounter++;
        document.getElementById('totalClaims').textContent = claimsCounter;
        approvedCounter++;
        document.getElementById('approved').textContent = approvedCounter;
        
    } catch (error) {
        console.error('Error processing claim:', error);
        alert('⚠️ Error: Make sure the AI service is running!\n\nRun: .venv\\Scripts\\python.exe -m uvicorn services.ai_processing.api:app --host 0.0.0.0 --port 8005');
        
        // Reset pipeline on error
        const steps = document.querySelectorAll('.pipeline-step');
        steps.forEach(step => step.classList.remove('active', 'completed'));
    }
}

// Animate a single step
async function animateStep(stepNumber) {
    const step = document.getElementById(`step-${stepNumber}`);
    step.classList.add('active');
    await new Promise(resolve => setTimeout(resolve, 1000));
    step.classList.remove('active');
    step.classList.add('completed');
}

// NEW: Show REAL results with justification
function showRealResults(analysisData, processingTime, extractedData, claimId) {
    // Use the provided claim ID from the processing
    
    // Update basic results
    document.getElementById('claimId').textContent = claimId;
    const status = analysisData.approval_rate > 0 ? 'APPROVED' : 'REJECTED';
    document.getElementById('status').textContent = status;
    document.getElementById('status').className = status === 'APPROVED' ? 'status-approved' : 'status-rejected';
    document.getElementById('settlement').textContent = `€${analysisData.total_approved.toFixed(2)} / €${analysisData.total_claimed.toFixed(2)}`;
    document.getElementById('processingTime').textContent = processingTime + 's';
    
    // Show result panel
    const resultPanel = document.getElementById('resultPanel');
    
    // Create or update justification section
    let justificationDiv = document.getElementById('justificationSection');
    if (!justificationDiv) {
        justificationDiv = document.createElement('div');
        justificationDiv.id = 'justificationSection';
        justificationDiv.style.marginTop = '30px';
        justificationDiv.style.padding = '20px';
        justificationDiv.style.background = '#f9fafb';
        justificationDiv.style.borderRadius = '8px';
        justificationDiv.style.border = '1px solid #e5e7eb';
        resultPanel.appendChild(justificationDiv);
    }
    
    // Build detailed justification HTML
    justificationDiv.innerHTML = `
        <h4 style="margin: 0 0 15px 0; color: #1f2937; display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-file-alt"></i> 
            Detailed Claim Justification
        </h4>
        <div style="background: white; padding: 15px; border-radius: 6px; border: 1px solid #e5e7eb;">
            <pre style="white-space: pre-wrap; font-family: 'Inter', sans-serif; font-size: 13px; line-height: 1.8; margin: 0; color: #374151;">${analysisData.justification}</pre>
        </div>
        
        <div style="margin-top: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
            <div style="background: white; padding: 15px; border-radius: 6px; border: 1px solid #e5e7eb;">
                <div style="font-size: 12px; color: #6b7280; margin-bottom: 5px;">Document Type</div>
                <div style="font-size: 16px; font-weight: 600; color: #1f2937;">${extractedData.document_type || 'Medical Invoice'}</div>
            </div>
            <div style="background: white; padding: 15px; border-radius: 6px; border: 1px solid #e5e7eb;">
                <div style="font-size: 12px; color: #6b7280; margin-bottom: 5px;">Extraction Confidence</div>
                <div style="font-size: 16px; font-weight: 600; color: #10b981;">${(extractedData.confidence_scores?.overall * 100 || 95).toFixed(1)}%</div>
            </div>
            <div style="background: white; padding: 15px; border-radius: 6px; border: 1px solid #e5e7eb;">
                <div style="font-size: 12px; color: #6b7280; margin-bottom: 5px;">Policy Match</div>
                <div style="font-size: 16px; font-weight: 600; color: #3b82f6;">Hallesche NK.select S</div>
            </div>
        </div>
    `;
    
    resultPanel.classList.add('show');
    resultPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

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
    
    // Check system health
    checkSystemHealth();
    setInterval(checkSystemHealth, 30000);
});

// System health check - now checks REAL API
async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, { method: 'GET' });
        if (response.ok) {
            console.log('✅ AI Service is healthy');
            const healthItems = document.querySelectorAll('.health-status');
            healthItems.forEach((item, index) => {
                item.textContent = index === 0 ? 'Healthy' : 
                                   index === 1 ? 'Connected' :
                                   index === 2 ? 'Running' : 'Active';
                item.style.color = '#10B981';
            });
        }
    } catch (error) {
        console.warn('⚠️  AI Service not responding - is it running on port 8005?');
    }
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
console.log('%cAI Processing API: http://localhost:8005/docs', 'color: #6B7280; font-size: 12px;');
console.log('%cHealth Check: http://localhost:8005/health', 'color: #6B7280; font-size: 12px;');
