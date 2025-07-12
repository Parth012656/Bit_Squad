// ========================
// SkillSwap - Main Script
// ========================

// Global state variables
let currentUser = null;   // Stores info about the currently logged-in user
let skills = [];          // List of all skills fetched from backend

// Wait for the page to load before initializing the app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Bootstraps the app once DOM is ready
function initializeApp() {
    addEventListeners();
    initializeTooltips();
    loadInitialData();
}

// Attach all necessary event listeners for forms, filters, modals, etc.
function addEventListeners() {
    // Handle all form submissions globally
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmission);
    });

    // Setup real-time search filter (debounced)
    const searchInput = document.getElementById('searchFilter');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }

    // Watch for filter dropdown changes
    const filterSelects = document.querySelectorAll('select[id$="Filter"]');
    filterSelects.forEach(select => {
        select.addEventListener('change', handleFilterChange);
    });

    // Modal open/close event hooks
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', handleModalShow);
        modal.addEventListener('hidden.bs.modal', handleModalHide);
    });
}

// Initialize Bootstrap tooltips across the app
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Check current route and load relevant data on page load
function loadInitialData() {
    if (window.location.pathname === '/skills') {
        loadSkills();  // Load all skills only on skills page
    }
}

// Basic form submission UX — disables button & shows loading state
function handleFormSubmission(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');

    if (submitButton) {
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<span class="loading"></span> Loading...';
        submitButton.disabled = true;

        // Reset after 3s — this can be adjusted based on response time
        setTimeout(() => {
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        }, 3000);
    }
}

// Live search filtering for skill cards (title, description, category)
function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const skillCards = document.querySelectorAll('.skill-card');

    skillCards.forEach(card => {
        const skillName = card.querySelector('.card-title').textContent.toLowerCase();
        const skillDescription = card.querySelector('.card-text').textContent.toLowerCase();
        const skillCategory = card.querySelector('.badge').textContent.toLowerCase();

        const matches = skillName.includes(searchTerm) || 
                       skillDescription.includes(searchTerm) || 
                       skillCategory.includes(searchTerm);

        card.style.display = matches ? 'block' : 'none';
    });
}

// Triggered when any dropdown filter value changes
function handleFilterChange(event) {
    const filterType = event.target.id.replace('Filter', '');
    const filterValue = event.target.value;
    
    console.log(`Filter changed: ${filterType} = ${filterValue}`);
    // Add actual filtering logic here (based on backend/frontend setup)
}

// Logs when modal is opened (can be expanded later for data pre-fill)
function handleModalShow(event) {
    const modal = event.target;
    console.log(`Modal opened: ${modal.id}`);
}

// Clears form inside modal when closed (resets modal state)
function handleModalHide(event) {
    const modal = event.target;
    console.log(`Modal closed: ${modal.id}`);

    const form = modal.querySelector('form');
    if (form) {
        form.reset();
    }
}

// Fetch all available skills from backend API
async function loadSkills() {
    try {
        const response = await fetch('/api/skills');
        const data = await response.json();
        skills = data;
        updateSkillsDisplay(data);
    } catch (error) {
        console.error('Error loading skills:', error);
        showNotification('Error loading skills', 'error');
    }
}

// Send skill creation request to backend
async function createSkill(skillData) {
    try {
        const response = await fetch('/api/skills', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(skillData)
        });

        if (response.ok) {
            const newSkill = await response.json();
            showNotification('Skill created successfully!', 'success');
            return newSkill;
        } else {
            throw new Error('Failed to create skill');
        }
    } catch (error) {
        console.error('Error creating skill:', error);
        showNotification('Error creating skill', 'error');
        throw error;
    }
}

// Debounce utility to limit function call frequency
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Display alert-style notifications (auto-dismiss after 5s)
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Update UI with newly fetched skill data (to be implemented as needed)
function updateSkillsDisplay(skills) {
    console.log('Skills loaded:', skills.length);
    // Actual DOM injection goes here if needed
}

// Add temporary CSS animation to an element
function animateElement(element, animation) {
    element.classList.add(animation);
    element.addEventListener('animationend', () => {
        element.classList.remove(animation);
    });
}

// Email validation (simple regex)
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Password must be at least 6 characters long
function validatePassword(password) {
    return password.length >= 6;
}

// Make selected functions globally available to other scripts or templates
window.SkillSwap = {
    createSkill,
    loadSkills,
    showNotification,
    validateEmail,
    validatePassword,
    animateElement
};
