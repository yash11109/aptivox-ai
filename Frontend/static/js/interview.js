/* ==========================================================================
   AI INTERVIEW PREPARATION PORTAL - INTERVIEW SESSION ENGINE
   ========================================================================== */

let currentSession = null;
let currentQuestionIndex = 0;
let sessionScores = [];
let isRecording = false;
let recognition = null;
let questionTimer = null;
let secondsElapsed = 0;

document.addEventListener('DOMContentLoaded', () => {
    initSpeechRecognition();
    bindInterviewEvents();
});

// Initialize Speech Recognition if supported
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            const textarea = document.getElementById('user-answer-input');
            if (textarea) {
                textarea.value = transcript;
            }
        };

        recognition.onerror = (e) => {
            console.error('Speech recognition error:', e.error);
            stopVoiceRecording();
        };

        recognition.onend = () => {
            if (isRecording) stopVoiceRecording();
        };
    }
}

function bindInterviewEvents() {
    const startForm = document.getElementById('start-interview-form');
    if (startForm) {
        startForm.addEventListener('submit', handleStartInterview);
    }

    const micBtn = document.getElementById('mic-toggle-btn');
    if (micBtn) {
        micBtn.addEventListener('click', toggleVoiceRecording);
    }

    const submitBtn = document.getElementById('submit-answer-btn');
    if (submitBtn) {
        submitBtn.addEventListener('click', handleAnswerSubmission);
    }

    const nextBtn = document.getElementById('next-question-btn');
    if (nextBtn) {
        nextBtn.addEventListener('click', handleNextQuestion);
    }

    const backBtn = document.getElementById('modal-back-btn');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            document.getElementById('feedback-modal').classList.remove('active');
        });
    }

    const closeXBtn = document.getElementById('modal-close-x');
    if (closeXBtn) {
        closeXBtn.addEventListener('click', () => {
            document.getElementById('feedback-modal').classList.remove('active');
        });
    }

}

async function handleStartInterview(e) {
    e.preventDefault();
    const role = document.getElementById('select-role').value;
    const category = document.getElementById('select-category').value;
    const difficulty = document.getElementById('select-difficulty').value;
    const questionsCount = document.getElementById('select-count').value;

    try {
        showToast('Entering interview room...', 'info');
        const res = await fetch('/api/interview/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role, category, difficulty, questions_count: questionsCount })
        });
        const data = await res.json();
        if (data.success) {
            currentSession = data;
            currentQuestionIndex = 0;
            sessionScores = [];
            secondsElapsed = 0;

            document.getElementById('setup-card').style.display = 'none';
            document.getElementById('active-interview-area').style.display = 'block';

            startTimer();
            loadQuestion(0);
            showToast('Interview session active. Good luck!', 'success');
        }
    } catch (err) {
        showToast('Failed to start interview session.', 'error');
    }
}

function loadQuestion(index) {
    if (!currentSession || !currentSession.questions[index]) return;

    const q = currentSession.questions[index];
    document.getElementById('current-q-num').innerText = index + 1;
    document.getElementById('total-q-num').innerText = currentSession.questions.length;
    document.getElementById('question-text-display').innerText = q.question;
    document.getElementById('user-answer-input').value = '';
    document.getElementById('question-hint-box').innerText = `💡 Focus Tip: ${q.hint || 'Structure your response clearly.'}`;

    // Update Progress Bar
    const percent = ((index + 1) / currentSession.questions.length) * 100;
    document.getElementById('progress-bar-fill').style.width = `${percent}%`;
}

function toggleVoiceRecording() {
    if (!recognition) {
        showToast('Speech recognition not supported in this browser. Please type your answer.', 'error');
        return;
    }

    const micBtn = document.getElementById('mic-toggle-btn');
    const recIndicator = document.getElementById('recording-indicator');

    if (!isRecording) {
        recognition.start();
        isRecording = true;
        micBtn.classList.add('btn-danger');
        micBtn.innerHTML = '🛑 Stop Recording';
        if (recIndicator) recIndicator.style.display = 'inline-flex';
        showToast('Listening to your voice answer...', 'info');
    } else {
        stopVoiceRecording();
    }
}

function stopVoiceRecording() {
    if (recognition && isRecording) {
        recognition.stop();
        isRecording = false;
        const micBtn = document.getElementById('mic-toggle-btn');
        const recIndicator = document.getElementById('recording-indicator');
        if (micBtn) {
            micBtn.classList.remove('btn-danger');
            micBtn.innerHTML = '🎙️ Speak Answer';
        }
        if (recIndicator) recIndicator.style.display = 'none';
    }
}

