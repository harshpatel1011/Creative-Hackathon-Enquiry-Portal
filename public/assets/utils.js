/* ========== SHARED ADMIN/COUNSELOR JS UTILITIES ========== */

const API = '';

function getToken() { return localStorage.getItem('ic_token'); }
function getUser() {
  try { return JSON.parse(localStorage.getItem('ic_user')); }
  catch { return null; }
}

function requireAuth(expectedRole = null) {
  const token = getToken();
  const user = getUser();
  if (!token || !user) {
    window.location.href = '/login.html';
    return null;
  }
  if (expectedRole && user.role !== expectedRole) {
    window.location.href = '/login.html';
    return null;
  }
  return user;
}

function logout() {
  localStorage.removeItem('ic_token');
  localStorage.removeItem('ic_user');
  window.location.href = '/login.html';
}

async function apiFetch(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(API + path, { ...options, headers });
  if (res.status === 401) { logout(); return null; }
  return res;
}

// Toast notifications
function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type]||'ℹ️'}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('removing');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Modal helpers
function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

// Status badge HTML
function statusBadge(status) {
  const cls = { 'New': 'new', 'Contacted': 'contacted', 'Interested': 'interested', 'Not Interested': 'not-interested', 'Converted': 'converted' };
  return `<span class="badge badge-${cls[status]||'new'}">${status}</span>`;
}

function demoBadge(status) {
  const cls = { 'Scheduled': 'scheduled', 'Completed': 'completed', 'Cancelled': 'cancelled' };
  return `<span class="badge badge-${cls[status]||'scheduled'}">${status}</span>`;
}

// Date formatting
function fmtDate(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

function fmtDateTime(d) {
  if (!d) return '—';
  return new Date(d).toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

// Update sidebar user info
function initSidebar(role) {
  const user = getUser();
  if (!user) return;
  const nameEl = document.getElementById('sidebar-user-name');
  const roleEl = document.getElementById('sidebar-user-role');
  const avatarEl = document.getElementById('sidebar-avatar');
  if (nameEl) nameEl.textContent = user.name;
  if (roleEl) roleEl.textContent = role === 'admin' ? 'Administrator' : 'Counselor';
  if (avatarEl) avatarEl.textContent = user.name.charAt(0).toUpperCase();

  // Update clock
  function tick() {
    const el = document.getElementById('clock');
    if (el) el.textContent = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
  }
  tick(); setInterval(tick, 1000);
  // Mobile sidebar
  const ham = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  if (ham) ham.onclick = () => { sidebar.classList.toggle('open'); overlay.classList.toggle('open'); };
  if (overlay) overlay.onclick = () => { sidebar.classList.remove('open'); overlay.classList.remove('open'); };
}

// Streams and statuses constants
const STREAMS = ['Data Science','Web Development','UI / UX Design','Python Full Stack','Java Full Stack','Digital Marketing','Video Editing'];
const STATUSES = ['New','Contacted','Interested','Not Interested','Converted'];
const SOURCES = ['Website','Walk-in','Referral','Social Media','Phone Call','Other'];

function streamOptions(selected='') {
  return STREAMS.map(s => `<option value="${s}" ${s===selected?'selected':''}>${s}</option>`).join('');
}
function statusOptions(selected='') {
  return STATUSES.map(s => `<option value="${s}" ${s===selected?'selected':''}>${s}</option>`).join('');
}
function sourceOptions(selected='') {
  return SOURCES.map(s => `<option value="${s}" ${s===selected?'selected':''}>${s}</option>`).join('');
}
