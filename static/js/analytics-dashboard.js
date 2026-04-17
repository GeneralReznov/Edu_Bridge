async function loadAnalytics() {
  try {
    const res = await fetch('/api/analytics/data');
    const json = await res.json();
    if (!json.success) throw new Error('Failed to load analytics');

    document.getElementById('adLoading').style.display = 'none';
    document.getElementById('adContent').style.display = 'block';

    const s = json.stats;
    renderKPIs(s);
    renderLevelCard(s);
    renderJourneyBanner(json.stage);
    renderNudge(json.nudge);
    renderToolList(json.tools);
    renderWeeklyChart(json.weekly_xp_data);
    renderEngagement(s.engagement_score);
    renderBadges(json.badges);
    renderRecommendations(json.recommendations);
  } catch (e) {
    document.getElementById('adLoading').innerHTML = `<p style="color:#dc2626;">⚠️ Could not load analytics: ${e.message}</p>`;
  }
}

function renderKPIs(s) {
  const kpis = [
    { icon: 'fas fa-bolt', bg: '#fef9c3', color: '#d97706', val: s.xp, label: 'Total XP', sub: `Level ${s.level}` },
    { icon: 'fas fa-layer-group', bg: '#f0f0ff', color: '#4f46e5', val: `${s.tools_completed}/${s.total_tools}`, label: 'Tools Used', sub: `${s.completion_pct}% complete` },
    { icon: 'fas fa-fire', bg: '#fff1f2', color: '#dc2626', val: s.streak, label: 'Day Streak', sub: 'Consecutive days' },
    { icon: 'fas fa-medal', bg: '#fffbeb', color: '#d97706', val: s.badges_count, label: 'Badges Earned', sub: 'Achievements' },
    { icon: 'fas fa-calendar-week', bg: '#f0fdf4', color: '#16a34a', val: s.weekly_xp, label: 'Weekly XP', sub: 'This week' },
    { icon: 'fas fa-chart-bar', bg: '#f0f9ff', color: '#0891b2', val: `${s.engagement_score}%`, label: 'Engagement', sub: 'Platform score' },
  ];
  document.getElementById('kpiGrid').innerHTML = kpis.map((k, i) => `
    <div class="kpi-card" style="border-bottom-color:${k.color};">
      <div class="kpi-icon" style="background:${k.bg};color:${k.color};"><i class="${k.icon}"></i></div>
      <div class="kpi-val">${k.val}</div>
      <div class="kpi-label">${k.label}</div>
      <div class="kpi-sub">${k.sub}</div>
    </div>`).join('');
}

function renderLevelCard(s) {
  document.getElementById('levelCard').innerHTML = `
    <div class="level-header">
      <div>
        <div style="font-size:.85rem;color:#64748b;font-weight:600;">Current Level</div>
        <div style="font-size:1.5rem;font-weight:800;color:#1e293b;">Level ${s.level}</div>
      </div>
      <span class="level-badge">⚡ ${s.xp} XP Total</span>
    </div>
    <div class="level-bar-bg">
      <div class="level-bar-fill" style="width:${s.level_progress_pct}%;"></div>
    </div>
    <div class="level-meta">
      <span>${s.xp} XP earned</span>
      <span>${s.xp_remaining} XP to Level ${s.level + 1}</span>
    </div>`;
}

function renderJourneyBanner(stage) {
  document.getElementById('journeyBanner').innerHTML = `
    <div class="journey-icon">${stage.icon}</div>
    <div class="journey-info" style="flex:1;">
      <h3>${stage.name}</h3>
      <p>Next: ${stage.next}</p>
      <div class="journey-prog-bg">
        <div class="journey-prog-fill" style="width:${stage.pct}%;"></div>
      </div>
    </div>
    <div style="font-size:1.2rem;font-weight:800;color:#16a34a;">${stage.pct}%</div>`;
}

function renderNudge(nudge) {
  if (!nudge) return;
  const card = document.getElementById('nudgeCard');
  card.style.display = 'flex';
  document.getElementById('nudgeText').textContent = nudge.message;
}

