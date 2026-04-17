/**
 * Adaptive Learning Engine
 * Client-side logic for adaptive recommendations, session tracking,
 * and personalized content delivery.
 */

window.AdaptiveEngine = (() => {

  const SESSION_KEY = 'edu_bridge_session';

  function getLocalSession() {
    try {
      return JSON.parse(localStorage.getItem(SESSION_KEY) || '{}');
    } catch { return {}; }
  }

  function saveLocalSession(data) {
    try { localStorage.setItem(SESSION_KEY, JSON.stringify(data)); } catch {}
  }

  /**
   * Log a page visit for adaptive recommendations.
   */
  function trackPageVisit(page) {
    const s = getLocalSession();
    s.visits = s.visits || {};
    s.visits[page] = (s.visits[page] || 0) + 1;
    s.lastPage = page;
    s.lastVisit = new Date().toISOString();
    saveLocalSession(s);

    // Log to server
    fetch('/api/analytics/log-activity', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'page_visit', page })
    }).catch(() => {});
  }

  /**
   * Track a tool completion for adaptive next-action recommendations.
   */
  function trackToolCompletion(toolId, xpGained) {
    const s = getLocalSession();
    s.completed = s.completed || [];
    if (!s.completed.includes(toolId)) s.completed.push(toolId);
    s.totalXP = (s.totalXP || 0) + (xpGained || 0);
    saveLocalSession(s);

    fetch('/api/analytics/log-activity', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'tool_complete', page: toolId, xp: xpGained })
    }).catch(() => {});
  }

  /**
   * Determine the "next best action" based on local session.
   * Returns an action object {url, title, reason, icon}.
   */
  function getNextBestAction() {
    const s = getLocalSession();
    const completed = s.completed || [];
    const flow = [
      { id: 'career_navigator',    url: '/career-navigator',    title: 'AI Career Navigator',     icon: '🧭', reason: 'Start by discovering the best countries and universities for you' },
      { id: 'admission_predictor', url: '/admission-predictor', title: 'Admission Predictor',      icon: '🎯', reason: 'Check your admission probability at target universities' },
      { id: 'roi_calculator',      url: '/roi-calculator',      title: 'ROI Calculator',           icon: '📈', reason: 'Calculate the financial return on your education investment' },
      { id: 'application_strategy',url: '/application-strategy',title: 'Application Strategy',    icon: '♟️', reason: 'Build a complete, AI-powered application strategy' },
      { id: 'peer_benchmarks',     url: '/peer-benchmarks',     title: 'Peer Benchmarking',        icon: '📊', reason: 'See how your profile compares to 1,247 Indian students' },
      { id: 'loan_planner',        url: '/loan-planner',        title: 'Loan Planner',             icon: '💰', reason: 'Find the best loan offers personalized to your profile' },
      { id: 'timeline_generator',  url: '/timeline-generator',  title: 'Application Timeline',     icon: '📅', reason: 'Build a month-by-month action plan for your application' },
    ];
    const next = flow.find(f => !completed.includes(f.id));
    return next || { url: '/analytics', title: 'Analytics Dashboard', icon: '📊', reason: 'Review your complete progress' };
  }

  /**
   * Inject a "What to do next" floating chip if element exists.
   */
  function injectNextActionChip(parentSelector) {
    const parent = document.querySelector(parentSelector);
    if (!parent) return;
    const next = getNextBestAction();
    const chip = document.createElement('a');
    chip.href = next.url;
    chip.style.cssText = `
      display:inline-flex;align-items:center;gap:8px;
      background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;
      padding:10px 18px;border-radius:20px;text-decoration:none;
      font-size:.85rem;font-weight:600;box-shadow:0 4px 14px rgba(79,70,229,.35);
      margin-top:12px;transition:.2s;
    `;
    chip.innerHTML = `${next.icon} Next: ${next.title} <i class="fas fa-arrow-right" style="font-size:.75rem;"></i>`;
    chip.addEventListener('mouseover', () => chip.style.transform = 'translateY(-2px)');
    chip.addEventListener('mouseout', () => chip.style.transform = 'none');
    parent.appendChild(chip);
  }

  /**
   * Show an XP gain animation popup.
   * (Re-exported for pages that import this script)
   */
  function showXPPopup(xp) {
    const pop = document.createElement('div');
    pop.style.cssText = `
      position:fixed;bottom:32px;right:32px;
      background:linear-gradient(135deg,#4f46e5,#7c3aed);
      color:#fff;padding:14px 22px;border-radius:14px;
      font-size:1rem;font-weight:700;z-index:9999;
      box-shadow:0 8px 30px rgba(79,70,229,.5);
      animation:slideInRight .4s ease,fadeOutDown .4s 2.4s forwards;
    `;
    pop.innerHTML = `⚡ +${xp} XP Earned!`;
    document.body.appendChild(pop);
    setTimeout(() => pop.remove(), 3000);
  }

  // Auto-track current page
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => trackPageVisit(window.location.pathname));
  } else {
    trackPageVisit(window.location.pathname);
  }

  // Inject CSS animations
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideInRight { from { transform:translateX(100px);opacity:0; } to { transform:none;opacity:1; } }
    @keyframes fadeOutDown { from { opacity:1; } to { transform:translateY(20px);opacity:0; } }
  `;
  document.head.appendChild(style);

  return { trackPageVisit, trackToolCompletion, getNextBestAction, injectNextActionChip, showXPPopup };

})();
