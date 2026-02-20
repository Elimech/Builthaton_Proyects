/* ============================================
   EMPLOYEE CLIMATE INTELLIGENCE — DASHBOARD JS
   Real Slack data + Charts + Functional UI
   ============================================ */

// --- Chart.js Global Defaults ---
Chart.defaults.color = '#9aa0a6';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.plugins.legend.display = false;
Chart.defaults.elements.line.tension = 0.4;
Chart.defaults.elements.point.radius = 3;
Chart.defaults.elements.point.hoverRadius = 6;
Chart.defaults.responsive = true;
Chart.defaults.maintainAspectRatio = true;

const COLORS = {
    positive: '#34a853',
    neutral: '#fbbc04',
    negative: '#ea4335',
    anger: '#ef5350',
    joy: '#ffca28',
    love: '#ec407a',
    sadness: '#42a5f5',
    fear: '#ab47bc',
    stress: '#ff7043',
    accent: '#7c4dff',
    gridLine: 'rgba(255, 255, 255, 0.04)',
    tooltipBg: '#1c1e2e',
};

// --- App State ---
let currentChannelId = null;
let currentChannelName = null;
let currentData = null;
let chartInstances = {};

// --- Utility Functions ---
function animateCounter(element, target, suffix = '', duration = 1200) {
    const isFloat = String(target).includes('.');
    let start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const value = start + (target - start) * eased;

        if (isFloat) {
            element.textContent = value.toFixed(1) + suffix;
        } else {
            element.textContent = Math.round(value) + suffix;
        }

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

function simpleMarkdown(text) {
    if (!text) return '';
    let html = text
        .replace(/## (.*)/g, '<h2>$1</h2>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/^\d+\.\s+(.+)/gm, '<li>$1</li>')
        .replace(/^- (.+)/gm, '<li>$1</li>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    html = html.replace(/((<li>.*?<\/li><br>?)+)/g, '<ol>$1</ol>');
    return `<p>${html}</p>`;
}

function showLoading(text = 'Analyzing team data...') {
    const overlay = document.getElementById('loadingOverlay');
    document.getElementById('loadingText').textContent = text;
    overlay.classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

function destroyCharts() {
    Object.values(chartInstances).forEach(chart => {
        if (chart) chart.destroy();
    });
    chartInstances = {};
}

function formatTimestamp(ts) {
    if (!ts) return '';
    try {
        const d = new Date(ts);
        return d.toLocaleDateString('es-CO', {
            weekday: 'short', month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    } catch (e) {
        return ts;
    }
}

function getStressColor(score) {
    if (score >= 0.5) return COLORS.negative;
    if (score > 0) return COLORS.neutral;
    return COLORS.positive;
}

// --- View Management ---
function switchView(viewName) {
    // Hide all views
    document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active-view'));

    // Show target view
    const target = document.getElementById(viewName + 'View');
    if (target) target.classList.add('active-view');

    // Update header buttons
    document.querySelectorAll('.header-btn[id^="btn"]').forEach(b => b.classList.remove('active'));
    const btnMap = {
        'sentiment': 'btnSentimentView',
        'messages': 'btnMessagesView',
        'insights': 'btnInsightsView',
    };
    const btn = document.getElementById(btnMap[viewName]);
    if (btn) btn.classList.add('active');

    // Update sidebar nav items
    document.querySelectorAll('.nav-item[data-view]').forEach(item => {
        item.classList.toggle('active', item.dataset.view === viewName);
    });
}

// --- Channel Loading ---
async function loadChannels() {
    const container = document.getElementById('channelList');
    try {
        const response = await fetch('/api/channels');
        const data = await response.json();

        if (data.error) {
            container.innerHTML = `<div class="channel-error">${data.error}</div>`;
            return;
        }

        container.innerHTML = '';
        data.channels.forEach(ch => {
            const item = document.createElement('a');
            item.href = '#';
            item.className = 'nav-item channel-item';
            item.dataset.channelId = ch.id;
            item.dataset.channelName = ch.name;
            item.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    ${ch.is_private
                    ? '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>'
                    : '<line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/>'
                }
                </svg>
                <span class="channel-name">${ch.name}</span>
                <span class="channel-members">${ch.num_members}</span>
            `;
            item.addEventListener('click', (e) => {
                e.preventDefault();
                selectChannel(ch.id, ch.name);
            });
            container.appendChild(item);
        });
    } catch (e) {
        container.innerHTML = `<div class="channel-error">Failed to load channels: ${e.message}</div>`;
    }
}

// --- Channel Selection & Analysis ---
async function selectChannel(channelId, channelName) {
    currentChannelId = channelId;
    currentChannelName = channelName;

    // Update UI
    document.getElementById('headerTitle').textContent = `# ${channelName}`;

    // Highlight selected channel
    document.querySelectorAll('.channel-item').forEach(item => {
        item.classList.toggle('active', item.dataset.channelId === channelId);
    });

    // Load analysis
    showLoading(`Analyzing #${channelName}...`);
    destroyCharts();

    try {
        const response = await fetch(`/api/channel/${channelId}/analyze`);
        const data = await response.json();

        if (data.error) {
            hideLoading();
            alert(`Error: ${data.error}`);
            return;
        }

        currentData = data;
        renderDashboard(data);
        switchView('sentiment');
        hideLoading();
    } catch (e) {
        hideLoading();
        alert(`Failed to analyze channel: ${e.message}`);
    }
}

// --- Render Dashboard ---
function renderDashboard(data) {
    // KPI Counters
    animateCounter(
        document.querySelector('#kpiTotalMessages .kpi-value'),
        data.total_messages || 0
    );
    animateCounter(
        document.querySelector('#kpiUniqueUsers .kpi-value'),
        data.unique_users || 0
    );
    animateCounter(
        document.querySelector('#kpiBurnout .kpi-value'),
        data.burnout_score || 0
    );
    animateCounter(
        document.querySelector('#kpiStress .kpi-value'),
        (data.stress_ratio || 0) * 100,
        '%'
    );

    // Badges
    const total = data.total_messages || 0;
    document.getElementById('sentimentBadge').textContent = `${total.toLocaleString()} Results`;
    document.getElementById('stressBadge').textContent = `${total.toLocaleString()} Results`;

    // Charts
    if (data.sentiment_share) {
        buildSentimentDonut('sentimentDonut', data.sentiment_share);
    }
    if (data.sentiment_over_time) {
        buildSentimentOverTime('sentimentLine', data.sentiment_over_time);
    }
    if (data.emotion_counts) {
        buildEmotionBar('emotionBar', data.emotion_counts);
    }
    if (data.weekly_stress) {
        buildStressTrend('stressLine', data.weekly_stress);
    }

    // Comments
    populateComments(data.similar_comments || []);

    // Messages
    populateMessages(data.messages || []);

    // Insights
    populateInsights(data.gemini_analysis || null);
}

// --- Chart Builders ---
function buildSentimentDonut(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    const total = data.positive + data.neutral + data.negative;

    // Reset canvas for re-render
    canvas.width = canvas.width;

    chartInstances.sentimentDonut = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [data.positive, data.neutral, data.negative],
                backgroundColor: [COLORS.positive, COLORS.neutral, COLORS.negative],
                borderColor: 'transparent',
                borderWidth: 0,
                hoverOffset: 8,
                cutout: '68%',
            }]
        },
        options: {
            plugins: {
                tooltip: {
                    backgroundColor: COLORS.tooltipBg,
                    titleFont: { weight: '600' },
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function (ctx) {
                            const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : 0;
                            return ` ${ctx.label}: ${ctx.parsed} (${pct}%)`;
                        }
                    }
                }
            },
            animation: { animateRotate: true, duration: 1200 }
        }
    });

    // Build legend
    const legend = document.getElementById('sentimentLegend');
    const items = [
        { label: 'Positive', color: COLORS.positive, value: data.positive_pct || (total > 0 ? ((data.positive / total) * 100).toFixed(1) : 0) },
        { label: 'Neutral', color: COLORS.neutral, value: data.neutral_pct || (total > 0 ? ((data.neutral / total) * 100).toFixed(1) : 0) },
        { label: 'Negative', color: COLORS.negative, value: data.negative_pct || (total > 0 ? ((data.negative / total) * 100).toFixed(1) : 0) },
    ];
    legend.innerHTML = items.map(item => `
        <div class="legend-item">
            <span class="legend-dot" style="background: ${item.color}"></span>
            <span>${item.label}</span>
            <strong style="margin-left: auto; color: ${item.color}">${item.value}%</strong>
        </div>
    `).join('');
}

function buildSentimentOverTime(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    chartInstances.sentimentLine = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Positive',
                    data: data.positive,
                    borderColor: COLORS.positive,
                    backgroundColor: COLORS.positive + '18',
                    fill: true,
                    pointBackgroundColor: COLORS.positive,
                },
                {
                    label: 'Neutral',
                    data: data.neutral,
                    borderColor: COLORS.neutral,
                    backgroundColor: 'transparent',
                    pointBackgroundColor: COLORS.neutral,
                },
                {
                    label: 'Negative',
                    data: data.negative,
                    borderColor: COLORS.negative,
                    backgroundColor: 'transparent',
                    pointBackgroundColor: COLORS.negative,
                },
            ]
        },
        options: {
            plugins: {
                legend: {
                    display: true, position: 'bottom',
                    labels: { usePointStyle: true, pointStyle: 'circle', padding: 20, font: { size: 10 } }
                },
                tooltip: {
                    backgroundColor: COLORS.tooltipBg, padding: 12, cornerRadius: 8,
                    mode: 'index', intersect: false,
                }
            },
            scales: {
                x: { grid: { color: COLORS.gridLine }, border: { display: false } },
                y: { grid: { color: COLORS.gridLine }, border: { display: false }, beginAtZero: true }
            }
        }
    });
}

