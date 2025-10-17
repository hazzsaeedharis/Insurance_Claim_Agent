// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// App State
let policies = []; // Store loaded policies

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

// ============================================================================
// POLICY MANAGEMENT FUNCTIONS
// ============================================================================

// State for file management
let selectedFiles = [];

// Load policies from API
async function loadPolicies() {
    try {
        console.log('Loading policies from:', `${API_BASE_URL}/api/policies`);
        const response = await fetch(`${API_BASE_URL}/api/policies`);
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if (!response.ok) {
            throw new Error(`Failed to load policies: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Received policies data:', data);
        policies = data.policies || [];
        console.log('Parsed policies:', policies);
        
        // Update dropdown in claim form
        updatePolicyDropdown();
        
        // Update policies list
        updatePoliciesList();
        
        return policies;
    } catch (error) {
        console.error('Error loading policies:', error);
        console.error('Error details:', error.message);
        return [];
    }
}

// Update policy selector dropdown
function updatePolicyDropdown() {
    const policySelect = document.getElementById('policySelect');
    
    if (!policySelect) return;
    
    policySelect.innerHTML = '';
    
    if (policies.length === 0) {
        policySelect.innerHTML = '<option value="">No policies available - Please upload a policy first</option>';
        return;
    }
    
    // Add default option
    policySelect.innerHTML = '<option value="">-- Select a policy --</option>';
    
    // Add policy options
    policies.forEach(policy => {
        const option = document.createElement('option');
        option.value = policy.policy_id;
        option.textContent = `${policy.policy_name} (${policy.policy_id})`;
        policySelect.appendChild(option);
    });
    
    // Auto-select first policy if available
    if (policies.length > 0) {
        policySelect.value = policies[0].policy_id;
    }
}

// Update policies list display
function updatePoliciesList() {
    const policiesList = document.getElementById('policiesList');
    
    if (!policiesList) return;
    
    if (policies.length === 0) {
        policiesList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-folder-open" style="font-size: 48px; color: #9ca3af; margin-bottom: 10px;"></i>
                <p style="color: #6b7280;">No policies indexed yet</p>
                <small style="color: #9ca3af;">Upload a policy document to get started</small>
            </div>
        `;
        return;
    }
    
    policiesList.innerHTML = policies.map(policy => `
        <div class="policy-item" id="policy-${policy.policy_id}">
            <div class="policy-info">
                <h4 class="policy-name" id="name-${policy.policy_id}">${policy.policy_name}</h4>
                <span class="policy-id">${policy.policy_id}</span>
            </div>
            <div class="policy-actions">
                <button class="btn btn-secondary btn-sm" onclick="renamePolicy('${policy.policy_id}')" title="Rename policy">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-danger btn-sm" onclick="deletePolicy('${policy.policy_id}')" title="Delete policy">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// ============================================================================
// FILE MANAGEMENT FUNCTIONS
// ============================================================================

// Handle file selection
function handleFileSelection(e) {
    const files = Array.from(e.target.files);
    
    // Append new files to existing selection
    selectedFiles = [...selectedFiles, ...files];
    
    // Render the files list
    renderFilesList();
    
    // Enable submit button
    updateSubmitButton();
    
    // Reset file input
    e.target.value = '';
}

// Render files list
function renderFilesList() {
    const container = document.getElementById('selectedFilesList');
    const filesContainer = document.getElementById('filesContainer');
    
    if (selectedFiles.length === 0) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'block';
    
    filesContainer.innerHTML = selectedFiles.map((file, index) => `
        <div class="file-item">
            <div class="file-info">
                <i class="fas fa-file-pdf file-icon"></i>
                <div class="file-details">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${formatFileSize(file.size)}</span>
                </div>
            </div>
            <button type="button" class="file-remove" onclick="removeFile(${index})">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `).join('');
}

// Remove a specific file
function removeFile(index) {
    selectedFiles.splice(index, 1);
    renderFilesList();
    updateSubmitButton();
}

// Clear all files
function clearAllFiles() {
    selectedFiles = [];
    renderFilesList();
    updateSubmitButton();
}

// Add more files
function addMoreFiles() {
    document.getElementById('policyFile').click();
}

// Update submit button state
function updateSubmitButton() {
    const btn = document.getElementById('submitPolicyBtn');
    btn.disabled = selectedFiles.length === 0;
}

// Format file size
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// ============================================================================
// POLICY UPLOAD WITH ANIMATION
// ============================================================================

// Animate policy processing step
async function animatePolicyStep(stepNumber, duration = 1500) {
    const step = document.getElementById(`policy-step-${stepNumber}`);
    if (!step) return;
    
    // Mark as active
    step.classList.add('active');
    
    // Wait
    await new Promise(resolve => setTimeout(resolve, duration));
    
    // Mark as completed
    step.classList.remove('active');
    step.classList.add('completed');
}

// Show processing pipeline
function showProcessingPipeline() {
    const pipeline = document.getElementById('policyProcessingPipeline');
    pipeline.style.display = 'block';
    
    // Reset all steps
    document.querySelectorAll('.processing-pipeline .pipeline-step').forEach(step => {
        step.classList.remove('active', 'completed');
    });
}

// Hide processing pipeline
function hideProcessingPipeline() {
    const pipeline = document.getElementById('policyProcessingPipeline');
    setTimeout(() => {
        pipeline.style.display = 'none';
    }, 2000);
}

// Policy upload form submission
if (document.getElementById('policyUploadForm')) {
    document.getElementById('policyUploadForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (selectedFiles.length === 0) {
            alert('Please select at least one PDF file');
            return;
        }
        
        const policyId = document.getElementById('policyId').value.trim();
        const policyName = document.getElementById('policyName').value.trim();
        const statusDiv = document.getElementById('policyUploadStatus');
        
        try {
            // Show processing pipeline
            showProcessingPipeline();
            statusDiv.style.display = 'none';
            
            // Step 1: Uploading files
            await animatePolicyStep(1, 1000);
            
            const formData = new FormData();
            
            // Add optional fields
            if (policyId) formData.append('policy_id', policyId);
            if (policyName) formData.append('policy_name', policyName);
            
            // Add all selected files
            selectedFiles.forEach(file => {
                formData.append('files', file);
            });
            
            // Upload to server
            const uploadPromise = fetch(`${API_BASE_URL}/api/policies/index`, {
                method: 'POST',
                body: formData
            });
            
            // Step 2: Extracting text (while uploading)
            await animatePolicyStep(2, 2000);
            
            // Wait for upload to complete
            const response = await uploadPromise;
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(errorData.detail || 'Upload failed');
            }
            
            const result = await response.json();
            
            // Step 3: Chunking
            await animatePolicyStep(3, 1500);
            
            // Step 4: Generating embeddings
            await animatePolicyStep(4, 1500);
            
            // Step 5: Storing in Pinecone
            await animatePolicyStep(5, 1000);
            
            // Show success
            statusDiv.style.display = 'block';
            statusDiv.style.color = '#10b981';
            statusDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${result.message}`;
            
            // Reset form
            selectedFiles = [];
            renderFilesList();
            updateSubmitButton();
            e.target.reset();
            
            // Reload policies
            await loadPolicies();
            
            // Hide pipeline and status after delay
            hideProcessingPipeline();
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 5000);
            
        } catch (error) {
            console.error('Error uploading policy:', error);
            
            // Hide pipeline
            document.getElementById('policyProcessingPipeline').style.display = 'none';
            
            // Show error
            statusDiv.style.display = 'block';
            statusDiv.style.color = '#ef4444';
            statusDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> Error: ${error.message}`;
        }
    });
    
    // File input label update
    document.getElementById('policyFile').addEventListener('change', function(e) {
        const fileName = e.target.files[0]?.name || 'Choose PDF file';
        document.querySelector('#policyFile + label span').textContent = fileName;
    });
}

// Rename policy
async function renamePolicy(policyId) {
    // Find current policy name
    const policy = policies.find(p => p.policy_id === policyId);
    if (!policy) return;
    
    const newName = prompt(`Rename policy:\n\nCurrent name: ${policy.policy_name}\n\nEnter new name:`, policy.policy_name);
    
    if (!newName || newName.trim() === '' || newName === policy.policy_name) {
        return; // Cancelled or no change
    }
    
    try {
        // Update policy name via API
        const response = await fetch(`${API_BASE_URL}/api/policies/${policyId}/rename`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ policy_name: newName.trim() })
        });
        
        if (!response.ok) {
            // If endpoint doesn't exist, update locally only
            console.warn('Rename endpoint not available, updating locally');
        }
        
        // Update local state immediately (real-time update)
        policy.policy_name = newName.trim();
        
        // Update UI immediately without reload
        const nameElement = document.getElementById(`name-${policyId}`);
        if (nameElement) {
            nameElement.textContent = newName.trim();
        }
        
        // Update dropdown
        updatePolicyDropdown();
        
        // Show success feedback
        const policyElement = document.getElementById(`policy-${policyId}`);
        if (policyElement) {
            policyElement.style.backgroundColor = '#d1fae5';
            setTimeout(() => {
                policyElement.style.backgroundColor = '';
            }, 1000);
        }
        
    } catch (error) {
        console.error('Error renaming policy:', error);
        alert(`Error: ${error.message}`);
    }
}

// Delete policy with real-time UI update
async function deletePolicy(policyId) {
    const policy = policies.find(p => p.policy_id === policyId);
    const policyName = policy ? policy.policy_name : policyId;
    
    if (!confirm(`Are you sure you want to delete policy "${policyName}"?\n\nThis will remove all indexed data for this policy.`)) {
        return;
    }
    
    // Show deleting animation immediately
    const policyElement = document.getElementById(`policy-${policyId}`);
    if (policyElement) {
        policyElement.style.opacity = '0.5';
        policyElement.style.pointerEvents = 'none';
        const deleteBtn = policyElement.querySelector('.btn-danger');
        if (deleteBtn) {
            deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
            deleteBtn.disabled = true;
        }
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/policies/${policyId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || 'Delete failed');
        }
        
        const result = await response.json();
        
        // Remove from local state immediately
        policies = policies.filter(p => p.policy_id !== policyId);
        
        // Animate removal from DOM
        if (policyElement) {
            policyElement.style.transform = 'translateX(-100%)';
            policyElement.style.transition = 'all 0.3s ease';
            
            setTimeout(() => {
                policyElement.remove();
                
                // Show empty state if no policies left
                if (policies.length === 0) {
                    updatePoliciesList();
                }
            }, 300);
        }
        
        // Update dropdown immediately
        updatePolicyDropdown();
        
        // Show success message briefly
        const successMsg = document.createElement('div');
        successMsg.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #10b981; color: white; padding: 1rem 1.5rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 9999;';
        successMsg.innerHTML = `<i class="fas fa-check-circle"></i> Policy deleted (${result.vectors_deleted} vectors removed)`;
        document.body.appendChild(successMsg);
        
        setTimeout(() => {
            successMsg.remove();
        }, 3000);
        
    } catch (error) {
        console.error('Error deleting policy:', error);
        
        // Restore UI on error
        if (policyElement) {
            policyElement.style.opacity = '';
            policyElement.style.pointerEvents = '';
            const deleteBtn = policyElement.querySelector('.btn-danger');
            if (deleteBtn) {
                deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                deleteBtn.disabled = false;
            }
        }
        
        alert(`Error: ${error.message}`);
    }
}

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
        
        const extractResponse = await fetch(`${API_BASE_URL}/api/documents/extract`, {
            method: 'POST',
            body: formData
        });
        
        if (!extractResponse.ok) {
            const errorData = await extractResponse.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(`Document extraction failed (${extractResponse.status}): ${errorData.detail || extractResponse.statusText}`);
        }
        
        const extractedData = await extractResponse.json();
        step2.querySelector('p').textContent = `Extracted €${extractedData.extracted_data.summary?.totalAmount || 0}`;
        
        // Step 3: AI Analysis - Analyze claim
        const step3 = document.getElementById('step-3');
        step3.querySelector('p').textContent = 'Matching against policy...';
        await animateStep(3);
        
        // Get selected policy
        const selectedPolicy = document.getElementById('policySelect').value;
        if (!selectedPolicy) {
            throw new Error('Please select a policy first');
        }
        
        const analysisResponse = await fetch(`${API_BASE_URL}/api/claims/analyze/${claimId}`, { // Use the same claim ID
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                policy_id: selectedPolicy,
                customer_id: 'DEMO-CUSTOMER'
            })
        });
        
        if (!analysisResponse.ok) {
            const errorData = await analysisResponse.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(`Claim analysis failed (${analysisResponse.status}): ${errorData.detail || analysisResponse.statusText}`);
        }
        
        const analysisData = await analysisResponse.json();
        step3.querySelector('p').textContent = `Calculated ${analysisData.approval_rate.toFixed(1)}% coverage`;
        
        // Step 4: Settlement
        const step4 = document.getElementById('step-4');
        step4.querySelector('p').textContent = `Approved: €${analysisData.total_approved.toFixed(2)}`;
        await animateStep(4);
        
        // Show results with REAL data
        const processingTime = ((Date.now() - startTime) / 1000).toFixed(1);
        showRealResults(analysisData, processingTime, extractedData, claimId);
        
    } catch (error) {
        console.error('Error processing claim:', error);
        
        // Show detailed error message
        let errorMsg = '⚠️ Error processing claim:\n\n';
        errorMsg += error.message + '\n\n';
        
        if (error.message.includes('Failed to fetch')) {
            errorMsg += 'The backend server may not be running.\nMake sure to run: py run.py';
        } else if (error.message.includes('404')) {
            errorMsg += 'API endpoint not found. Check that the server is running on port 8000.';
        } else {
            errorMsg += 'Check the browser console (F12) for more details.';
        }
        
        alert(errorMsg);
        
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

// ============================================================================
// EVENT LISTENERS
// ============================================================================

// File selection handler
if (document.getElementById('policyFile')) {
    document.getElementById('policyFile').addEventListener('change', handleFileSelection);
}

// Clear all files button
if (document.getElementById('clearFiles')) {
    document.getElementById('clearFiles').addEventListener('click', clearAllFiles);
}

// Add more files button
if (document.getElementById('addMoreFiles')) {
    document.getElementById('addMoreFiles').addEventListener('click', addMoreFiles);
}

// Claim document file upload handling
if (document.getElementById('document')) {
    document.getElementById('document').addEventListener('change', function(e) {
        const files = e.target.files;
        const label = document.querySelector('#document + label span');
        
        if (files && files.length > 0) {
            if (files.length === 1) {
                label.textContent = files[0].name;
                countDiv.style.display = 'none';
            } else {
                label.textContent = `${files.length} files selected`;
                countDiv.style.display = 'block';
                countDiv.textContent = `Files: ${Array.from(files).map(f => f.name).join(', ')}`;
            }
        } else {
            label.textContent = 'Choose PDF file(s)';
            countDiv.style.display = 'none';
        }
    });
}

// Claim document file upload handling
document.getElementById('document').addEventListener('change', function(e) {
    const fileName = e.target.files[0]?.name || 'Choose file or drag here';
    document.querySelector('.file-upload span').textContent = fileName;
});

// Initialize on page load
window.addEventListener('DOMContentLoaded', function() {
    // Load policies on page load
    loadPolicies();
});

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
console.log('%cAI Processing API: http://localhost:8000/docs', 'color: #6B7280; font-size: 12px;');
console.log('%cHealth Check: http://localhost:8000/health', 'color: #6B7280; font-size: 12px;');
