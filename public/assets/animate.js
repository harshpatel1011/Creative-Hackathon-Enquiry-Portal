/* utils.js already has base helpers. This extends it with animation helpers.
   Include AFTER utils.js */

/* ─── Ripple Effect ───────────────────────────── */
function addRipple(btn) {
  btn.addEventListener('click', function(e) {
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const wave = document.createElement('span');
    wave.className = 'ripple-wave';
    wave.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX-rect.left-size/2}px;top:${e.clientY-rect.top-size/2}px`;
    btn.classList.add('ripple-btn');
    btn.appendChild(wave);
    wave.addEventListener('animationend', () => wave.remove());
  });
}
document.querySelectorAll('.btn').forEach(addRipple);
document.addEventListener('DOMNodeInserted', e => {
  if (e.target.classList && e.target.classList.contains('btn')) addRipple(e.target);
});

/* ─── Animated Number Counter ─────────────────── */
function animateCounter(el, target, duration = 1200) {
  if (!el) return;
  const start = 0;
  const startTime = performance.now();
  const isPercent = el.dataset.suffix === '%';
  function step(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 4); // ease-out quart
    const current = Math.floor(start + (target - start) * ease);
    el.textContent = current + (isPercent ? '%' : '');
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = target + (isPercent ? '%' : '');
  }
  requestAnimationFrame(step);
}

/* ─── Scroll Reveal ────────────────────────────── */
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.1 });
document.querySelectorAll('.reveal, .reveal-left, .reveal-right').forEach(el => revealObserver.observe(el));

/* ─── Progress Bar Animation ───────────────────── */
function animateProgressBars() {
  document.querySelectorAll('.progress-bar[data-value]').forEach(bar => {
    const val = bar.dataset.value;
    setTimeout(() => { bar.style.width = val + '%'; }, 300);
  });
}

/* ─── Scroll to Top ────────────────────────────── */
(function() {
  const btn = document.createElement('button');
  btn.className = 'scroll-top';
  btn.innerHTML = '↑';
  btn.title = 'Back to top';
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  document.body.appendChild(btn);
  const content = document.querySelector('.main-content') || window;
  (content === window ? window : content).addEventListener('scroll', () => {
    const scrollY = content === window ? window.scrollY : content.scrollTop;
    btn.classList.toggle('visible', scrollY > 300);
  });
})();

/* ─── Page Transition ──────────────────────────── */
(function() {
  const overlay = document.createElement('div');
  overlay.id = 'page-transition';
  overlay.innerHTML = '<div class="page-transition-logo">∞</div>';
  document.body.appendChild(overlay);

  // Intercept internal link clicks
  document.addEventListener('click', function(e) {
    const link = e.target.closest('a[href]');
    if (!link) return;
    const href = link.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('http') || href.startsWith('javascript')) return;
    if (link.target === '_blank') return;
    e.preventDefault();
    overlay.classList.add('entering');
    setTimeout(() => { window.location.href = href; }, 480);
  });

  // Reveal on page load
  window.addEventListener('load', () => {
    overlay.classList.add('leaving');
    setTimeout(() => { overlay.classList.remove('entering', 'leaving'); }, 600);
  });
})();

/* ─── FAB Menu Toggle ──────────────────────────── */
function initFAB(items) {
  const fab = document.createElement('button');
  fab.className = 'fab';
  fab.innerHTML = '+';
  fab.setAttribute('data-tip', 'Quick Actions');
  fab.title = 'Quick Actions';

  const menu = document.createElement('div');
  menu.className = 'fab-menu';
  items.forEach((item, i) => {
    const el = document.createElement('a');
    el.className = 'fab-item';
    el.href = item.href || '#';
    if (item.action) el.addEventListener('click', (e) => { e.preventDefault(); menu.classList.remove('open'); fab.style.transform = ''; item.action(); });
    el.innerHTML = `<span style="font-size:16px">${item.icon}</span>${item.label}`;
    el.style.animationDelay = `${i * 0.05}s`;
    menu.appendChild(el);
  });

  let open = false;
  fab.addEventListener('click', () => {
    open = !open;
    menu.classList.toggle('open', open);
    fab.style.transform = open ? 'rotate(45deg)' : '';
    fab.style.boxShadow = open ? '0 12px 32px rgba(108,43,217,0.6)' : '';
  });
  document.addEventListener('click', e => {
    if (!fab.contains(e.target) && !menu.contains(e.target)) {
      open = false; menu.classList.remove('open'); fab.style.transform = '';
    }
  });

  document.body.appendChild(menu);
  document.body.appendChild(fab);
}

/* ─── Notification System ──────────────────────── */
function initNotifications(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const wrap = document.createElement('div');
  wrap.style.position = 'relative';

  const btn = document.createElement('button');
  btn.className = 'notif-btn';
  btn.innerHTML = '🔔';

  const dot = document.createElement('span');
  dot.className = 'notif-dot';
  btn.appendChild(dot);

  const dropdown = document.createElement('div');
  dropdown.className = 'notif-dropdown';
  dropdown.innerHTML = `
    <div class="notif-header">Recent Activity</div>
    <div id="notif-items"><div style="padding:20px;text-align:center;color:var(--text-muted);font-size:13px">Loading…</div></div>
  `;

  btn.addEventListener('click', async e => {
    e.stopPropagation();
    dropdown.classList.toggle('open');
    if (dropdown.classList.contains('open')) loadNotifications();
  });
  document.addEventListener('click', () => dropdown.classList.remove('open'));

  wrap.appendChild(btn);
  wrap.appendChild(dropdown);
  container.insertBefore(wrap, container.firstChild);

  async function loadNotifications() {
    const res = await apiFetch('/api/analytics/recent-enquiries');
    if (!res || !res.ok) return;
    const items = await res.json();
    const el = document.getElementById('notif-items');
    if (!items.length) { el.innerHTML = '<div style="padding:16px;text-align:center;color:var(--text-muted);font-size:13px">No recent activity</div>'; return; }
    el.innerHTML = items.slice(0,5).map(e => `
      <div class="notif-item" onclick="location.href='enquiries.html'">
        <div class="title">📋 ${e.student_name} — ${e.stream}</div>
        <div class="time">${statusBadge(e.status)} &nbsp; ${fmtDate(e.created_at)}</div>
      </div>
    `).join('');
    dot.style.display = items.length ? '' : 'none';
  }
}

/* ─── Global Search ────────────────────────────── */
function initGlobalSearch(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const wrap = document.createElement('div');
  wrap.className = 'global-search';
  wrap.innerHTML = `
    <span class="search-icon">🔍</span>
    <input type="text" placeholder="Search students… (Ctrl+K)" id="global-search-input">
    <div class="global-search-results" id="global-search-results"></div>
  `;
  container.appendChild(wrap);

  const input = wrap.querySelector('input');
  const results = wrap.querySelector('#global-search-results');
  let timer;

  input.addEventListener('input', () => {
    clearTimeout(timer);
    const q = input.value.trim();
    if (!q) { results.classList.remove('open'); return; }
    timer = setTimeout(() => search(q), 280);
  });

  input.addEventListener('blur', () => setTimeout(() => results.classList.remove('open'), 200));

  // Ctrl+K shortcut
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); input.focus(); input.select(); }
  });

  async function search(q) {
    const res = await apiFetch(`/api/enquiries?search=${encodeURIComponent(q)}`);
    if (!res || !res.ok) return;
    const data = await res.json();
    if (!data.length) {
      results.innerHTML = '<div style="padding:16px;text-align:center;color:var(--text-muted);font-size:13px">No results found</div>';
    } else {
      results.innerHTML = data.slice(0,6).map(e => `
        <div class="search-result-item" onclick="location.href='enquiries.html'">
          <div class="sr-avatar">${e.student_name.charAt(0)}</div>
          <div><div class="sr-name">${e.student_name}</div><div class="sr-sub">${e.stream} · ${e.contact} · ${e.status}</div></div>
        </div>
      `).join('');
    }
    results.classList.add('open');
  }
}

/* ─── Slide Panel ──────────────────────────────── */
function openSlidePanel(content, title = 'Details') {
  let panel = document.getElementById('global-slide-panel');
  let overlay = document.getElementById('global-panel-overlay');
  if (!panel) {
    overlay = document.createElement('div');
    overlay.id = 'global-panel-overlay';
    overlay.className = 'slide-panel-overlay';
    overlay.addEventListener('click', closeSlidePanel);
    panel = document.createElement('div');
    panel.id = 'global-slide-panel';
    panel.className = 'slide-panel';
    panel.innerHTML = `
      <div class="slide-panel-header">
        <div id="panel-title" style="font-size:16px;font-weight:700"></div>
        <button class="modal-close" onclick="closeSlidePanel()">✕</button>
      </div>
      <div class="slide-panel-body" id="panel-body"></div>
    `;
    document.body.appendChild(overlay);
    document.body.appendChild(panel);
  }
  document.getElementById('panel-title').textContent = title;
  document.getElementById('panel-body').innerHTML = content;
  requestAnimationFrame(() => {
    overlay.classList.add('open');
    panel.classList.add('open');
  });
}
function closeSlidePanel() {
  const panel = document.getElementById('global-slide-panel');
  const overlay = document.getElementById('global-panel-overlay');
  if (panel) panel.classList.remove('open');
  if (overlay) overlay.classList.remove('open');
}
