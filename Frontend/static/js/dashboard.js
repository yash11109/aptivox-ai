/* ==========================================================================
   TALENTFORGE AI - DASHBOARD & CANDIDATE ANALYTICS ENGINE
   ========================================================================== */

let radarChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    bindDashboardEvents();
});

function bindDashboardEvents() {
    const clearBtn = document.getElementById('clear-history-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', handleClearHistory);
    }
}

async function loadDashboardData() {
    try {
        const res = await fetch('/api/dashboard/stats');
        const data = await res.json();
        if (data.success) {
            renderSummaryCards(data.stats);
            renderRadarChart(data.stats.skill_matrix);
            renderHistoryTable(data.stats.history);
        }
    } catch (err) {
        console.error('Error loading dashboard stats:', err);
    }
}

function renderSummaryCards(stats) {
    const avgScoreEl = document.getElementById('stat-avg-score');
    if (avgScoreEl) avgScoreEl.innerText = `${stats.average_score} / 10`;

    const countEl = document.getElementById('stat-completed-count');
    if (countEl) countEl.innerText = stats.completed_count;

    const questionsEl = document.getElementById('stat-questions-count');
    if (questionsEl) questionsEl.innerText = stats.total_questions_count !== undefined ? `${stats.total_questions_count}` : '0';

    const streakEl = document.getElementById('stat-streak');
    if (streakEl) streakEl.innerText = `${stats.prep_streak_days} Days`;
}

function renderRadarChart(skills) {
    const ctx = document.getElementById('skillRadarChart');
    if (!ctx) return;

    const labels = Object.keys(skills);
    const dataValues = Object.values(skills);

    if (radarChartInstance) {
        radarChartInstance.destroy();
    }

    radarChartInstance = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Competency Level (%)',
                data: dataValues,
                backgroundColor: 'rgba(99, 102, 241, 0.25)',
                borderColor: '#6366f1',
                pointBackgroundColor: '#06b6d4',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#6366f1'
            }]
        },
        options: {
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                    grid: { color: 'rgba(255, 255, 255, 0.08)' },
                    pointLabels: { color: '#94a3b8', font: { size: 12, weight: '600' } },
                    ticks: { display: false, max: 100 }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function renderHistoryTable(history) {
    const tbody = document.getElementById('history-table-body');
    if (!tbody) return;

    if (!history || history.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align:center; padding:36px; color:var(--text-muted);">
                    <div style="font-size:1.5rem; margin-bottom:8px;">🌱</div>
                    <strong>No interview sessions recorded yet.</strong>
                    <p style="font-size:0.85rem; margin-top:4px; color:var(--text-dim);">You are starting fresh! Launch your first mock interview to track real-time analytics.</p>
                    <a href="/interview" class="btn btn-primary" style="margin-top:12px; font-size:0.85rem; padding:8px 18px;">🎙️ Start First Interview</a>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = history.map(item => `
        <tr id="row-${item.id}">
            <td><strong>${item.role}</strong></td>
            <td><span class="badge" style="background:rgba(99,102,241,0.15); color:#a5b4fc; padding:4px 10px; border-radius:6px; font-size:0.8rem;">${item.topic}</span></td>
            <td>${item.date}</td>
            <td><strong style="color:var(--success);">${item.score} / 10</strong></td>
            <td>${item.duration}</td>
            <td style="display:flex; gap:8px;">
                <a href="/interview" class="btn btn-secondary" style="padding:4px 10px; font-size:0.8rem;">Retake</a>
                <button onclick="handleDeleteSingleSession('${item.id}')" class="btn btn-secondary" style="padding:4px 8px; font-size:0.8rem; border-color:rgba(239,68,68,0.3); color:#fca5a5;" title="Delete this session">🗑️</button>
            </td>
        </tr>
    `).join('');
}

async function handleClearHistory() {
    const confirmClear = window.confirm("Are you sure you want to delete all previous interview history and start completely fresh? This cannot be undone.");
    if (!confirmClear) return;

    try {
        const res = await fetch('/api/dashboard/history/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await res.json();
        if (data.success) {
            if (typeof showToast === 'function') {
                showToast("All previous interview history deleted. Starting completely fresh!", "success");
            } else {
                alert("History cleared successfully!");
            }
            loadDashboardData();
        }
    } catch (err) {
        console.error("Error clearing history:", err);
        if (typeof showToast === 'function') {
            showToast("Failed to clear history.", "error");
        }
    }
}

async function handleDeleteSingleSession(sessionId) {
    if (!window.confirm("Delete this interview record?")) return;

    try {
        const res = await fetch(`/api/dashboard/history/${sessionId}`, {
            method: 'DELETE'
        });
        const data = await res.json();
        if (data.success) {
            if (typeof showToast === 'function') {
                showToast("Session record removed.", "info");
            }
            loadDashboardData();
        }
    } catch (err) {
        console.error("Error deleting session:", err);
    }
}
