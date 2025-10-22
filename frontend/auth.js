// Authentication JavaScript
const API_BASE_URL = 'http://localhost:8000';

// Tab switching
function switchTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.auth-tab').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update forms
    document.querySelectorAll('.auth-form').forEach(form => {
        form.classList.remove('active');
    });
    document.getElementById(`${tab}-form`).classList.add('active');

    // Clear messages
    hideMessages();
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    document.getElementById('success-message').style.display = 'none';
}

// Show success message
function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    document.getElementById('error-message').style.display = 'none';
}

// Hide messages
function hideMessages() {
    document.getElementById('error-message').style.display = 'none';
    document.getElementById('success-message').style.display = 'none';
}

// Handle login
async function handleLogin(event) {
    event.preventDefault();
    hideMessages();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        // Create form data (OAuth2PasswordRequestForm expects form data)
        const formData = new FormData();
        formData.append('username', email);  // OAuth2 uses 'username' field
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            body: formData,
            credentials: 'include'  // Include cookies
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        // Store tokens
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('token_expires_at', Date.now() + (data.expires_in * 1000));

        showSuccess('Login successful! Redirecting...');

        // Redirect to main app
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1000);

    } catch (error) {
        console.error('Login error:', error);
        showError(error.message || 'Login failed. Please try again.');
    }
}

// Handle registration
async function handleRegister(event) {
    event.preventDefault();
    hideMessages();

    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password,
                full_name: name || null
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Registration failed');
        }

        showSuccess('Account created successfully! Please login.');

        // Switch to login tab after 2 seconds
        setTimeout(() => {
            document.getElementById('register-form').reset();
            const loginTab = document.querySelector('.auth-tab:first-child');
            loginTab.click();
        }, 2000);

    } catch (error) {
        console.error('Registration error:', error);
        showError(error.message || 'Registration failed. Please try again.');
    }
}

// Login with Google
function loginWithGoogle() {
    // Redirect to Google OAuth endpoint
    window.location.href = `${API_BASE_URL}/auth/google/login`;
}

// Check if already logged in
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const expiresAt = localStorage.getItem('token_expires_at');

    if (token && expiresAt && Date.now() < parseInt(expiresAt)) {
        // Already logged in, redirect to main app
        window.location.href = 'index.html';
    }
}

// Run on page load
checkAuth();

