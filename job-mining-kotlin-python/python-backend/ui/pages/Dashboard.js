// API Base URL
const API_BASE = 'http://localhost:8000/dashboard';

// Initialisiere Dashboard
async function initDashboard() {
try {
console.log('📊 Lade Dashboard-Daten von API...');

// ✅ ECHTE API-Calls (statt Mock-Daten)
const [stats, trends, levels, roles, emerging] = await Promise.all([
fetch(`${API_BASE}/stats`).then(r => r.json()),
fetch(`${API_BASE}/competence-trends`).then(r => r.json()),
fetch(`${API_BASE}/level-progression`).then(r => r.json()),
fetch(`${API_BASE}/role-distribution`).then(r => r.json()),
fetch(`${API_BASE}/emerging-skills`).then(r => r.json())
]);

// Update Metriken
document.getElementById('total-jobs').textContent = stats.total_jobs.toLocaleString();
document.getElementById('total-skills').textContent = stats.total_skills.toLocaleString();
document.getElementById('digital-skills').textContent = stats.discovery_skills.toLocaleString();
document.getElementById('quality').textContent = `${stats.avg_quality}%`;

// Erstelle Charts
createChart('trendsChart', trends, 'line');
createChart('levelChart', levels, 'bar');
createChart('roleChart', roles, 'doughnut');

// Emerging Skills rendern
renderEmergingSkills(emerging);

console.log('✅ Dashboard erfolgreich geladen');
} catch (error) {
console.error('❌ Fehler beim Laden:', error);
alert('Fehler: Stelle sicher, dass der API-Server läuft (Port 8000)');
}
}

// Chart.js Helper
function createChart(canvasId, data, type) {
const ctx = document.getElementById(canvasId).getContext('2d');

new Chart(ctx, {
    type: type,
    data: data,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'bottom'
            }
        }
    }
});
}

// Emerging Skills Rendering
function renderEmergingSkills(skills) {
const container = document.getElementById('emerging-skills');
container.innerHTML = skills.map((s, i) => `
                                           <div class="skill-item">
<span>${i + 1}. ${s.skill}</span>
<span class="growth">+${s.growth} (${s.growth_pct > 0 ? '+' : ''}${s.growth_pct}%)</span>
</div>
`).join('');
}

// Auto-refresh alle 5 Minuten
setInterval(initDashboard, 5 * 60 * 1000);

// Start beim Laden
document.addEventListener('DOMContentLoaded', initDashboard);
