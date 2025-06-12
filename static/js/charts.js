// Chart functionality for Student Productivity Hub

const Charts = {
    // Default chart configuration
    defaultConfig: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: '#fff',
                    usePointStyle: true,
                    padding: 20
                }
            }
        },
        scales: {
            x: {
                ticks: { color: '#fff' },
                grid: { color: 'rgba(255, 255, 255, 0.1)' }
            },
            y: {
                ticks: { color: '#fff' },
                grid: { color: 'rgba(255, 255, 255, 0.1)' }
            }
        }
    },

    // Color schemes
    colors: {
        primary: '#0d6efd',
        success: '#198754',
        danger: '#dc3545',
        warning: '#ffc107',
        info: '#0dcaf0',
        secondary: '#6c757d',
        light: '#f8f9fa',
        dark: '#212529'
    },

    // Initialize all charts
    init() {
        this.initializeHabitCharts();
        this.initializeFinanceCharts();
        this.initializeGoalCharts();
        this.initializeProductivityChart();
        console.log('Charts initialized');
    },

    // Create habit tracking chart
    createHabitChart(data) {
        const ctx = document.getElementById('habitChart');
        if (!ctx) return;

        // Prepare data for streak comparison
        const labels = data.map(habit => habit.name);
        const currentStreaks = data.map(habit => habit.streak);
        const bestStreaks = data.map(habit => habit.best_streak);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Current Streak',
                        data: currentStreaks,
                        backgroundColor: this.colors.primary,
                        borderColor: this.colors.primary,
                        borderWidth: 1
                    },
                    {
                        label: 'Best Streak',
                        data: bestStreaks,
                        backgroundColor: this.colors.success,
                        borderColor: this.colors.success,
                        borderWidth: 1
                    }
                ]
            },
            options: {
                ...this.defaultConfig,
                plugins: {
                    ...this.defaultConfig.plugins,
                    title: {
                        display: true,
                        text: 'Habit Streaks Comparison',
                        color: '#fff'
                    }
                },
                scales: {
                    ...this.defaultConfig.scales,
                    y: {
                        ...this.defaultConfig.scales.y,
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Days',
                            color: '#fff'
                        }
                    }
                }
            }
        });
    },

    // Create expense breakdown chart
    createExpenseChart(data) {
        const ctx = document.getElementById('expenseChart');
        if (!ctx) return;

        const backgroundColors = [
            this.colors.primary,
            this.colors.success,
            this.colors.danger,
            this.colors.warning,
            this.colors.info,
            this.colors.secondary
        ];

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: backgroundColors.slice(0, data.labels.length),
                    borderWidth: 2,
                    borderColor: '#212529'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#fff',
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    title: {
                        display: true,
                        text: 'Expense Categories',
                        color: '#fff'
                    }
                }
            }
        });
    },

    // Create goal progress chart
    createGoalProgressChart(goals) {
        const ctx = document.getElementById('goalProgressChart');
        if (!ctx) return;

        const labels = goals.map(goal => goal.title);
        const progress = goals.map(goal => goal.progress);

        new Chart(ctx, {
            type: 'horizontalBar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Progress (%)',
                    data: progress,
                    backgroundColor: progress.map(p => {
                        if (p >= 80) return this.colors.success;
                        if (p >= 60) return this.colors.info;
                        if (p >= 40) return this.colors.warning;
                        return this.colors.danger;
                    }),
                    borderWidth: 1
                }]
            },
            options: {
                ...this.defaultConfig,
                indexAxis: 'y',
                plugins: {
                    ...this.defaultConfig.plugins,
                    title: {
                        display: true,
                        text: 'Goal Progress',
                        color: '#fff'
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { 
                            color: '#fff',
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        ticks: { color: '#fff' },
                        grid: { display: false }
                    }
                }
            }
        });
    },

    // Create productivity trend chart
    createProductivityChart(data) {
        const ctx = document.getElementById('productivityChart');
        if (!ctx) return;

        // Generate sample data for the last 7 days
        const dates = [];
        const productivity = [];
        
        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            dates.push(date.toLocaleDateString());
            // Simulate productivity data
            productivity.push(Math.floor(Math.random() * 40) + 60);
        }

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Productivity Score',
                    data: productivity,
                    borderColor: this.colors.primary,
                    backgroundColor: this.colors.primary + '20',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                }]
            },
            options: {
                ...this.defaultConfig,
                plugins: {
                    ...this.defaultConfig.plugins,
                    title: {
                        display: true,
                        text: 'Productivity Trend (Last 7 Days)',
                        color: '#fff'
                    }
                },
                scales: {
                    ...this.defaultConfig.scales,
                    y: {
                        ...this.defaultConfig.scales.y,
                        min: 0,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Score (%)',
                            color: '#fff'
                        }
                    }
                }
            }
        });
    },

    // Create task completion chart
    createTaskCompletionChart(data) {
        const ctx = document.getElementById('taskCompletionChart');
        if (!ctx) return;

        const completedTasks = data.completed || 0;
        const pendingTasks = data.pending || 0;
        const overdueTasks = data.overdue || 0;

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Completed', 'Pending', 'Overdue'],
                datasets: [{
                    data: [completedTasks, pendingTasks, overdueTasks],
                    backgroundColor: [
                        this.colors.success,
                        this.colors.info,
                        this.colors.danger
                    ],
                    borderWidth: 2,
                    borderColor: '#212529'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#fff',
                            usePointStyle: true
                        }
                    },
                    title: {
                        display: true,
                        text: 'Task Status Distribution',
                        color: '#fff'
                    }
                }
            }
        });
    },

    // Create study time chart
    createStudyTimeChart(data) {
        const ctx = document.getElementById('studyTimeChart');
        if (!ctx) return;

        // Sample data for study time by subject
        const subjects = ['Mathematics', 'Science', 'Literature', 'History', 'Foreign Language'];
        const studyHours = [12, 8, 6, 4, 10];

        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: subjects,
                datasets: [{
                    label: 'Hours This Week',
                    data: studyHours,
                    borderColor: this.colors.primary,
                    backgroundColor: this.colors.primary + '30',
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#fff' }
                    },
                    title: {
                        display: true,
                        text: 'Study Time by Subject',
                        color: '#fff'
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        ticks: { color: '#fff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        pointLabels: { color: '#fff' }
                    }
                }
            }
        });
    },

    // Create financial trend chart
    createFinancialTrendChart(data) {
        const ctx = document.getElementById('financialTrendChart');
        if (!ctx) return;

        // Generate sample monthly data
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        const income = [800, 850, 900, 800, 950, 900];
        const expenses = [650, 700, 750, 720, 680, 800];

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'Income',
                        data: income,
                        borderColor: this.colors.success,
                        backgroundColor: this.colors.success + '20',
                        fill: false
                    },
                    {
                        label: 'Expenses',
                        data: expenses,
                        borderColor: this.colors.danger,
                        backgroundColor: this.colors.danger + '20',
                        fill: false
                    }
                ]
            },
            options: {
                ...this.defaultConfig,
                plugins: {
                    ...this.defaultConfig.plugins,
                    title: {
                        display: true,
                        text: 'Financial Trend',
                        color: '#fff'
                    }
                },
                scales: {
                    ...this.defaultConfig.scales,
                    y: {
                        ...this.defaultConfig.scales.y,
                        title: {
                            display: true,
                            text: 'Amount ($)',
                            color: '#fff'
                        }
                    }
                }
            }
        });
    },

    // Initialize habit-related charts
    initializeHabitCharts() {
        // Create habit calendar heatmap
        this.createHabitCalendar();
    },

    // Create habit calendar heatmap
    createHabitCalendar() {
        const container = document.getElementById('habitCalendar');
        if (!container) return;

        // Generate calendar for the last 3 months
        const today = new Date();
        const startDate = new Date(today);
        startDate.setMonth(startDate.getMonth() - 3);

        let html = '<div class="habit-calendar-grid">';
        const currentDate = new Date(startDate);

        while (currentDate <= today) {
            const dayClass = Math.random() > 0.7 ? 'completed' : 'missed';
            const dateStr = currentDate.toISOString().split('T')[0];
            
            html += `<div class="habit-day ${dayClass}" 
                          data-date="${dateStr}" 
                          title="${currentDate.toLocaleDateString()}">
                     </div>`;
            
            currentDate.setDate(currentDate.getDate() + 1);
        }

        html += '</div>';
        container.innerHTML = html;
    },

    // Initialize finance charts
    initializeFinanceCharts() {
        // Will be called when finance data is available
    },

    // Initialize goal charts
    initializeGoalCharts() {
        // Will be called when goal data is available
    },

    // Initialize productivity charts
    initializeProductivityChart() {
        // Will be called from dashboard
    },

    // Update chart with new data
    updateChart(chartInstance, newData) {
        if (!chartInstance) return;

        chartInstance.data = newData;
        chartInstance.update();
    },

    // Destroy chart instance
    destroyChart(chartInstance) {
        if (chartInstance) {
            chartInstance.destroy();
        }
    },

    // Export chart as image
    exportChart(chartInstance, filename = 'chart') {
        if (!chartInstance) return;

        const url = chartInstance.toBase64Image();
        const link = document.createElement('a');
        link.download = `${filename}.png`;
        link.href = url;
        link.click();
    }
};

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Set Chart.js defaults for dark theme
    Chart.defaults.color = '#fff';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
    
    Charts.init();
});

// Export for global access
window.Charts = Charts;

// Helper function to create charts from external scripts
window.createHabitChart = Charts.createHabitChart.bind(Charts);
window.createExpenseChart = Charts.createExpenseChart.bind(Charts);
window.createGoalProgressChart = Charts.createGoalProgressChart.bind(Charts);
window.createProductivityChart = Charts.createProductivityChart.bind(Charts);
