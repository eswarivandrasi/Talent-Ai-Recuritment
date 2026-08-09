// AI Recruitment System Main UI JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Auto-dismiss alert banners after 5 seconds
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // File Upload Feedback
    var fileInput = document.getElementById('resume_pdf');
    var fileLabel = document.getElementById('file_name_display');
    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', function (e) {
            if (e.target.files.length > 0) {
                fileLabel.textContent = "Selected: " + e.target.files[0].name;
                fileLabel.classList.remove('d-none');
            }
        });
    }

    // Recruiter Job Form Dynamic Weight Validation
    var weightResume = document.getElementById('weight_resume');
    var weightInterview = document.getElementById('weight_interview');
    var weightSkill = document.getElementById('weight_skill');
    var weightExp = document.getElementById('weight_exp');
    var totalWeightDisplay = document.getElementById('total_weight_display');

    function updateTotalWeight() {
        if (weightResume && weightInterview && weightSkill && weightExp && totalWeightDisplay) {
            var total = (parseFloat(weightResume.value) || 0) +
                        (parseFloat(weightInterview.value) || 0) +
                        (parseFloat(weightSkill.value) || 0) +
                        (parseFloat(weightExp.value) || 0);
            
            totalWeightDisplay.textContent = total + "%";
            if (Math.abs(total - 100) < 0.1) {
                totalWeightDisplay.className = "fw-bold text-success";
            } else {
                totalWeightDisplay.className = "fw-bold text-danger";
            }
        }
    }

    [weightResume, weightInterview, weightSkill, weightExp].forEach(function (input) {
        if (input) {
            input.addEventListener('input', updateTotalWeight);
        }
    });
    updateTotalWeight();
});