function buildEmotionBar(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const labels = Object.keys(data);
    const values = Object.values(data);
    const colors = [COLORS.anger, COLORS.joy, COLORS.love, COLORS.sadness, COLORS.fear, COLORS.stress];
    const total = values.reduce((a, b) => a + b, 0);

    chartInstances.emotionBar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: 'transparent',
                borderRadius: 4,
                barThickness: 22,
            }]
        },
        options: {
            indexAxis: 'y',
            plugins: {
                tooltip: {
                    backgroundColor: COLORS.tooltipBg, padding: 12, cornerRadius: 8,
                    callbacks: { label: (ctx) => ` ${ctx.parsed.x} messages` }
                }
            },
            scales: {
                x: { grid: { color: COLORS.gridLine }, border: { display: false }, beginAtZero: true },
                y: { grid: { display: false }, border: { display: false } }
            }
        }
    });

    document.getElementById('emotionBadge').textContent = `${total.toLocaleString()} Results`;
}

function buildStressTrend(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    const gradient = ctx.createLinearGradient(0, 0, 0, 250);
    gradient.addColorStop(0, COLORS.stress + '40');
    gradient.addColorStop(1, COLORS.stress + '00');

    chartInstances.stressTrend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Stress Level',
                data: data.values,
                borderColor: COLORS.stress,
                backgroundColor: gradient,
                fill: true,
                borderWidth: 2.5,
                pointBackgroundColor: COLORS.stress,
                pointBorderColor: '#1c1e2e',
                pointBorderWidth: 2,
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: true, position: 'bottom',
                    labels: { usePointStyle: true, pointStyle: 'circle', padding: 20, font: { size: 10 } }
                },
                tooltip: {
                    backgroundColor: COLORS.tooltipBg, padding: 12, cornerRadius: 8,
                    callbacks: { label: (ctx) => ` Stress: ${(ctx.parsed.y * 100).toFixed(0)}%` }
                }
            },
            scales: {
                x: { grid: { color: COLORS.gridLine }, border: { display: false } },
                y: {
                    grid: { color: COLORS.gridLine }, border: { display: false },
                    beginAtZero: true, max: 1,
                    ticks: { callback: (v) => (v * 100) + '%' }
                }
            }
        }
    });
}

