// Chart.js Visualization Initializers for Recruiter Analytics

function initRecruiterCharts(jobTitles, appsPerJob, scoreBins, statusCounts) {
    if (typeof Chart === 'undefined') return;

    // 1. Applications Per Job Bar Chart
    var ctxJobs = document.getElementById('chartAppsPerJob');
    if (ctxJobs) {
        new Chart(ctxJobs, {
            type: 'bar',
            data: {
                labels: jobTitles,
                datasets: [{
                    label: 'Applications Received',
                    data: appsPerJob,
                    backgroundColor: 'rgba(79, 70, 229, 0.8)',
                    borderColor: '#4f46e5',
                    borderWidth: 1,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { precision: 0 } }
                }
            }
        });
    }

    // 2. Score Distribution Histogram
    var ctxScores = document.getElementById('chartScoreDistribution');
    if (ctxScores) {
        new Chart(ctxScores, {
            type: 'line',
            data: {
                labels: Object.keys(scoreBins),
                datasets: [{
                    label: 'Candidates Count',
                    data: Object.values(scoreBins),
                    fill: true,
                    backgroundColor: 'rgba(6, 182, 212, 0.15)',
                    borderColor: '#06b6d4',
                    borderWidth: 3,
                    tension: 0.4,
                    pointBackgroundColor: '#06b6d4'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { precision: 0 } }
                }
            }
        });
    }

    // 3. Status Breakdown Doughnut Chart
    var ctxStatus = document.getElementById('chartStatusBreakdown');
    if (ctxStatus) {
        new Chart(ctxStatus, {
            type: 'doughnut',
            data: {
                labels: Object.keys(statusCounts),
                datasets: [{
                    data: Object.values(statusCounts),
                    backgroundColor: [
                        '#64748b', // Applied
                        '#3b82f6', // Interviewed
                        '#10b981', // Shortlisted
                        '#ef4444' // Rejected
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
}
