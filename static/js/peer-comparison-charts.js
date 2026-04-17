/**
 * Peer Comparison Charts utility
 * Provides helper functions for rendering comparison visualizations
 * on the Peer Benchmarking page.
 */

window.PeerCharts = {

  /**
   * Renders a horizontal bar chart in the given container element.
   * bars: [{label, value, max, color}]
   */
  renderHorizontalBars(containerId, bars) {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = bars.map(b => {
      const pct = Math.min(100, (b.value / (b.max || 100)) * 100);
      return `
        <div style="margin-bottom:10px;">
          <div style="display:flex;justify-content:space-between;font-size:.82rem;color:#374151;margin-bottom:4px;">
            <span>${b.label}</span>
            <span style="font-weight:700;">${b.value}</span>
          </div>
          <div style="background:#f1f5f9;border-radius:10px;height:10px;overflow:hidden;">
            <div style="width:${pct}%;height:100%;border-radius:10px;background:${b.color || '#0891b2'};transition:width .6s ease;"></div>
          </div>
        </div>`;
    }).join('');
  },

  /**
   * Renders a gauge (semi-circle) for a percentile value.
   */
  renderGauge(containerId, percentile, label) {
    const el = document.getElementById(containerId);
    if (!el) return;
    const rotation = (percentile / 100) * 180 - 90; // -90 to +90 degrees
    const color = percentile >= 75 ? '#16a34a' : percentile >= 50 ? '#0891b2' : percentile >= 25 ? '#d97706' : '#dc2626';
    el.innerHTML = `
      <div style="position:relative;width:120px;height:70px;margin:0 auto;">
        <div style="position:absolute;bottom:0;width:100%;height:60px;border-radius:60px 60px 0 0;background:#f1f5f9;overflow:hidden;">
          <div style="position:absolute;bottom:0;width:100%;height:100%;
               background:conic-gradient(from -90deg, ${color} ${percentile * 1.8}deg, #f1f5f9 0);
               border-radius:60px 60px 0 0;"></div>
        </div>
        <div style="position:absolute;bottom:-8px;width:100%;text-align:center;font-size:1.1rem;font-weight:800;color:${color};">${percentile}%</div>
      </div>
      <div style="text-align:center;font-size:.78rem;color:#64748b;margin-top:14px;">${label}</div>`;
  },

  /**
   * Renders a radar/spider chart using SVG.
   * dimensions: [{label, value}] (0-100)
   */
  renderRadarChart(containerId, dimensions, color = '#0891b2') {
    const el = document.getElementById(containerId);
    if (!el || !dimensions || dimensions.length < 3) return;

    const W = 240, H = 240, CX = 120, CY = 120, R = 90;
    const N = dimensions.length;
    const angle = (i) => (i * 2 * Math.PI / N) - Math.PI / 2;

    // Grid circles
    let svgContent = '';
    [20, 40, 60, 80, 100].forEach(r => {
      const pts = dimensions.map((_, i) => {
        const a = angle(i), rad = (r / 100) * R;
        return `${CX + rad * Math.cos(a)},${CY + rad * Math.sin(a)}`;
      }).join(' ');
      svgContent += `<polygon points="${pts}" fill="none" stroke="#e2e8f0" stroke-width="1"/>`;
    });

    // Axes
    dimensions.forEach((_, i) => {
      const a = angle(i);
      svgContent += `<line x1="${CX}" y1="${CY}" x2="${CX + R * Math.cos(a)}" y2="${CY + R * Math.sin(a)}" stroke="#e2e8f0" stroke-width="1"/>`;
    });

    // Data polygon
    const dataPts = dimensions.map((d, i) => {
      const a = angle(i), r = (d.value / 100) * R;
      return `${CX + r * Math.cos(a)},${CY + r * Math.sin(a)}`;
    }).join(' ');
    svgContent += `<polygon points="${dataPts}" fill="${color}30" stroke="${color}" stroke-width="2"/>`;

    // Labels
    dimensions.forEach((d, i) => {
      const a = angle(i), lx = CX + (R + 18) * Math.cos(a), ly = CY + (R + 18) * Math.sin(a);
      svgContent += `<text x="${lx}" y="${ly}" text-anchor="middle" dominant-baseline="middle" font-size="9" fill="#374151" font-family="Inter,sans-serif">${d.label}</text>`;
    });

    el.innerHTML = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="display:block;margin:0 auto;">${svgContent}</svg>`;
  },

  /**
   * Renders an animated counter for a numeric value.
   */
  animateCounter(elementId, targetVal, duration = 1200, prefix = '', suffix = '') {
    const el = document.getElementById(elementId);
    if (!el) return;
    const start = Date.now();
    const startVal = 0;
    const step = () => {
      const elapsed = Date.now() - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // cubic ease-out
      el.textContent = prefix + Math.round(startVal + (targetVal - startVal) * eased) + suffix;
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }
};