// --- Populate Comments ---
function populateComments(comments) {
    const list = document.getElementById('similarComments');
    if (!comments.length) {
        list.innerHTML = '<li class="comment-item" style="border-left-color: var(--color-positive);">No high-stress comments found ✓</li>';
        return;
    }
    list.innerHTML = '';
    comments.forEach((comment, idx) => {
        const li = document.createElement('li');
        li.className = 'comment-item fade-in';
        li.style.animationDelay = `${idx * 0.1}s`;
        li.innerHTML = `<span class="comment-index">${idx + 1}</span>${comment}`;
        list.appendChild(li);
    });
}

// --- Populate Messages ---
function populateMessages(messages) {
    const container = document.getElementById('messagesList');
    const countEl = document.getElementById('messagesCount');

    countEl.textContent = `${messages.length} messages`;

    if (!messages.length) {
        container.innerHTML = `
            <div class="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.3">
                    <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
                </svg>
                <p>No messages found in this channel</p>
            </div>`;
        return;
    }

    container.innerHTML = '';
    messages.forEach((msg, idx) => {
        const div = document.createElement('div');
        div.className = 'message-card fade-in';
        div.style.animationDelay = `${Math.min(idx * 0.03, 1)}s`;

        const stressColor = getStressColor(msg.stress_score);
        const stressLabel = msg.stress_score >= 0.5 ? 'High' : msg.stress_score > 0 ? 'Med' : 'Low';
        const reactions = msg.reactions.length
            ? `<div class="msg-reactions">${msg.reactions.map(r => `<span class="reaction">:${r}:</span>`).join('')}</div>`
            : '';

        div.innerHTML = `
            <div class="msg-header">
                <div class="msg-user">
                    <div class="msg-avatar">${msg.user.charAt(0).toUpperCase()}</div>
                    <strong>${msg.user}</strong>
                    ${msg.is_thread ? '<span class="msg-thread-badge">thread</span>' : ''}
                </div>
                <div class="msg-meta">
                    <span class="msg-stress" style="color: ${stressColor}; border-color: ${stressColor}30; background: ${stressColor}12;">
                        ${stressLabel} ${(msg.stress_score * 100).toFixed(0)}%
                    </span>
                    <span class="msg-time">${formatTimestamp(msg.timestamp)}</span>
                </div>
            </div>
            <p class="msg-text">${msg.text}</p>
            ${reactions}
        `;
        container.appendChild(div);
    });
}