async function handleAnswerSubmission() {
    stopVoiceRecording();
    const answer = document.getElementById('user-answer-input').value.trim();
    if (!answer) {
        showToast('Please type or record an answer before submitting.', 'error');
        return;
    }

    const submitBtn = document.getElementById('submit-answer-btn');
    submitBtn.disabled = true;
    submitBtn.innerText = 'Evaluating AI Feedback...';

    const currentQ = currentSession.questions[currentQuestionIndex];

    try {
        const res = await fetch('/api/interview/evaluate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: currentQ.question,
                user_answer: answer,
                category: currentSession.category,
                difficulty: currentSession.difficulty
            })
        });
        const data = await res.json();
        if (data.success) {
            sessionScores.push(data.score);

            // Display Feedback Modal
            const scoreValEl = document.getElementById('modal-score-val');
            if (data.score === 0 || data.is_wrong) {
                scoreValEl.className = 'score-badge-circle score-fail';
                scoreValEl.innerHTML = `
                    <span style="font-size:2.3rem; font-weight:800; line-height:1; color:#ffffff; text-shadow:0 2px 10px rgba(0,0,0,0.4);">0</span>
                    <span style="font-size:0.85rem; font-weight:700; color:#fecaca; margin-top:3px; letter-spacing:0.5px;">/ 10</span>
                `;
            } else {
                scoreValEl.className = 'score-badge-circle';
                scoreValEl.innerHTML = `
                    <span style="font-size:2.3rem; font-weight:800; line-height:1; color:#ffffff; text-shadow:0 2px 10px rgba(0,0,0,0.3);">${data.score}</span>
                    <span style="font-size:0.85rem; font-weight:700; color:#e0f2fe; margin-top:3px; letter-spacing:0.5px;">/ 10</span>
                `;
            }
            document.getElementById('modal-status-tag').innerText = data.status;

            const wrongBanner = document.getElementById('modal-wrong-banner');
            const correctionBox = document.getElementById('modal-correction-container');
            const wrongRationale = document.getElementById('modal-wrong-rationale');
            const correctionText = document.getElementById('modal-correction-text');

            if (data.is_wrong || data.score === 0 || data.status.includes("wrong")) {
                document.getElementById('modal-status-tag').style.color = '#ef4444';
                if (wrongBanner) {
                    wrongBanner.style.display = 'block';
                    if (wrongRationale) wrongRationale.innerText = data.error_rationale || "Your answer is incorrect. 0 out of 10 points awarded.";
                }
                if (correctionBox) {
                    correctionBox.style.display = 'block';
                    if (correctionText) correctionText.innerText = data.correction || data.sample_ideal;
                }
            } else {
                document.getElementById('modal-status-tag').style.color = '#38bdf8';
                if (wrongBanner) wrongBanner.style.display = 'none';
                if (correctionBox) {
                    if (data.correction) {
                        correctionBox.style.display = 'block';
                        if (correctionText) correctionText.innerText = data.correction;
                    } else {
                        correctionBox.style.display = 'none';
                    }
                }
            }

            const strengthsList = document.getElementById('modal-strengths-list');
            strengthsList.innerHTML = data.strengths.map(s => `<li style="color:#ffffff; margin-bottom:8px; font-weight:500;"><span style="color:#4ade80; font-weight:bold; margin-right:6px;">✔</span> ${s}</li>`).join('');

            const gapsList = document.getElementById('modal-gaps-list');
            gapsList.innerHTML = data.gaps.map(g => `<li style="color:#ffffff; margin-bottom:8px; font-weight:500;"><span style="color:#fbbf24; font-weight:bold; margin-right:6px;">•</span> ${g}</li>`).join('');

            document.getElementById('modal-sample-answer').innerText = data.sample_ideal;
            document.getElementById('modal-followup').innerText = data.follow_up;

            document.getElementById('feedback-modal').classList.add('active');
        }
    } catch (err) {
        showToast('Error generating AI evaluation.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = '⚡ Submit & Analyze Answer';
    }
}

function handleNextQuestion() {
    document.getElementById('feedback-modal').classList.remove('active');
    currentQuestionIndex++;

    if (currentQuestionIndex < currentSession.questions.length) {
        loadQuestion(currentQuestionIndex);
    } else {
        finishSession();
    }
}

async function finishSession() {
    clearInterval(questionTimer);
    const avgScore = (sessionScores.reduce((a, b) => a + b, 0) / sessionScores.length).toFixed(1);

    try {
        await fetch('/api/interview/finish', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                role: currentSession.role,
                category: currentSession.category,
                difficulty: currentSession.difficulty,
                average_score: avgScore,
                duration_seconds: secondsElapsed,
                questions_count: currentSession.questions.length,
                summary_feedback: `Completed ${currentSession.questions.length} questions with an average score of ${avgScore}/10.`
            })
        });
    } catch (err) {
        console.error('Failed to persist session summary:', err);
    }

    document.getElementById('active-interview-area').style.display = 'none';
    document.getElementById('completed-summary-card').style.display = 'block';
    document.getElementById('final-score-display').innerText = `${avgScore} / 10`;
    showToast('Interview session completed & saved to Database!', 'success');
}

function startTimer() {
    clearInterval(questionTimer);
    questionTimer = setInterval(() => {
        secondsElapsed++;
        const mins = String(Math.floor(secondsElapsed / 60)).padStart(2, '0');
        const secs = String(secondsElapsed % 60).padStart(2, '0');
        const timerEl = document.getElementById('interview-timer');
        if (timerEl) timerEl.innerText = `${mins}:${secs}`;
    }, 1000);
}
