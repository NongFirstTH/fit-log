// Main JavaScript file for Fit Log application

// Global variables
let currentUser = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    addAnimations();
});

// Initialize application
function initializeApp() {
    // Set current date for date inputs
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = today;
        }
    });

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Form validation
    setupFormValidation();
    
    // Auto-save functionality
    setupAutoSave();
    
    // Keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Theme toggle
    setupThemeToggle();
}

// Form validation
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Find first invalid field and focus
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    showNotification('กรุณากรอกข้อมูลให้ครบถ้วน', 'warning');
                }
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });
}

// Auto-save functionality for forms
function setupAutoSave() {
    const autoSaveForms = document.querySelectorAll('[data-auto-save]');
    
    autoSaveForms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('input', debounce(function() {
                saveFormData(form);
            }, 1000));
        });
        
        // Load saved data on page load
        loadFormData(form);
    });
}

// Save form data to localStorage
function saveFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    const formId = form.id || form.getAttribute('data-form-id');
    if (formId) {
        localStorage.setItem(`fitlog_form_${formId}`, JSON.stringify(data));
        showNotification('ข้อมูลถูกบันทึกอัตโนมัติ', 'info', 2000);
    }
}

// Load form data from localStorage
function loadFormData(form) {
    const formId = form.id || form.getAttribute('data-form-id');
    if (formId) {
        const savedData = localStorage.getItem(`fitlog_form_${formId}`);
        if (savedData) {
            const data = JSON.parse(savedData);
            
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input && !input.value) {
                    input.value = data[key];
                }
            });
        }
    }
}

// Clear saved form data
function clearFormData(formId) {
    localStorage.removeItem(`fitlog_form_${formId}`);
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S to save (prevent default and trigger form submit)
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const activeForm = document.querySelector('form:focus-within');
            if (activeForm) {
                const submitBtn = activeForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
        }
        
        // Ctrl/Cmd + N for new entry (redirect to add form)
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const currentPage = window.location.pathname;
            if (currentPage.includes('activity')) {
                document.getElementById('activity_name')?.focus();
            } else if (currentPage.includes('weight')) {
                document.getElementById('weight')?.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                bootstrap.Modal.getInstance(modal)?.hide();
            });
        }
    });
}

// Theme toggle functionality
function setupThemeToggle() {
    const themeToggle = document.createElement('button');
    themeToggle.className = 'btn btn-outline-light btn-sm position-fixed';
    themeToggle.style.cssText = 'top: 20px; right: 20px; z-index: 1050;';
    themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    themeToggle.title = 'Toggle Dark Mode';
    
    document.body.appendChild(themeToggle);
    
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        
        this.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        localStorage.setItem('fitlog_theme', isDark ? 'dark' : 'light');
    });
    
    // Load saved theme
    const savedTheme = localStorage.getItem('fitlog_theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
}

// Add animations to elements
function addAnimations() {
    // Animate cards on scroll
    const cards = document.querySelectorAll('.card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, { threshold: 0.1 });
    
    cards.forEach(card => {
        observer.observe(card);
    });
    
    // Animate stats numbers
    animateStatsNumbers();
    
    // Animate progress bars
    animateProgressBars();
}

// Animate stats numbers with counting effect
function animateStatsNumbers() {
    const statsNumbers = document.querySelectorAll('.stats-number');
    
    statsNumbers.forEach(element => {
        const targetValue = parseFloat(element.textContent);
        if (isNaN(targetValue)) return;
        
        let currentValue = 0;
        const increment = targetValue / 50;
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= targetValue) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            
            if (targetValue % 1 === 0) {
                element.textContent = Math.floor(currentValue);
            } else {
                element.textContent = currentValue.toFixed(1);
            }
        }, 40);
    });
}

// Animate progress bars
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const targetWidth = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 2s ease-in-out';
            bar.style.width = targetWidth;
        }, 500);
    });
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

function formatNumber(num) {
    return new Intl.NumberFormat('th-TH').format(num);
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('th-TH', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Show notification
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 100px; right: 20px; z-index: 1060; max-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto dismiss
    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 150);
        }
    }, duration);
}

// BMI Calculator
function calculateBMI(weight, height) {
    const heightInMeters = height / 100;
    return weight / (heightInMeters * heightInMeters);
}

function getBMICategory(bmi) {
    if (bmi < 18.5) return { category: 'น้ำหนักน้อย', color: 'info' };
    if (bmi < 25) return { category: 'น้ำหนักปกติ', color: 'success' };
    if (bmi < 30) return { category: 'น้ำหนักเกิน', color: 'warning' };
    return { category: 'อ้วน', color: 'danger' };
}

// Activity calorie estimator
function estimateCalories(activityType, duration, weight) {
    const metValues = {
        'walking_slow': 2.5,
        'walking_moderate': 3.5,
        'walking_fast': 4.3,
        'jogging': 7.0,
        'running': 9.8,
        'cycling_leisure': 4.0,
        'cycling_moderate': 8.0,
        'swimming': 6.0,
        'weight_training': 3.5,
        'yoga': 2.5,
        'aerobics': 6.5,
        'basketball': 8.0,
        'soccer': 10.0,
        'tennis': 7.3,
        'badminton': 5.5,
        'dancing': 4.8
    };
    
    const met = metValues[activityType] || 3.5;
    return Math.round(met * weight * (duration / 60));
}

// Chart utilities
function createSimpleChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    // Simple chart implementation using Canvas API
    const canvas = ctx.getContext('2d');
    const width = ctx.width;
    const height = ctx.height;
    
    // Clear canvas
    canvas.clearRect(0, 0, width, height);
    
    // Draw simple line chart
    if (data.length > 0) {
        const maxValue = Math.max(...data.map(d => d.value));
        const minValue = Math.min(...data.map(d => d.value));
        const range = maxValue - minValue || 1;
        
        canvas.strokeStyle = '#667eea';
        canvas.lineWidth = 3;
        canvas.beginPath();
        
        data.forEach((point, index) => {
            const x = (width / (data.length - 1)) * index;
            const y = height - ((point.value - minValue) / range) * height;
            
            if (index === 0) {
                canvas.moveTo(x, y);
            } else {
                canvas.lineTo(x, y);
            }
        });
        
        canvas.stroke();
    }
    
    return ctx;
}

// Data export functionality
function exportData(data, filename, format = 'json') {
    let content, mimeType;
    
    switch (format) {
        case 'csv':
            content = convertToCSV(data);
            mimeType = 'text/csv';
            break;
        case 'json':
        default:
            content = JSON.stringify(data, null, 2);
            mimeType = 'application/json';
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function convertToCSV(data) {
    if (!Array.isArray(data) || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(',')];
    
    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            return typeof value === 'string' ? `"${value}"` : value;
        });
        csvRows.push(values.join(','));
    });
    
    return csvRows.join('\n');
}

// Performance monitoring
function trackPerformance() {
    if ('performance' in window) {
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart + 'ms');
        });
    }
}

// Initialize performance tracking
trackPerformance();

// Service Worker registration for PWA capabilities
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('ServiceWorker registration successful');
            })
            .catch(err => {
                console.log('ServiceWorker registration failed');
            });
    });
}