function renderToolList(tools) {
  const COLORS = {
    'career_navigator': '#4f46e5', 'roi_calculator': '#16a34a',
    'admission_predictor': '#7c3aed', 'timeline_generator': '#f97316',
    'loan_planner': '#0891b2', 'chatbot': '#ec4899',
    'application_strategy': '#dc2626', 'university_comparison': '#d97706',
    'peer_benchmarks': '#0f766e',
  };
  document.getElementById('toolList').innerHTML = tools.map(t => `
    <div class="tool-row">
      <div class="t-icon" style="background:${COLORS[t.id]||'#64748b'};"><i class="${t.icon}"></i></div>
      <div class="t-name">${t.name}</div>
      <div class="t-xp">${t.xp} XP</div>
      <div class="t-done ${t.done ? 'yes' : 'no'}">
        ${t.done ? '<i class="fas fa-check"></i>' : '<i class="fas fa-circle"></i>'}
      </div>
    </div>`).join('');
}

function renderWeeklyChart(data) {
  const maxXP = Math.max(...data.map(d => d.xp), 1);
  document.getElementById('weeklyChart').innerHTML = data.map(d => `
    <div class="wc-bar-wrap">
      <div class="wc-val">${d.xp > 0 ? d.xp : ''}</div>
      <div class="wc-bar" style="height:${Math.max(4, d.xp / maxXP * 80)}px;width:100%;"></div>
      <div class="wc-label">${d.day}</div>
    </div>`).join('');
}

function renderEngagement(score) {
  const el = document.getElementById('engCircle');
  el.style.setProperty('--eng', score);
  document.getElementById('engNum').textContent = score;
}

function renderBadges(earned) {
  const ALL_BADGES = [
    { id: 'career_navigator', name: '🧭 Navigator', desc: 'Used Career Navigator' },
    { id: 'roi_calculator', name: '📈 ROI Pro', desc: 'Calculated Education ROI' },
    { id: 'admission_predictor', name: '🎯 Predictor', desc: 'Used Admission Predictor' },
    { id: 'loan_planner', name: '💰 Finance Wizard', desc: 'Planned Education Loan' },
    { id: 'timeline_generator', name: '📅 Planner', desc: 'Generated Timeline' },
    { id: 'sop_outline', name: '✍️ SOP Master', desc: 'Generated AI SOP Draft' },
    { id: 'chatbot', name: '🤖 AI User', desc: 'Chatted with EduMentor' },
    { id: 'application_strategy', name: '🎯 Strategist', desc: 'Built App Strategy' },
    { id: 'peer_benchmarks', name: '📊 Benchmarker', desc: 'Did Peer Benchmarking' },
    { id: 'all_rounder', name: '🌟 All-Rounder', desc: 'Used 5+ tools' },
    { id: 'level2', name: '⚡ Level 2 Scholar', desc: 'Reached 500 XP' },
    { id: 'university_comparison', name: '⚖️ Comparator', desc: 'Compared Universities' },
  ];
  const earnedIds = earned.map(b => b.id);
  document.getElementById('badgesGrid').innerHTML = ALL_BADGES.map(b => {
    const isEarned = earnedIds.includes(b.id);
    return `
      <div class="badge-tile ${isEarned ? 'earned' : ''}" title="${b.desc}">
        <span class="badge-emoji" style="filter:${isEarned ? 'none' : 'grayscale(1) opacity(.4)'}">${b.name.split(' ')[0]}</span>
        <div class="badge-name">${b.name.split(' ').slice(1).join(' ')}</div>
        <div class="badge-desc">${isEarned ? '✓ Earned' : 'Locked'}</div>
      </div>`;
  }).join('');
}

function renderRecommendations(recs) {
  const ICONS = {
    career_navigator: 'fas fa-compass', roi_calculator: 'fas fa-chart-line',
    admission_predictor: 'fas fa-brain', timeline_generator: 'fas fa-calendar-alt',
    loan_planner: 'fas fa-piggy-bank', chatbot: 'fas fa-robot',
    application_strategy: 'fas fa-chess', university_comparison: 'fas fa-balance-scale',
    peer_benchmarks: 'fas fa-users', analytics: 'fas fa-chart-pie',
  };
  document.getElementById('recsList').innerHTML = (recs || []).map(r => `
    <a class="rec-row" href="${r.url}">
      <div class="rec-icon"><i class="${ICONS[r.action] || 'fas fa-arrow-right'}"></i></div>
      <div class="rec-info">
        <h5>${r.url.replace('/', '').replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}</h5>
        <p>${r.reason}</p>
      </div>
      <div class="rec-xp">+${r.xp} XP</div>
    </a>`).join('') || '<p style="color:#64748b;">Great job! You\'ve completed all recommended tools.</p>';
}
