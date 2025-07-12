// Main JavaScript file for SkillSwap

// Global variables
let currentUser = null;
let skills = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Add event listeners
    addEventListeners();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Load initial data if needed
    loadInitialData();
}

function addEventListeners() {
    // Form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmission);
    });
    
    // Search functionality
    const searchInput = document.getElementById('searchFilter');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
    
    // Filter changes
    const filterSelects = document.querySelectorAll('select[id$="Filter"]');
    filterSelects.forEach(select => {
        select.addEventListener('change', handleFilterChange);
    });
    
    // Modal events
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', handleModalShow);
        modal.addEventListener('hidden.bs.modal', handleModalHide);
    });
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function loadInitialData() {
    // Load skills if on skills page
    if (window.location.pathname === '/skills') {
        loadSkills();
    }
}

// Form handling
function handleFormSubmission(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        // Show loading state
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<span class="loading"></span> Loading...';
        submitButton.disabled = true;
        
        // Re-enable after a delay (in case of validation errors)
        setTimeout(() => {
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        }, 3000);
    }
}

// Search functionality
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

// Filter functionality
function handleFilterChange(event) {
    const filterType = event.target.id.replace('Filter', '');
    const filterValue = event.target.value;
    
    console.log(`Filter changed: ${filterType} = ${filterValue}`);
    // Implement filter logic here
}

// Modal handling
function handleModalShow(event) {
    const modal = event.target;
    console.log(`Modal opened: ${modal.id}`);
}

function handleModalHide(event) {
    const modal = event.target;
    console.log(`Modal closed: ${modal.id}`);
    
    // Reset form if it's a modal with a form
    const form = modal.querySelector('form');
    if (form) {
        form.reset();
    }
}

// API functions
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

// Utility functions
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

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function updateSkillsDisplay(skills) {
    // This function would update the skills display
    // Implementation depends on the current page structure
    console.log('Skills loaded:', skills.length);
}

// Animation functions
function animateElement(element, animation) {
    element.classList.add(animation);
    element.addEventListener('animationend', () => {
        element.classList.remove(animation);
    });
}

// Validation functions
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

// Export functions for use in templates
window.SkillSwap = {
    createSkill,
    loadSkills,
    showNotification,
    validateEmail,
    validatePassword,
    animateElement
}; 