// --- Populate Insights ---
function populateInsights(text) {
    const container = document.getElementById('geminiInsights');
    if (!text) {
        container.innerHTML = `
            <div class="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.3">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
                <p>AI analysis unavailable. Ensure GEMINI_API_KEY is set.</p>
            </div>`;
        return;
    }
    container.innerHTML = simpleMarkdown(text);
}

// --- Sidebar Toggle ---
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebarToggle');

    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });
}

// --- Button Wiring ---
function initButtons() {
    // View buttons in header
    document.getElementById('btnSentimentView').addEventListener('click', () => switchView('sentiment'));
    document.getElementById('btnMessagesView').addEventListener('click', () => switchView('messages'));
    document.getElementById('btnInsightsView').addEventListener('click', () => switchView('insights'));

    // Sidebar view items
    document.querySelectorAll('.nav-item[data-view]').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            switchView(item.dataset.view);
        });
    });

    // Refresh button
    document.getElementById('btnRefresh').addEventListener('click', () => {
        if (currentChannelId) {
            selectChannel(currentChannelId, currentChannelName);
        } else {
            loadChannels();
        }
    });

    // Back button
    document.getElementById('btnBack').addEventListener('click', () => {
        currentChannelId = null;
        currentChannelName = null;
        currentData = null;
        document.getElementById('headerTitle').textContent = 'Select a Channel';

        // Deselect channels
        document.querySelectorAll('.channel-item').forEach(item => item.classList.remove('active'));

        // Reset KPIs
        document.querySelectorAll('.kpi-value').forEach(el => el.textContent = '—');

        // Clear charts
        destroyCharts();
        ['sentimentLegend', 'similarComments'].forEach(id => {
            document.getElementById(id).innerHTML = '';
        });

        switchView('sentiment');
    });
}

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initButtons();
    loadChannels();
});
