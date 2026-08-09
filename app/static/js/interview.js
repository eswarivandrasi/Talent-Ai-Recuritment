// Live AI Interview Interface Controller

document.addEventListener('DOMContentLoaded', function () {
    var interviewForm = document.getElementById('interviewForm');
    if (!interviewForm) return;

    var durationMins = parseInt(interviewForm.getAttribute('data-duration') || '15', 10);
    var timerDisplay = document.getElementById('timerDisplay');
    
    // Countdown Timer Logic
    var totalSeconds = Math.max(60, durationMins * 60);
    var submittedAutomatically = false;

    function renderTimer() {
        var mins = Math.floor(totalSeconds / 60);
        var secs = totalSeconds % 60;
        if (timerDisplay) {
            timerDisplay.textContent = (mins < 10 ? "0" : "") + mins + ":" + (secs < 10 ? "0" : "") + secs;
            if (totalSeconds < 180) {
                timerDisplay.className = "fw-bold text-danger animate-pulse";
            }
        }
    }

    renderTimer();

    var timerInterval = setInterval(function () {
        totalSeconds--;
        if (totalSeconds <= 0) {
            clearInterval(timerInterval);
            if (!submittedAutomatically) {
                submittedAutomatically = true;
                alert("Interview time has expired. Your current answers will be submitted automatically.");
                interviewForm.submit();
            }
        } else {
            renderTimer();
        }
    }, 1000);

    // Question Navigation Logic
    var questionCards = document.querySelectorAll('.question-step');
    var navBtns = document.querySelectorAll('.q-nav-btn');
    var prevBtn = document.getElementById('prevQBtn');
    var nextBtn = document.getElementById('nextQBtn');
    var submitBtn = document.getElementById('submitInterviewBtn');
    var currentStep = 0;

    function showStep(index) {
        questionCards.forEach(function (card, i) {
            if (i === index) {
                card.classList.remove('d-none');
            } else {
                card.classList.add('d-none');
            }
        });

        navBtns.forEach(function (btn, i) {
            if (i === index) {
                btn.className = "btn btn-primary btn-sm rounded-circle me-2 q-nav-btn";
            } else {
                btn.className = "btn btn-outline-secondary btn-sm rounded-circle me-2 q-nav-btn";
            }
        });

        if (prevBtn) prevBtn.disabled = (index === 0);
        if (nextBtn) {
            if (index === questionCards.length - 1) {
                nextBtn.classList.add('d-none');
                if (submitBtn) submitBtn.classList.remove('d-none');
            } else {
                nextBtn.classList.remove('d-none');
                if (submitBtn) submitBtn.classList.add('d-none');
            }
        }
        currentStep = index;
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', function () {
            if (currentStep > 0) showStep(currentStep - 1);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function () {
            if (currentStep < questionCards.length - 1) showStep(currentStep + 1);
        });
    }

    navBtns.forEach(function (btn, i) {
        btn.addEventListener('click', function () {
            showStep(i);
        });
    });

    // Initialize first question view
    showStep(0);
});
