// Dashboard-specific JavaScript functionality

const Dashboard = {
    // Initialize dashboard
    init() {
        this.loadQuickStats();
        this.setupWidgetRefresh();
        this.setupQuickActions();
        this.loadRecentActivity();
        this.setupWidgetDragDrop();
        console.log('Dashboard initialized');
    },

    // Load quick statistics
    loadQuickStats() {
        fetch('/api/dashboard/stats')
            .then(response => response.json())
            .then(data => {
                this.updateStatCards(data);
                this.updateProgressIndicators(data);
            })
            .catch(error => {
                console.error('Error loading dashboard stats:', error);
                StudentHub.showToast('Error', 'Failed to load dashboard statistics', 'danger');
            });
    },

    // Update stat cards with new data
    updateStatCards(data) {
        // Update pending tasks
        const pendingTasksElement = document.querySelector('[data-stat="pending-tasks"]');
        if (pendingTasksElement) {
            pendingTasksElement.textContent = data.pending_tasks || 0;
        }

        // Update overdue tasks
        const overdueTasksElement = document.querySelector('[data-stat="overdue-tasks"]');
        if (overdueTasksElement) {
            overdueTasksElement.textContent = data.overdue_tasks || 0;
            // Add warning class if there are overdue tasks
            if (data.overdue_tasks > 0) {
                overdueTasksElement.closest('.card').classList.add('border-warning');
            }
        }

        // Update active streaks
        const activeStreaksElement = document.querySelector('[data-stat="active-streaks"]');
        if (activeStreaksElement) {
            activeStreaksElement.textContent = data.active_streaks || 0;
        }

        // Update goal progress
        const goalProgressElement = document.querySelector('[data-stat="goal-progress"]');
        if (goalProgressElement) {
            goalProgressElement.textContent = `${data.avg_goal_progress || 0}%`;
        }
    },

    // Update progress indicators
    updateProgressIndicators(data) {
        // Habit completion rate
        const habitProgress = document.getElementById('habitProgressBar');
        if (habitProgress) {
            const rate = (data.habits_completed_today / Math.max(data.total_habits, 1)) * 100;
            habitProgress.style.width = `${rate}%`;
            habitProgress.setAttribute('aria-valuenow', rate);
        }

        // Task completion rate
        const taskProgress = document.getElementById('taskProgressBar');
        if (taskProgress) {
            const totalTasks = data.pending_tasks + data.completed_today;
            const rate = totalTasks > 0 ? (data.completed_today / totalTasks) * 100 : 0;
            taskProgress.style.width = `${rate}%`;
            taskProgress.setAttribute('aria-valuenow', rate);
        }
    },

    // Setup widget refresh functionality
    setupWidgetRefresh() {
        // Auto-refresh every 5 minutes
        setInterval(() => {
            this.loadQuickStats();
        }, 5 * 60 * 1000);

        // Manual refresh buttons
        document.querySelectorAll('[data-action="refresh-widget"]').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const widget = button.closest('.card');
                this.refreshWidget(widget);
            });
        });
    },

    // Refresh individual widget
    refreshWidget(widget) {
        if (!widget) return;

        // Add loading state
        widget.classList.add('loading');
        const originalContent = widget.innerHTML;

        // Simulate refresh
        setTimeout(() => {
            widget.classList.remove('loading');
            this.loadQuickStats();
            StudentHub.showToast('Refreshed', 'Widget updated successfully', 'success');
        }, 1000);
    },

    // Setup quick actions
    setupQuickActions() {
        // Quick add task
        const quickTaskForm = document.getElementById('quickTaskForm');
        if (quickTaskForm) {
            quickTaskForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addQuickTask(new FormData(quickTaskForm));
            });
        }

        // Quick add habit completion
        document.querySelectorAll('[data-action="complete-habit"]').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.completeHabit(button.dataset.habitId);
            });
        });

        // Quick add devotion entry
        const quickDevotionBtn = document.getElementById('quickDevotionBtn');
        if (quickDevotionBtn) {
            quickDevotionBtn.addEventListener('click', () => {
                this.showQuickDevotionModal();
            });
        }
    },

    // Add quick task
    addQuickTask(formData) {
        fetch('/tasks/add', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                StudentHub.showToast('Success', 'Task added successfully', 'success');
                this.loadQuickStats();
                // Clear form
                document.getElementById('quickTaskForm').reset();
            } else {
                throw new Error('Failed to add task');
            }
        })
        .catch(error => {
            console.error('Error adding task:', error);
            StudentHub.showToast('Error', 'Failed to add task', 'danger');
        });
    },

    // Complete habit
    completeHabit(habitId) {
        fetch(`/habits/${habitId}/complete`, {
            method: 'POST'
        })
        .then(response => {
            if (response.ok) {
                StudentHub.showToast('Well done!', 'Habit marked as complete', 'success');
                this.loadQuickStats();
                // Update button state
                const button = document.querySelector(`[data-habit-id="${habitId}"]`);
                if (button) {
                    button.classList.add('btn-success');
                    button.classList.remove('btn-outline-success');
                    button.innerHTML = '<i class="fas fa-check"></i> Done';
                    button.disabled = true;
                }
            } else {
                throw new Error('Failed to complete habit');
            }
        })
        .catch(error => {
            console.error('Error completing habit:', error);
            StudentHub.showToast('Error', 'Failed to complete habit', 'danger');
        });
    },

    // Show quick devotion modal
    showQuickDevotionModal() {
        const modalContent = `
            <form id="quickDevotionForm">
                <div class="mb-3">
                    <label for="quickScripture" class="form-label">Scripture</label>
                    <input type="text" class="form-control" id="quickScripture" name="scripture" placeholder="e.g., John 3:16">
                </div>
                <div class="mb-3">
                    <label for="quickReflection" class="form-label">Quick Reflection</label>
                    <textarea class="form-control" id="quickReflection" name="reflection" rows="3" placeholder="What stood out to you today?"></textarea>
                </div>
                <div class="mb-3">
                    <label for="quickDuration" class="form-label">Duration (minutes)</label>
                    <input type="number" class="form-control" id="quickDuration" name="duration_minutes" value="15" min="1">
                </div>
                <button type="submit" class="btn btn-primary">Save Entry</button>
            </form>
        `;

        StudentHub.showModal('Quick Devotion Entry', modalContent);

        // Handle form submission
        document.getElementById('quickDevotionForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addQuickDevotion(new FormData(e.target));
        });
    },

    // Add quick devotion
    addQuickDevotion(formData) {
        formData.append('date', new Date().toISOString().split('T')[0]);
        formData.append('title', 'Quick Entry');

        fetch('/devotion/add', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                StudentHub.showToast('Blessed!', 'Devotion entry saved', 'success');
                bootstrap.Modal.getInstance(document.getElementById('dynamicModal')).hide();
            } else {
                throw new Error('Failed to add devotion');
            }
        })
        .catch(error => {
            console.error('Error adding devotion:', error);
            StudentHub.showToast('Error', 'Failed to save devotion', 'danger');
        });
    },

    // Load recent activity
    loadRecentActivity() {
        // This would typically fetch recent activity data
        // For now, we'll simulate it
        const activities = [
            { type: 'task', text: 'Completed "Study for Math Exam"', time: '2 hours ago', icon: 'fas fa-check text-success' },
            { type: 'habit', text: 'Completed daily Bible reading', time: '3 hours ago', icon: 'fas fa-book text-info' },
            { type: 'goal', text: 'Updated "Learn Spanish" progress to 65%', time: '1 day ago', icon: 'fas fa-bullseye text-warning' },
            { type: 'devotion', text: 'Added devotion entry', time: '2 days ago', icon: 'fas fa-pray text-primary' }
        ];

        const activityContainer = document.getElementById('recentActivity');
        if (activityContainer) {
            activityContainer.innerHTML = activities.map(activity => `
                <div class="d-flex align-items-center mb-3">
                    <div class="flex-shrink-0">
                        <i class="${activity.icon}"></i>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <div class="text-sm">${activity.text}</div>
                        <small class="text-muted">${activity.time}</small>
                    </div>
                </div>
            `).join('');
        }
    },

    // Setup widget drag and drop (for future customization)
    setupWidgetDragDrop() {
        // This would implement drag and drop for widget reordering
        // Placeholder for future implementation
        console.log('Widget drag and drop setup (placeholder)');
    },

    // Update motivational quote
    updateMotivationalQuote() {
        const quotes = [
            { text: "The future belongs to those who believe in the beauty of their dreams.", author: "Eleanor Roosevelt" },
            { text: "Education is the most powerful weapon which you can use to change the world.", author: "Nelson Mandela" },
            { text: "Success is not final, failure is not fatal: it is the courage to continue that counts.", author: "Winston Churchill" },
            { text: "Trust in the Lord with all your heart and lean not on your own understanding.", author: "Proverbs 3:5" },
            { text: "For I know the plans I have for you, declares the Lord, plans to prosper you.", author: "Jeremiah 29:11" }
        ];

        const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
        const quoteElement = document.getElementById('motivationalQuote');
        
        if (quoteElement) {
            quoteElement.innerHTML = `
                <blockquote class="blockquote text-center">
                    <p class="mb-0">"${randomQuote.text}"</p>
                    <footer class="blockquote-footer mt-2">
                        <cite title="Source Title">${randomQuote.author}</cite>
                    </footer>
                </blockquote>
            `;
        }
    },

    // Calculate and display productivity score
    calculateProductivityScore(stats) {
        let score = 0;
        let maxScore = 100;

        // Tasks completion (30 points max)
        const taskCompletionRate = stats.completed_today / Math.max(stats.pending_tasks + stats.completed_today, 1);
        score += taskCompletionRate * 30;

        // Habits completion (25 points max)
        const habitCompletionRate = stats.habits_completed_today / Math.max(stats.total_habits, 1);
        score += habitCompletionRate * 25;

        // Goal progress (25 points max)
        score += (stats.avg_goal_progress / 100) * 25;

        // Penalty for overdue tasks (-10 points max)
        score -= Math.min(stats.overdue_tasks * 2, 10);

        // Bonus for streaks (+20 points max)
        score += Math.min(stats.active_streaks * 0.5, 20);

        score = Math.max(0, Math.min(100, Math.round(score)));

        const scoreElement = document.getElementById('productivityScore');
        if (scoreElement) {
            scoreElement.textContent = `${score}%`;
            
            // Update score color based on value
            scoreElement.className = `h3 ${score >= 80 ? 'text-success' : score >= 60 ? 'text-warning' : 'text-danger'}`;
        }

        return score;
    },

    // Setup weather widget (placeholder)
    setupWeatherWidget() {
        // This would integrate with a weather API
        // Placeholder implementation
        const weatherWidget = document.getElementById('weatherWidget');
        if (weatherWidget) {
            weatherWidget.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-sun fa-2x text-warning mb-2"></i>
                    <h6>72°F</h6>
                    <small class="text-muted">Sunny</small>
                </div>
            `;
        }
    }
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname === '/' || window.location.pathname === '/dashboard') {
        Dashboard.init();
    }
});

// Export for global access
window.Dashboard = Dashboard;
