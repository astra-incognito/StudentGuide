// Main application JavaScript for Student Productivity Hub

// Global app configuration
const StudentHub = {
    config: {
        notifications: {
            enabled: true,
            defaultTimeout: 5000
        },
        theme: 'dark',
        version: '1.0.0'
    },
    
    // Initialize the application
    init() {
        this.setupNotifications();
        this.setupKeyboardShortcuts();
        this.setupFormValidation();
        this.setupProgressBars();
        this.setupTooltips();
        this.loadUserPreferences();
        this.setupAutoSave();
        console.log('Student Hub initialized successfully');
    },

    // Setup browser notifications
    setupNotifications() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                console.log('Notification permission:', permission);
            });
        }
    },

    // Show notification
    showNotification(title, message, type = 'info') {
        // Browser notification
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/images/favicon.ico',
                badge: '/static/images/badge.png'
            });
        }

        // In-app notification
        this.showToast(title, message, type);
    },

    // Show toast notification
    showToast(title, message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong><br>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        // Add to toast container or create one
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        container.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    // Setup keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 't':
                        e.preventDefault();
                        this.openAddTaskModal();
                        break;
                    case 'e':
                        e.preventDefault();
                        this.openAddEventModal();
                        break;
                    case 'h':
                        e.preventDefault();
                        window.location.href = '/habits';
                        break;
                    case 'g':
                        e.preventDefault();
                        window.location.href = '/goals';
                        break;
                    case '/':
                        e.preventDefault();
                        this.showKeyboardShortcuts();
                        break;
                }
            }
        });
    },

    // Open add task modal if available
    openAddTaskModal() {
        const modal = document.getElementById('addTaskModal');
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        } else {
            window.location.href = '/tasks';
        }
    },

    // Open add event modal if available
    openAddEventModal() {
        const modal = document.getElementById('addEventModal');
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        } else {
            window.location.href = '/calendar';
        }
    },

    // Show keyboard shortcuts modal
    showKeyboardShortcuts() {
        const shortcuts = [
            { key: 'Ctrl + T', action: 'Add new task' },
            { key: 'Ctrl + E', action: 'Add new event' },
            { key: 'Ctrl + H', action: 'Go to habits' },
            { key: 'Ctrl + G', action: 'Go to goals' },
            { key: 'Ctrl + /', action: 'Show shortcuts' },
            { key: 'Esc', action: 'Close modals' }
        ];

        let shortcutsList = shortcuts.map(s => 
            `<tr><td><code>${s.key}</code></td><td>${s.action}</td></tr>`
        ).join('');

        this.showModal('Keyboard Shortcuts', `
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Shortcut</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${shortcutsList}
                </tbody>
            </table>
        `);
    },

    // Generic modal display
    showModal(title, content, size = '') {
        const modalId = 'dynamicModal';
        let modal = document.getElementById(modalId);
        
        if (!modal) {
            modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = modalId;
            modal.innerHTML = `
                <div class="modal-dialog ${size}">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${content}
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        } else {
            modal.querySelector('.modal-title').textContent = title;
            modal.querySelector('.modal-body').innerHTML = content;
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    },

    // Setup form validation
    setupFormValidation() {
        // Add validation to all forms
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                    this.showToast('Validation Error', 'Please check your input and try again.', 'danger');
                }
                form.classList.add('was-validated');
            });
        });

        // Real-time validation for required fields
        document.querySelectorAll('input[required], textarea[required], select[required]').forEach(field => {
            field.addEventListener('blur', () => {
                if (!field.checkValidity()) {
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                    field.classList.add('is-valid');
                }
            });
        });
    },

    // Setup animated progress bars
    setupProgressBars() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressBar = entry.target.querySelector('.progress-bar');
                    if (progressBar) {
                        const width = progressBar.getAttribute('aria-valuenow');
                        progressBar.style.width = '0%';
                        setTimeout(() => {
                            progressBar.style.width = width + '%';
                        }, 100);
                    }
                }
            });
        });

        document.querySelectorAll('.progress').forEach(progress => {
            observer.observe(progress);
        });
    },

    // Setup tooltips
    setupTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize Bootstrap popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(popoverTriggerEl => {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    },

    // Load user preferences
    loadUserPreferences() {
        const preferences = this.getStoredPreferences();
        
        // Apply theme
        if (preferences.theme && preferences.theme !== 'dark') {
            document.documentElement.setAttribute('data-bs-theme', preferences.theme);
        }

        // Apply other preferences
        if (preferences.compactMode) {
            document.body.classList.add('compact-mode');
        }

        if (!preferences.animations) {
            document.body.classList.add('no-animations');
        }
    },

    // Get stored preferences
    getStoredPreferences() {
        try {
            return JSON.parse(localStorage.getItem('studentHub_preferences')) || {};
        } catch (error) {
            console.warn('Error loading preferences:', error);
            return {};
        }
    },

    // Save preferences
    savePreferences(preferences) {
        try {
            localStorage.setItem('studentHub_preferences', JSON.stringify(preferences));
        } catch (error) {
            console.warn('Error saving preferences:', error);
        }
    },

    // Setup auto-save functionality
    setupAutoSave() {
        let saveTimeout;
        
        document.querySelectorAll('input, textarea, select').forEach(field => {
            if (field.type !== 'password' && field.type !== 'submit') {
                field.addEventListener('input', () => {
                    clearTimeout(saveTimeout);
                    saveTimeout = setTimeout(() => {
                        this.autoSaveFormData(field.form);
                    }, 1000);
                });
            }
        });
    },

    // Auto-save form data
    autoSaveFormData(form) {
        if (!form || form.dataset.noAutosave) return;

        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        const formId = form.id || form.action.split('/').pop();
        localStorage.setItem(`studentHub_autosave_${formId}`, JSON.stringify(data));
    },

    // Restore auto-saved data
    restoreAutoSavedData(form) {
        const formId = form.id || form.action.split('/').pop();
        const saved = localStorage.getItem(`studentHub_autosave_${formId}`);
        
        if (saved) {
            try {
                const data = JSON.parse(saved);
                Object.keys(data).forEach(key => {
                    const field = form.querySelector(`[name="${key}"]`);
                    if (field) {
                        field.value = data[key];
                    }
                });
            } catch (error) {
                console.warn('Error restoring auto-saved data:', error);
            }
        }
    },

    // Clear auto-saved data
    clearAutoSavedData(form) {
        const formId = form.id || form.action.split('/').pop();
        localStorage.removeItem(`studentHub_autosave_${formId}`);
    },

    // Modern Task Interactions

    markTaskComplete(checkbox) {
        if (checkbox.checked) {
            const taskId = checkbox.getAttribute('data-task-id');
            fetch(`/tasks/${taskId}/complete`, { method: 'POST' })
                .then(() => window.location.reload());
        }
    },

    fillEditTaskForm(btn) {
        const row = btn.closest('tr');
        const taskId = btn.getAttribute('data-task-id');
        document.getElementById('editTaskForm').setAttribute('action', `/tasks/${taskId}/edit`);
        document.getElementById('edit_title').value = row.querySelector('h6').innerText;
        document.getElementById('edit_description').value = row.querySelector('small') ? row.querySelector('small').innerText : '';
        document.getElementById('edit_category').value = row.querySelector('.badge.bg-secondary').innerText.toLowerCase();
        document.getElementById('edit_priority').value = row.querySelector('.badge.bg-danger, .badge.bg-warning, .badge.bg-info, .badge.bg-secondary').innerText.toLowerCase();
        document.getElementById('edit_due_date').value = row.querySelector('td:nth-child(4)').innerText.trim().match(/\d{2}\/\d{2}\/\d{4}/) ? row.querySelector('td:nth-child(4)').innerText.trim().match(/\d{2}\/\d{2}\/\d{4}/)[0].split('/').reverse().join('-') : '';
        // Course select left as default
        const editModal = new bootstrap.Modal(document.getElementById('editTaskModal'));
        editModal.show();
    },

    // Utility functions
    utils: {
        // Format date
        formatDate(date, format = 'MM/DD/YYYY') {
            if (!date) return '';
            
            const d = new Date(date);
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            const year = d.getFullYear();
            
            return format
                .replace('MM', month)
                .replace('DD', day)
                .replace('YYYY', year);
        },

        // Format time
        formatTime(time) {
            if (!time) return '';
            
            const [hours, minutes] = time.split(':');
            const hour12 = hours % 12 || 12;
            const ampm = hours < 12 ? 'AM' : 'PM';
            
            return `${hour12}:${minutes} ${ampm}`;
        },

        // Calculate days between dates
        daysBetween(date1, date2) {
            const oneDay = 24 * 60 * 60 * 1000;
            const firstDate = new Date(date1);
            const secondDate = new Date(date2);
            
            return Math.round(Math.abs((firstDate - secondDate) / oneDay));
        },

        // Debounce function
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        // Throttle function
        throttle(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },

        // Generate unique ID
        generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substr(2);
        },

        // Sanitize HTML
        sanitizeHtml(str) {
            const temp = document.createElement('div');
            temp.textContent = str;
            return temp.innerHTML;
        }
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    StudentHub.init();

    // Mark task as complete via checkbox
    document.querySelectorAll('.mark-complete-checkbox').forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            StudentHub.markTaskComplete(this);
        });
    });

    // Edit task button opens modal and fills form
    document.querySelectorAll('.edit-task-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            StudentHub.fillEditTaskForm(this);
        });
    });
});

// Calendar month navigation (client-side only)
document.addEventListener('DOMContentLoaded', function() {
    const prevBtn = document.getElementById('prevMonthBtn');
    const nextBtn = document.getElementById('nextMonthBtn');
    if (prevBtn && nextBtn) {
        let currentMonth = new Date().getMonth();
        let currentYear = new Date().getFullYear();
        function updateCalendar(month, year) {
            window.location.href = `?month=${month+1}&year=${year}`;
        }
        prevBtn.addEventListener('click', function(e) {
            e.preventDefault();
            currentMonth--;
            if (currentMonth < 0) {
                currentMonth = 11;
                currentYear--;
            }
            updateCalendar(currentMonth, currentYear);
        });
        nextBtn.addEventListener('click', function(e) {
            e.preventDefault();
            currentMonth++;
            if (currentMonth > 11) {
                currentMonth = 0;
                currentYear++;
            }
            updateCalendar(currentMonth, currentYear);
        });
    }
});

// Calendar quick add event (fix for modal and date)
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.add-quick-event-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const day = btn.getAttribute('data-day');
            const urlParams = new URLSearchParams(window.location.search);
            const month = urlParams.get('month') ? parseInt(urlParams.get('month')) : (new Date().getMonth() + 1);
            const year = urlParams.get('year') ? parseInt(urlParams.get('year')) : new Date().getFullYear();
            document.getElementById('start_date').value = `${year}-${String(month).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
            const addEventModal = new bootstrap.Modal(document.getElementById('addEventModal'));
            addEventModal.show();
        });
    });
});

// Export for use in other scripts
window.StudentHub = StudentHub;
