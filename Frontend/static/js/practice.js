/* ==========================================================================
   AI INTERVIEW PREPARATION PORTAL - PRACTICE HUB ENGINE
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    loadPracticeQuestions();
    bindPracticeEvents();
});

function bindPracticeEvents() {
    const filterCat = document.getElementById('filter-category');
    const filterDom = document.getElementById('filter-domain');

    if (filterCat) filterCat.addEventListener('change', loadPracticeQuestions);
    if (filterDom) filterDom.addEventListener('change', loadPracticeQuestions);
}

async function loadPracticeQuestions() {
    const cat = document.getElementById('filter-category')?.value || 'All';
    const dom = document.getElementById('filter-domain')?.value || 'All';

    try {
        const res = await fetch(`/api/practice/questions?category=${encodeURIComponent(cat)}&domain=${encodeURIComponent(dom)}`);
        const data = await res.json();
        if (data.success) {
            renderQuestionCards(data.questions);
        }
    } catch (err) {
        console.error('Error fetching practice questions:', err);
    }
}

function renderQuestionCards(questions) {
    const container = document.getElementById('questions-list-container');
    if (!container) return;

    if (!questions || questions.length === 0) {
        container.innerHTML = '<div style="text-align:center; padding:40px; color:var(--text-muted);">No questions found for the selected filters.</div>';
        return;
    }

    container.innerHTML = questions.map((q, idx) => `
        <div class="card" style="margin-bottom:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="display:flex; gap:8px;">
                    <span style="background:rgba(99,102,241,0.15); color:#a5b4fc; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:600;">${q.category}</span>
                    <span style="background:rgba(6,182,212,0.15); color:#67e8f9; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:600;">${q.domain}</span>
                </div>
                <span style="color:var(--text-dim); font-size:0.85rem;">Level: ${q.difficulty}</span>
            </div>
            
            <h3 style="font-size:1.15rem; margin-bottom:12px;">${q.question}</h3>

            <div id="star-box-${idx}" style="display:none; background:rgba(15,23,42,0.8); border:1px solid var(--border-light); padding:16px; border-radius:var(--radius-md); margin:16px 0; font-size:0.9rem; color:var(--text-muted);">
                <strong style="color:var(--secondary); display:block; margin-bottom:6px;">⭐ STAR Guide & Ideal Structure:</strong>
                ${q.star_guide}
                <hr style="border:none; border-top:1px solid var(--border-light); margin:12px 0;">
                <strong style="color:var(--success); display:block; margin-bottom:6px;">💡 Sample Key Answer:</strong>
                ${q.sample_answer}
            </div>

            <div style="display:flex; gap:12px; margin-top:12px;">
                <button onclick="toggleStarGuide('${idx}')" class="btn btn-secondary" style="padding:8px 16px; font-size:0.85rem;">
                    💡 View STAR Guide & Solution
                </button>
                <a href="/interview" class="btn btn-primary" style="padding:8px 16px; font-size:0.85rem;">
                    🎙️ Practice in Mock Room
                </a>
            </div>
        </div>
    `).join('');
}

function toggleStarGuide(idx) {
    const box = document.getElementById(`star-box-${idx}`);
    if (box) {
        box.style.display = (box.style.display === 'none' || !box.style.display) ? 'block' : 'none';
    }
}
