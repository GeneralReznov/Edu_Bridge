// ── Main JS: EduBridge ─────────────────────────────────────────────────────

// ── Navbar Scroll Effect ──────────────────────────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 20);
});

// ── Mobile Nav Toggle ─────────────────────────────────────────────────────
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');
if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });
  document.addEventListener('click', (e) => {
    if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
      navLinks.classList.remove('open');
    }
  });
}

// ── Intersection Observer: Animate on scroll ──────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.animationPlayState = 'running';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.animate-fade-up').forEach(el => {
  el.style.animationPlayState = 'paused';
  observer.observe(el);
});

// ── Toast Notifications ───────────────────────────────────────────────────
function showToast(message, type = 'success', duration = 4000) {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
  toast.innerHTML = `<i class="fas ${icon}"></i><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    toast.style.transition = '0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ── XP Award ─────────────────────────────────────────────────────────────
async function awardXP(action) {
  try {
    const res = await fetch('/api/profile/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    });
    const data = await res.json();
    if (data.success) {
      // Update XP pill in nav
      const navXpEl = document.getElementById('navXpVal');
      if (navXpEl) navXpEl.textContent = data.profile.xp;

      // Show XP popup
      showXPPopup('+' + data.xp_gained + ' XP');

      // If this page has hero XP display, update it
      const heroXp = document.getElementById('heroXpCurrent');
      const heroLevel = document.getElementById('heroLevel');
      const heroXpBar = document.getElementById('heroXpBar');
      const heroStreak = document.getElementById('heroStreak');
      if (heroXp) heroXp.textContent = data.profile.xp + ' XP';
      if (heroLevel) heroLevel.textContent = 'Level ' + data.profile.level;
      if (heroStreak) heroStreak.textContent = data.profile.streak + ' day streak';
      if (heroXpBar) {
        const pct = Math.min((data.profile.xp % 500) / 500 * 100, 100);
        heroXpBar.style.width = pct + '%';
      }
    }
  } catch (err) {
    console.error('XP award failed:', err);
  }
}

function showXPPopup(text) {
  const popup = document.getElementById('xpPopup');
  if (!popup) return;
  document.getElementById('xpPopupVal').textContent = text;
  popup.classList.add('show');
  setTimeout(() => popup.classList.remove('show'), 1800);
}

// ── Load and display nav XP on page load ─────────────────────────────────
(async function initProfile() {
  try {
    const res = await fetch('/api/profile/get');
    const data = await res.json();
    if (data.success) {
      const navXpEl = document.getElementById('navXpVal');
      if (navXpEl) navXpEl.textContent = data.profile.xp;
    }
  } catch (e) { /* silent fail */ }
})();
